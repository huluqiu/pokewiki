from peewee import (
    Model, PostgresqlDatabase, PrimaryKeyField, ForeignKeyField,
    TextField, IntegerField, CharField, BooleanField, FloatField,
    SmallIntegerField,
)
from playhouse.postgres_ext import (
    PostgresqlExtDatabase, ArrayField, BinaryJSONField
)

database = PostgresqlDatabase('pokewiki', user='alezai')

class BaseModel(Model):
    class Meta:
        database = database

class Pokemon(BaseModel):
    num = SmallIntegerField(primary_key=True)
    name = CharField(max_length=10)
    name_jp = CharField(max_length=10)
    name_en = CharField(max_length=20)
    class = CharField(max_length=10)
    category = CharField(max_length=20)

    class Meta:
        db_table = 'pokemon'
