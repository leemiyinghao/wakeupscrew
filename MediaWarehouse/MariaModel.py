from peewee import *
import datetime
from MediaWarehouse import Media as OldMedia, Tag as OldTag, db as olddb
from tqdm import tqdm
from playhouse.migrate import *

db = MySQLDatabase('MediaWarehouse', user='mediawarehouse', password='howdoyouturnthison', charset='utf8mb4')

class LongBlogField(BlobField):
    field_type = 'LONGBLOB'

class Media(Model):
    id = UUIDField(primary_key=True)
    extension = CharField()
    mainDescription = CharField(default="")
    additionalData = TextField(default=None, null=True)
    created = DateTimeField(default=datetime.datetime.now)
    lastHit = DateTimeField(default=datetime.datetime.now)
    data = LongBlogField()
    thumbnail = LongBlogField()
    sourceType = CharField(default="TEMP")
    source = CharField(default="", max_length=2048)

    class Meta:
        database = db
        indexes = (('sourceType', False), ('mainDescription', False))


class Tag(Model):
    name = CharField(default="")
    media = ForeignKeyField(Media, backref='tags')

    class Meta:
        database = db
        primary_key = False

def datetimeWrapper(date):
    return datetime.datetime.fromtimestamp(date) if isinstance(date, float) else date

if __name__ == '__main__':
    #db.create_tables([Media, Tag])
    for media in tqdm(OldMedia.select(), total=OldMedia.select().count()):
        if Media.select().where(Media.id==media.id).exists():
            continue
        newmedia = Media.create(id=media.id,
        extension=media.extension,
        mainDescription=media.mainDescription,
        additionalData=media.additionalData,
        created=datetimeWrapper(media.created),
        lastHit=datetimeWrapper(media.lastHit),
        data=media.data,
        thumbnail=media.thumbnail,
        sourceType=media.sourceType,
        source=media.source)
        for tag in OldTag.select(OldTag.name).where(OldTag.media==media):
            Tag.create(name=tag.name, media=newmedia)