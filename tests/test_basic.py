from nexorm import IntegerField, Model, StringField, configure, transaction
from nexorm.migrations.operations import CreateTable


def create_table(model, db=None):
    db = db or model.objects.get_queryset().db
    dialect = db.dialect
    columns = [
        {
            "name": name,
            "sql": dialect.column_sql(field),
        }
        for name, field in model._meta.fields.items()
    ]
    for sql in CreateTable(model._meta.table_name, columns).to_sql(dialect):
        db.execute(sql)
    db.commit()


def test_model_create_and_query(tmp_path):
    configure(str(tmp_path / "test.sqlite3"))

    class User(Model):
        name = StringField(max_length=80)
        age = IntegerField(nullable=True)

    create_table(User)

    created = User.objects.create(name="Ada", age=36)
    found = User.objects.get(id=created.id)

    assert found.name == "Ada"
    assert found.age == 36
    assert User.objects.filter(name__contains="Ad").count() == 1


def test_named_database_connection(tmp_path):
    primary = configure(str(tmp_path / "primary.sqlite3"))
    analytics = configure(str(tmp_path / "analytics.sqlite3"), alias="analytics")

    class Account(Model):
        username = StringField(max_length=80, unique=True)

    create_table(Account, primary)
    create_table(Account, analytics)

    Account.objects.create(username="primary")
    Account.objects.using("analytics").create(username="report")

    assert Account.objects.filter(username="primary").count() == 1
    assert Account.objects.using("analytics").filter(username="primary").count() == 0
    assert Account.objects.using("analytics").filter(username="report").count() == 1

    with transaction.atomic("analytics"):
        Account.objects.using("analytics").create(username="worker")

    assert Account.objects.using("analytics").filter(username="worker").exists()
