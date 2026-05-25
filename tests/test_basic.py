from nexorm import IntegerField, Model, StringField, configure
from nexorm.migrations.operations import CreateTable


def create_table(model):
    db = model.objects.get_queryset().db
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
