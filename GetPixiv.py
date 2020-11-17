from MediaWarehouse import MediaWarehouse
import datetime
import json
import urllib
import random

EXPIRE_LIMIT = 30*6  # 6 month


async def getImage(sourceType="PIXIV", **args):
    media = MediaWarehouse.getMetadata(sourceType=sourceType, random=True, **args)
    allTags = MediaWarehouse.listTags(media['id'])
    mainTag = allTags[0] if len(allTags) > 0 else " "
    return MediaWarehouse.convertThumbnailURL(media['id']), "https://wakeupscrew.catlee.se/tag/{}/{}".format(urllib.parse.quote(mainTag), media['id']), media['source'], json.loads(media['additionalData'])['pixiv_v2']

async def getAllImage(num, **args):
    limit = datetime.datetime.now() - datetime.timedelta(days=EXPIRE_LIMIT)
    medias = MediaWarehouse.searchMetadata(limit = num, created=limit, random=True, **args)
    sets = []
    for media in medias:
        mainTag = MediaWarehouse.listTags(media['id'])[0]
        sets.append([MediaWarehouse.convertThumbnailURL(media['id']), "https://wakeupscrew.catlee.se/tag/{}/{}".format(urllib.parse.quote(mainTag), media['id']), media['source'], json.loads(media['additionalData'])['pixiv_v2']])
    return sets

async def getImageByTag(tags, tagOr=True, **args):
    media = MediaWarehouse.getMetadata(tags=tags, tagOr=tagOr, random=True, **args)
    matchTags = list(filter(lambda x: x in tags, MediaWarehouse.listTags(media['id'])))
    mainTag = (matchTags[0] if len(matchTags)>0 else MediaWarehouse.listTags(media['id'])[0]) if tagOr else " ".join(tags)
    return MediaWarehouse.convertThumbnailURL(media['id']), "https://wakeupscrew.catlee.se/tag/{}/{}".format(urllib.parse.quote(mainTag), media['id']), media['source'], json.loads(media['additionalData'])['pixiv_v2']


async def getImagesByTag(tags, tagOr=True, **args):
    medias = MediaWarehouse.searchMetadata(tags=tags, tagOr=tagOr, random=True, **args)
    sets = []
    for media in medias:
        matchTags = list(filter(lambda x: x in tags, MediaWarehouse.listTags(media['id'])))
        mainTag = (matchTags[0] if len(matchTags)>0 else MediaWarehouse.listTags(media['id'])[0]) if tagOr else " ".join(tags)
        sets.append([MediaWarehouse.convertThumbnailURL(media['id']), "https://wakeupscrew.catlee.se/tag/{}/{}".format(urllib.parse.quote(mainTag), media['id']), media['source'], json.loads(media['additionalData'])['pixiv_v2']])
    return sets


async def getMikuImage(num = 1):
    limit = datetime.datetime.now() - datetime.timedelta(days=EXPIRE_LIMIT)
    tags = ["初音ミク"]
    return await getImagesByTag(tags, created=limit, limit=num)


async def getMikuLegImage(num = 1):
    tags = ["足", "初音ミク"]
    return await getImagesByTag(tags, tagOr=False, limit=num)


async def getHifumiImage(num = 1):
    tags = ["滝本ひふみ"]
    return await getImagesByTag(tags, limit=num)


async def getGanbaruImage(num = 1):
    tags = ["今日も一日がんばるぞい!"]
    return await getImagesByTag(tags, limit=num)


async def getLoliImage(num = 1):
    tags = ["ロリ"]
    return await getImagesByTag(tags, limit=num)


async def getTomgirlImage(num = 1):
    tags = ["男の娘"]
    return await getImagesByTag(tags, limit=num)


async def getReDiveImage(num = 1):
    tags = ["プリンセスコネクト!Re:Dive"]
    return await getImagesByTag(tags, limit=num)


async def getCHCImage(num = 1):
    tags = ["GUMI",
            "ひだまりスケッチ",
            "きんいろモザイク",
            "NEWGAME!",
            "ご注文はうさぎですか?",
            "ゆるキャン△",
            "まちカドまぞく",
            "ブレンド・S",
            "ハナヤマタ",
            "GA芸術科アートデザインクラス",
            "けいおん!",
            "がっこうぐらし!",
            "Aチャンネル",
            "キルミーベイベー",
            "ゆゆ式"]
    #return getImageByTag([random.choice(tags)])
    return await getImagesByTag(tags, limit=num)


async def getExplosionImage(num = 1):
    tags = ["めぐみん", "このすば", "この素晴らしい世界に祝福を!"]
    return await getImagesByTag(tags, limit=num)


async def getYoshimaruImage(num = 1):
    tags = ["よしまる", "国木田花丸", "津島善子"]
    return await getImagesByTag(tags, limit=num)


async def getYuriImage(num = 1):
    tags = ["百合"]
    return await getImagesByTag(tags, limit=num)


async def getKGImage(num = 1):
    tags = ["アイカツ!", "アイカツ", "プリキュア", "プリパラ"]
    return await getImagesByTag(tags, limit=num)


async def getCatImage(num = 1):
    tags = ["猫"]
    return await getImagesByTag(tags, limit=num)


async def getWineImage(num = 1):
    tags = ["酒"]
    return await getImagesByTag(tags, limit=num)


async def getPaychanImage(num = 1):
    tags = ["変態王子と笑わない猫", "時雨", "ペンギン"]
    return await getImagesByTag(tags, limit=num)

async def getPaychanErkImage(num = 1):
    tags = ["足", "時雨"]
    return await getImagesByTag(tags, tagOr=False, limit=num)

async def getCatleeImage(num = 1):
    tags = ["艦これ", "艦隊これくしょん", "五月雨"]
    return await getImagesByTag(tags, tagOr=False, limit=num)


if __name__ == '__main__':
    print(getMikuImage())
