from peewee import *

db = SqliteDatabase("SenComPlete.sqlite")

class Sentence(Model):
    id = AutoField(index=True)
    text = CharField()
    class Meta:
        database = db
class SubSentence(Model):
    id = AutoField(index=True)
    sentence = ForeignKeyField(Sentence, backref='sub_sentences')
    text = CharField()
    location = IntegerField()
    class Meta:
        database = db
class Word(Model):
    id = AutoField(index=True)
    sub_sentence = ForeignKeyField(SubSentence, backref='words')
    text = CharField()
    location = IntegerField()
    length = IntegerField()
    class Meta:
        database = db

if __name__ == '__main__':
    db.create_tables([Sentence, SubSentence, Word])
