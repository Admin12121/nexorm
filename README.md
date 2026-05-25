<h3 align="center">NexORM</h3>

<p align="center">
  A minimal Python ORM for SQLite apps with models, query helpers, transactions, migrations, and named database connections.
</p>

<p align="center">
  <a href="https://pypi.org/project/nexorm/">
    <img alt="Release" src="https://img.shields.io/badge/release-v0.1.0-f2c6c2?style=for-the-badge&labelColor=2f2d42">
  </a>
  <a href="https://github.com/Admin12121/nexorm/stargazers">
    <img alt="Stars" src="https://img.shields.io/github/stars/Admin12121/nexorm?style=for-the-badge&labelColor=34364d&color=b8b8f3">
  </a>
  <a href="https://github.com/Admin12121/nexorm/issues">
    <img alt="Issues" src="https://img.shields.io/github/issues/Admin12121/nexorm?style=for-the-badge&labelColor=34364d&color=f4a77c">
  </a>
  <a href="https://github.com/Admin12121/nexorm/graphs/contributors">
    <img alt="Contributors" src="https://img.shields.io/github/contributors/Admin12121/nexorm?style=for-the-badge&labelColor=34364d&color=a7dc9a">
  </a>
</p>

## Installation

```bash
pip install nexorm
```

For local development:

```bash
python -m pip install -e ".[dev]"
```

## Quick Start

Initialize NexORM in your project:

```bash
nexorm init
```

This creates a local `manage.py` file and a `migrations/` directory:

```text
manage.py
migrations/
```

After that, you can use NexORM through `python manage.py`, similar to Django.

Define models in your app, for example `app/models.py`:

```python
from nexorm import ForeignKey, IntegerField, Model, StringField


class User(Model):
    id = IntegerField(primary_key=True, auto_increment=True)
    username = StringField(max_length=100, unique=True, index=True)

    class Meta:
        table_name = "users"


class Post(Model):
    id = IntegerField(primary_key=True, auto_increment=True)
    title = StringField(max_length=200)
    user_id = ForeignKey("User", on_delete="CASCADE", related_name="posts")

    class Meta:
        table_name = "posts"
```

Generate and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py rollback
python manage.py sqlmigrate 0001_create_table_users.py
```

By default, `manage.py` uses `db.sqlite3` and imports models from `app.models`.
You can override both:

```bash
python manage.py --database local.sqlite3 --models myproject.models makemigrations
python manage.py --database local.sqlite3 --models myproject.models migrate
```

Use the ORM:

```python
from nexorm import configure, transaction
from app.models import Post, User

configure("db.sqlite3")

user = User.objects.create(username="admin")
post = Post.objects.create(title="Hello", user_id=user.id)

same_user = User.objects.filter(username__contains="adm").first()
recent_posts = user.posts.order_by("-id").limit(10).all()

with transaction.atomic():
    User.objects.create(username="vicky")
```

Use raw SQL only with parameters:

```python
user = User.objects.raw("SELECT * FROM users WHERE id = ?", [1]).first()
```

Use with Flask:

```python
from flask import Flask
from nexorm import configure


def create_app():
    configure("db.sqlite3")
    app = Flask(__name__)
    return app
```

## Models

Define models by subclassing `Model` and assigning field instances. If a model does not define a primary key, NexORM adds an auto-incrementing `id` field.

```python
from nexorm import BooleanField, DateTimeField, IntegerField, Model, StringField


class Article(Model):
    title = StringField(max_length=180)
    views = IntegerField(default=0)
    published = BooleanField(default=False)
    created_at = DateTimeField(nullable=True)
```

## Queries

```python
Post.objects.create(title="First post", user_id=1)

posts = Post.objects.filter(title__contains="First").order_by("-id").limit(10).all()
count = Post.objects.filter(user_id=1).count()
exists = Post.objects.filter(title="First post").exists()
```

Supported lookup suffixes include exact matching and common comparisons such as `gt`, `gte`, `lt`, `lte`, `contains`, `startswith`, `endswith`, and `in`.

## Multiple Databases

Configure the default connection:

```python
from nexorm import configure

configure("db.sqlite3")
```

Configure named connections:

```python
from nexorm import configure, transaction
from app.models import User

configure("db.sqlite3")
configure("analytics.sqlite3", alias="analytics")

admin = User.objects.create(username="admin")
report_user = User.objects.using("analytics").create(username="report")

analytics_users = User.objects.using("analytics").filter(username__contains="rep").all()

with transaction.atomic("analytics"):
    User.objects.using("analytics").create(username="worker")
```

You can also pass a `Database` instance directly to `using(...)` or `transaction.atomic(...)`.

## Transactions

```python
from nexorm import transaction


with transaction.atomic():
    Post.objects.create(title="Inside a transaction", user_id=1)
```

Nested transactions use SQLite savepoints.

## Migrations CLI

Initialize a project:

```bash
nexorm init
```

That command creates this local `manage.py` file:

```python
from nexorm.cli import main


if __name__ == "__main__":
    main()
```

Generate and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

Other commands:

```bash
python manage.py rollback
python manage.py sqlmigrate 0001_initial.py
python manage.py dbshell
```

You can still use the installed `nexorm` command directly:

```bash
nexorm --database app.sqlite3 --models app.models makemigrations
nexorm --database app.sqlite3 --models app.models migrate
```

## Build

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```

## Publish to PyPI

Create an API token in PyPI, then upload manually:

```bash
python -m twine upload dist/*
```

When prompted:

```text
username: __token__
password: pypi-...
```

Use TestPyPI first if you want a dry run:

```bash
python -m twine upload --repository testpypi dist/*
```

## Status

NexORM is an early package. The current implementation focuses on SQLite and keeps the public API small: model fields, managers/querysets, raw queries, transactions, named connections, and file-based migrations.
