from peewee import *

db = SqliteDatabase("beer.sqlite")

class Beer(Model):
    originUrl = CharField()
    title = CharField()
    imagePath = CharField()
    aspect_ratio = CharField()
    style = CharField()
    brewer = CharField()
    rate = DoubleField()
    abv = CharField()
    ibu = CharField()
    cal = CharField()
    describe = TextField()
    class Meta:
        database = db

if __name__ == '__main__':
    db.create_tables([Beer])
