import datetime
from uuid import uuid1, uuid4
from peewee import *
import peewee_async
#import datetime
import os
import logging
from playhouse.migrate import *
from playhouse.shortcuts import model_to_dict
from playhouse.mysql_ext import MySQLConnectorDatabase
from peewee import NodeList
from urllib.parse import quote_plus
from PIL import Image
from math import floor
import io
from functools import reduce
import random as Random

from wand.image import Image as WandImage
from wand.api import library
from ctypes import c_void_p, c_size_t
library.MagickSetCompressionQuality.argtypes = [c_void_p, c_size_t]


def HEICEncode(otherBlob):
    other = WandImage(blob=otherBlob)
    other.format = 'heic'
    return other.make_blob()


def HEICDecode(heicBlob, _format='jpg'):
    heic = WandImage(blob=heicBlob)
    heic.format = _format
    if _format in ['jpg', 'jpeg']:
        library.MagickSetCompressionQuality(heic.wand, 100)
    return heic.make_blob()


#db = MySQLDatabase('MediaWarehouse', user='mediawarehouse', password='howdoyouturnthison', **{'charset': 'utf8', 'use_unicode': True})
db = peewee_async.MySQLDatabase('MediaWarehouse', user='mediawarehouse', password='howdoyouturnthison', **{'charset': 'utf8', 'use_unicode': True})


class LongBlogField(BlobField):
    field_type = 'LONGBLOB'


class Media(Model):
    id = UUIDField(primary_key=True)
    extension = CharField()
    mainDescription = CharField(default="")
    additionalData = TextField(default=None, null=True)
    created = DateTimeField(default=datetime.datetime.now)
    lastHit = DateTimeField(default=datetime.datetime.now)
    _data = LongBlogField(column_name='data', null=True)

    @property
    def data(self):
        return self._data if len(self.datas) == 0 else HEICDecode(self.datas[0].data, self.extension)

    @data.setter
    def data(self, blob):
        self._data = blob
        #OriginalImage.create(media_id=self.id, data=HEICEncode(blob))

    thumbnail = LongBlogField()
    thumbnail2x = LongBlogField(null=True)
    sourceType = CharField(default="TEMP")
    source = CharField(default="", max_length=2048)
    disabled = BooleanField(default=False)

    @property
    def thumbnailRetina(self):
        if self.thumbnail2x is not None:
            return self.thumbnail2x
        else:
            return self.thumbnail

    @thumbnailRetina.setter
    def thumbnailRetina(self, setObj):
        self.thumbnail2x = setObj

    class Meta:
        database = db
        indexes = (('sourceType', False), ('mainDescription', False))


class Description(Model):
    id = UUIDField(primary_key=True)
    text = TextField(default=None, null=True)

    class Meta:
        database = db


class Tag(Model):
    name = CharField(default="")
    media = ForeignKeyField(Media, backref='tags')

    class Meta:
        database = db
        primary_key = False


class Tagv2(Model):
    id = PrimaryKeyField()
    name = CharField()

    class Meta:
        database = db
        indexes = (('name'), False)


class MediaToTag(Model):
    id = PrimaryKeyField()
    tag = ForeignKeyField(Tagv2, backref='mediaToTags')
    media = ForeignKeyField(Media, backref='mediaToTags')

    class Meta:
        database = db


class OriginalImage(Model):
    media = ForeignKeyField(Media, primary_key=True, backref='datas', null=True)
    format = CharField(default='heic')
    serial = IntegerField(default=0)
    data = LongBlogField()

    class Meta:
        database = db


class MediaWarehouse:
    @staticmethod
    def create(extension,
               mainDescription,
               data,
               thumbnail,
               sourceType,
               created=datetime.datetime.now(),
               additionalData='',
               source='',
               tags=None,
               thumbnailRetina=None,
               heic=False,
               index=None
               ):
        if thumbnailRetina == None:
            imgBuffer = io.BytesIO(data)
            imgObj = Image.open(imgBuffer)
            imgObj = imgObj.convert('RGB')
            width, height = imgObj.size
            if width > 800:
                twidth = min([width, 1600])
                theight = floor((twidth/width)*height + 0.5)
                imgObj.thumbnail((twidth, theight), resample=Image.ANTIALIAS)
                thumb = io.BytesIO()
                imgObj.save(thumb, format="jpeg", quality=95, optimize=True)
                thumbnailRetina = thumb.getvalue()
            else:
                thumbnailRetina = None
        with db.atomic():
            mediaId = uuid1()
            media = Media.create(
                id=mediaId,
                extension=extension,
                mainDescription=mainDescription,
                sourceType=sourceType,
                created=created,
                additionalData=additionalData,
                source=source,
                lastHit=datetime.datetime.now(),
                data=data if not heic else None,
                thumbnail=thumbnail,
                thumbnailRetina=thumbnailRetina)
            if sourceType == "PIXIV":
                Description.create(id=mediaId, text=index)
        if heic:
            # transition period code
            OriginalImage.create(media=media, data=HEICEncode(data))

        if tags is not None:
            for name in tags:
                tag, _ = Tagv2.get_or_create(name=name)
                MediaToTag.get_or_create(tag=tag, media=media)
        return model_to_dict(media)

    @staticmethod
    def search(id=None,
               extension=None,
               mainDescription=None,
               sourceType=None,
               created=None,
               lastHit=None,
               source=None,
               tags=None,
               tagOr=False,  # default link tags AND
               random=False,
               limit=1,
               updateHit=False):
        query = Media.select(Media.id).where(Media.disabled == False)
        if id is not None:
            query = query.where(Media.id == id)
        if lastHit is not None:
            query = query.where(Media.lastHit > lastHit)
        if created is not None:
            query = query.where(Media.created > created)
        if mainDescription is not None:
            query = query.where(Media.mainDescription == mainDescription)
        if sourceType is not None:
            query = query.where(Media.sourceType == sourceType)
        if source is not None:
            query = query.where(Media.source == source)
        if extension is not None:
            query = query.where(Media.extension == extension)
        if not query.exists():
            return None
        if updateHit:
            media_ids = [media.id for media in query.limit(limit)]
            Media.update({Media.lastHit: datetime.datetime.now()}).where(Media.id << media_ids).execute()
        # return list(query.limit(limit).dicts())
        queryBackup = query
        if tags is not None:
            idListPerTag = []
            for tag in tags:
                _tags = Tagv2.select().where(Tagv2.name == tag)
                idListPerTag.append(Media.id << MediaToTag.select(MediaToTag.media_id).where(MediaToTag.tag << _tags))
            if tagOr:
                idExpression = reduce(lambda x, y: x | y, idListPerTag)
            else:
                idExpression = reduce(lambda x, y: x & y, idListPerTag)
            query = query.where(idExpression)
        if not query.exists():
            query = queryBackup
            if tags is not None:
                idListPerTag = []
                for tag in tags:
                    _tags = Tagv2.select().where(Tagv2.name.contains(tag))
                    idListPerTag.append(Media.id << MediaToTag.select(MediaToTag.media_id).where(MediaToTag.tag << _tags))
                if tagOr:
                    idExpression = reduce(lambda x, y: x | y, idListPerTag)
                else:
                    idExpression = reduce(lambda x, y: x & y, idListPerTag)
                query = query.where(idExpression)
        if random:
            _uuid = uuid1()
            queryBackup = query
            query = query.order_by(Media.id).where(Media.id > _uuid)
            if not query.exists():
                query = queryBackup.order_by(Media.id.desc()).where(Media.id < _uuid)
        return list(Media.select().where(Media.id << [media.id for media in query.limit(limit)]).limit(limit).dicts())

    @staticmethod
    def get(**args):
        results = MediaWarehouse.search(**args)
        return results[0] if results is not None else None

    @staticmethod
    def searchMetadata(id=None,
                       extension=None,
                       mainDescription=None,
                       sourceType=None,
                       created=None,
                       lastHit=None,
                       source=None,
                       tags=None,
                       tagOr=False,  # default link tags AND
                       random=False,
                       limit=1,
                       updateHit=False):
        query = Media.select(Media.id, Media.extension, Media.mainDescription, Media.additionalData, Media.created, Media.lastHit, Media.sourceType, Media.source).where(Media.disabled == False)
        if id is not None:
            query = query.where(Media.id == id)
        if lastHit is not None:
            query = query.where(Media.lastHit > lastHit)
        if created is not None:
            query = query.where(Media.created > created)
        if mainDescription is not None:
            query = query.where(Media.mainDescription == mainDescription)
        if sourceType is not None:
            query = query.where(Media.sourceType == sourceType)
        if source is not None:
            query = query.where(Media.source == source)
        if extension is not None:
            query = query.where(Media.extension == extension)
        if not query.exists():
            return None
        if updateHit:
            media_ids = [media.id for media in query.limit(limit)]
            Media.update({Media.lastHit: datetime.datetime.now()}).where(Media.id << media_ids).execute()
        # return list(query.limit(limit).dicts())
        queryBackup = query
        if tags is not None:
            idListPerTag = []
            if tagOr:
                query = query.join(Description, on=(Description.id == Media.id)).where(NodeList((fn.Match(Description.text), fn.Against(NodeList((" ".join(tags), SQL("IN BOOLEAN MODE")))))))
            else:
                query = query.join(Description, on=(Description.id == Media.id)).where(NodeList((fn.Match(Description.text), fn.Against(NodeList((" ".join(["+" + tag for tag in tags]), SQL("IN BOOLEAN MODE")))))))
        if query.limit(limit).count() < limit:
            query = queryBackup
            query = query.join(Description, on=(Description.id == Media.id)).where(NodeList((fn.Match(Description.text), fn.Against(NodeList((" ".join(tags), SQL("IN NATURAL LANGUAGE MODE")))))))
        if random:
            _uuid = uuid4()
            queryBackup = query
            query = query.order_by(Media.id).where(Media.id > _uuid)
            if query.limit(limit).count() < limit:
                query = queryBackup.order_by(Media.id.desc()).where(Media.id < _uuid)
        return list(query.limit(limit).dicts())

    @staticmethod
    def getMetadata(**args):
        results = MediaWarehouse.searchMetadata(**args)
        return results[0] if results is not None else None

    @staticmethod
    def convertURL(id):
        media = Media.select(Media.mainDescription, Media.extension, Media.id).where(Media.id == id).limit(1)[0]
        #return "https://wakeupscrew.catlee.se/media/{}/{}.{}".format(media.id, quote_plus(media.mainDescription), media.extension)
        return "https://wakeupscrew.catlee.se/media/{}/{}.{}".format(media.id, media.id, media.extension)

    @staticmethod
    def convertThumbnailURL(id):
        media = Media.select(Media.mainDescription, Media.extension, Media.id).where(Media.id == id).limit(1)[0]
        return "https://wakeupscrew.catlee.se/media/thumbnail/{}/{}.jpg".format(media.id, media.id)

    @staticmethod
    def convertThumbnailRetinaURL(id):
        media = Media.select(Media.mainDescription, Media.extension, Media.id).where(Media.id == id).limit(1)[0]
        return "https://wakeupscrew.catlee.se/media/thumbnailretina/{}/{}.jpg".format(media.id, media.id)

    @staticmethod
    def popularTags(count=10, skip=0):
        mediaToTags = MediaToTag.select(MediaToTag.tag, fn.COUNT(MediaToTag.id)).group_by(MediaToTag.tag).order_by(fn.COUNT(MediaToTag.id).desc()).paginate(floor(skip/count)+1, count + floor(skip % count))[floor(skip % count):]
        tagsWithCounts = sorted([[tag.name, tag.mediaToTags.count()] for tag in Tagv2.select().where(Tagv2.id << [mediaToTag.tag for mediaToTag in mediaToTags])], key=lambda x: x[1], reverse=True)
        tags = [tagsWithCount[0] for tagsWithCount in tagsWithCounts]
        tagToCount = {tagsWithCount[0]: tagsWithCount[1] for tagsWithCount in tagsWithCounts}
        return tags, tagToCount

    @staticmethod
    def listTags(id):
        return [totag.tag.name for totag in MediaToTag.select(MediaToTag.tag).where(MediaToTag.media_id == id)]

    @staticmethod
    def findTags(keyword, limit=20):
        return [tag.name for tag in Tagv2.select(Tagv2.name).where(Tagv2.name.contains(keyword)).limit(limit)]
    @staticmethod
    def randomTag():
        key = Random.randint(0, Tagv2.select(Tagv2.name).count())
        return Tagv2.select(Tagv2.name).where(Tagv2.id >= key).get().name
