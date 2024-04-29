from peewee import SqliteDatabase, Model, CharField, TextField, DateField, ForeignKeyField

db = SqliteDatabase("todolist")

class User(Model):
    username = CharField(unique=True)
    passwd = CharField()
    
    class Meta:
        database = db

class Todolist(Model):
    title = CharField()
    description = TextField(null=True)
    due_date = DateField(null=True)
    status = CharField(choices=['Todo', 'InProgress', 'Done'], default='Todo')
    user = ForeignKeyField(User, backref='todolists')

    class Meta:
        database = db

""" db.connect()
db.create_tables([User, Todolist]) """
