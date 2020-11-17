import os
from tqdm import tqdm
from MediaWarehouse import MediaWarehouse, Media, Tag, db, LongBlogField, Tagv2, MediaToTag, OriginalImage, Description
from playhouse.migrate import *
from functools import reduce
import json
import datetime
if __name__ == "__main__":
    #print(MediaWarehouse.search(mainDescription="68352062"))
    #db.create_tables([Thumbnail])
    #migrator = MySQLMigrator(db)
    #db.create_tables([OriginalImage])
    '''migrate(
        migrator.add_index('tagv2', ['name'], False)
    )'''
    '''migrate(
        #migrator.alter_add_column('media', 'data', LongBlogField(column_name='data', null=True))
        migrator.drop_not_null('media', 'data')
    )'''
    #migrator = MySQLMigrator(db)
    """migrate(
        migrator.drop_column('media', 'data'),
        migrator.drop_column('media', 'thumbnail')
    )"""
    """migrate(
        migrator.add_column('media', 'thumbnail2x', LongBlogField(null=True))
    )"""
    '''migrate(
        migrator.add_column('media', 'disabled', BooleanField(default=False))
    )'''
    #print(MediaWarehouse.listTags(MediaWarehouse.get(tags=['初音ミク', 'Fate/GrandOrder'], random=True, tagOr=True)['id']))
    '''tags = ['下着', 'Fate/GrandOrder']
    idListPerTag = []
    for tag in tags:
        _tags = Tagv2.select().where(Tagv2.name.contains(tag))
        idListPerTag.append(Media.id << MediaToTag.select(MediaToTag.media_id).where(MediaToTag.tag << _tags))
    print(idListPerTag)
    idExpression = reduce(lambda x,y:x | y, idListPerTag)
    print(Media.select().where(idExpression).sql())'''
    #db.create_tables([Description])
    '''for media in tqdm(Media.select(Media.id, Media.additionalData).where(Media.sourceType == "PIXIV").iterator(), total=Media.select(Media.id).where(Media.sourceType == "PIXIV").count()):
        if media.additionalData: #and not Description.select().where(Description.id == media.id).exists():
            try:
                additionalData = json.loads(media.additionalData)["pixiv_v2"]
                text = "{} {} {} {}".format(additionalData["title"], additionalData["caption"], " ".join(additionalData["tags"]), additionalData["user"]["name"])
                #Description.get_or_create(id = media.id, text = text)
                Description.update({Description.text: text}).where(Description.id == media.id)
            except Exception as e:
                print(e)'''
    #print(MediaWarehouse.popularTags())
    now = datetime.datetime.now()
    result = MediaWarehouse.searchMetadata(tags=["初音ミク", "裸足"], random=True)
    print(result)
    print(result[0]['id'])
    print(Description.select().where(Description.id == result[0]['id']).get().text)
    print(datetime.datetime.now() - now)