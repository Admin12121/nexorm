<h3 align="center">NexORM</h3>

<p align="center">
  A minimal Python ORM for SQLite apps with models, query helpers, transactions, and migrations.
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

```python
from nexorm import IntegerField, Model, StringField, configure
from nexorm.migrations.operations import CreateTable


db = configure("app.sqlite3")


class User(Model):
    name = StringField(max_length=120)
    age = IntegerField(nullable=True)

    class Meta:
        table_name = "users"


# Create the table with the migration SQL helper.
for sql in CreateTable(
    User._meta.table_name,
    [{"name": name, "sql": db.dialect.column_sql(field)} for name, field in User._meta.fields.items()],
).to_sql():
    User.objects.get_queryset().db.execute(sql)

user = User.objects.create(name="Ada", age=36)
found = User.objects.get(id=user.id)
print(found.to_dict())
```

## Models

Define models by subclassing `Model` and assigning field instances:

```python
from nexorm import BooleanField, DateTimeField, IntegerField, Model, StringField


class Article(Model):
    title = StringField(max_length=180)
    views = IntegerField(default=0)
    published = BooleanField(default=False)
    created_at = DateTimeField(nullable=True)
```

If a model does not define a primary key, NexORM adds an auto-incrementing `id` field.

## Queries

```python
Article.objects.create(title="First post")

posts = Article.objects.filter(published=False).order_by("-id").limit(10).all()
count = Article.objects.filter(published=False).count()
exists = Article.objects.filter(title="First post").exists()
```

Supported lookup suffixes include exact matching and common comparisons such as `gt`, `gte`, `lt`, `lte`, `contains`, `startswith`, `endswith`, and `in`.

## Transactions

```python
from nexorm import transaction


with transaction():
    Article.objects.create(title="Inside a transaction")
```

Nested transactions use SQLite savepoints.

## Migrations CLI

Initialize a project:

```bash
nexorm init
```

Generate and apply migrations:

```bash
nexorm --database app.sqlite3 --models app.models makemigrations
nexorm --database app.sqlite3 --models app.models migrate
nexorm --database app.sqlite3 --models app.models showmigrations
```

Other commands:

```bash
nexorm --database app.sqlite3 rollback
nexorm --database app.sqlite3 sqlmigrate 0001_initial.py
nexorm --database app.sqlite3 dbshell
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

NexORM is an early package. The current implementation focuses on SQLite and keeps the public API small: model fields, managers/querysets, raw queries, transactions, and file-based migrations.
