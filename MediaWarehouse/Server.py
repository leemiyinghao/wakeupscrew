#from flask import Flask, send_file, abort, redirect, render_template, Response
from quart import Quart, send_file, abort, redirect, render_template, Response
from MediaWarehouse import Media, MediaWarehouse, db
import datetime
import io, logging
import json
import re
import logging
import urllib
from markupsafe import Markup
from uuid import UUID

downloader = Quart(__name__)

@downloader.template_filter('urlencode')
def urlencode_filter(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = urllib.parse.quote(s)
    return Markup(s)

@downloader.before_request
async def _db_connect():
    db.connect()

@downloader.teardown_request
async def _db_close(exc):
    if not db.is_closed():
        db.close()

@downloader.route('/favicon.ico')
async def favicon():
    abort(404)

@downloader.route('/media/<id>/<path:filename>', strict_slashes=False)
@downloader.route('/media/<id>', strict_slashes=False)
async def download(id, filename='image'):
    try:
        id = str(UUID(id))
        media = Media.get(id=id)
        return await send_file(io.BytesIO(media.data), attachment_filename="{}.{}".format(filename, media.extension))
    except Exception as e:
        logging.exception(e)
        abort(404)
@downloader.route('/media/thumbnail/<id>/<path:filename>', strict_slashes=False)
@downloader.route('/media/thumbnail/<id>', strict_slashes=False)
async def downloadthumbnail(id, filename='image'):
    try:
        id = str(UUID(id))
        media = Media.get(id=id)
        return await send_file(io.BytesIO(media.thumbnail), attachment_filename="{}.jpg".format(filename))
    except Exception as e:
        logging.exception(e)
        abort(404)
@downloader.route('/media/thumbnailretina/<id>/<path:filename>', strict_slashes=False)
@downloader.route('/media/thumbnailretina/<id>', strict_slashes=False)
async def downloadthumbnailRetina(id, filename='image'):
    try:
        id = str(UUID(id))
        media = Media.get(id=id)
        return await send_file(io.BytesIO(media.thumbnailRetina), attachment_filename="{}.jpg".format(filename))
    except Exception as e:
        logging.exception(e)
        abort(404)
@downloader.route('/media')
@downloader.route('/media/')
async def random():
    url = MediaWarehouse.convertURL(MediaWarehouse.get(random=True, lastHit=datetime.datetime.now() - datetime.timedelta(days=30*6))['id'])
    return redirect(url, code=302)
@downloader.route('/<sourceType>')
@downloader.route('/<sourceType>/')
@downloader.route('/<sourceType>/<id>')
async def randomWithType(sourceType, id=None):
    try:
        convs = {
            "MIKU": {"tags": ["初音ミク"], "tagOr": True},
            "ERK": {"tags": ["裸足裏", "初音ミク"], "tagOr": False},
            "YUGIOH_WAKE": {"tags": ["滝本ひふみ"], "tagOr": True},
            "GANBARU": {"tags": ["今日も一日がんばるぞい!"], "tagOr": True},
            "LOLI": {"tags": ["ロリ"], "tagOr": True},
            "TOMGIRL": {"tags": ["男の娘"], "tagOr": True},
            "REDIVE": {"tags": ["プリンセスコネクト!Re:Dive"], "tagOr": True},
            "CHC": {"tags": ["GUMI",
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
            "ゆゆ式"], "tagOr": True},
            "MEGUMIN": {"tags": ["めぐみん", "このすば", "この素晴らしい世界に祝福を!"], "tagOr": True},
            "YOSHIMARU": {"tags": ["よしまる", "国木田花丸", "津島善子"], "tagOr": True},
            "KG": {"tags": ["アイカツ!", "アイカツ", "プリキュア", "プリパラ"], "tagOr": True},
            "YURI": {"tags": ["百合"], "tagOr": True},
            "RAIL": {"tags": ["電車", "鉄道"], "tagOr": True},
        }
        if id is None:
            conv = convs[sourceType]
            media = MediaWarehouse.getMetadata(random=True, tags=conv["tags"], tagOr=conv["tagOr"])
            return redirect("https://wakeupscrew.catlee.se/{}/{}".format(sourceType, media['id']), code=302)
        else:
            id = str(UUID(id))
            media = MediaWarehouse.getMetadata(id=id)
        url = MediaWarehouse.convertURL(media['id'])
        thumb = MediaWarehouse.convertThumbnailURL(media['id'])
        thumbRetina = MediaWarehouse.convertThumbnailRetinaURL(media['id'])
        sourceTypes = list(reversed([
            ["MIKU", "螺絲醒醒"],
            ["ERK", "螺絲矮額"],
            ["GANBARU", "ZOI"],
            ["YUGIOH_WAKE", "遊戲亡起床尿尿"],
            ["LOLI", "鱻鱻醒醒"],
            ["CHC", "CHC醒醒"],
            ["REDIVE", "市場醒醒"],
            ["MEGUMIN", "EXPLOSION"],
            ["YOSHIMARU", "阿部醒醒"],
            ["KG", "KG醒醒"],
            ["YURI", "真香"],
            ["RAIL", "車車"],
        ]))
        sourceTypeConv = { t[0]: t[1] for t in sourceTypes}
        if sourceType in [t[0] for t in sourceTypes]:
            pixiv = json.loads(media['additionalData'])['pixiv_v2']
            now = datetime.datetime.now().timestamp()
            return await render_template("pixiv.html", pixiv=pixiv, url=url, thumb=thumb, thumbRetina=thumbRetina, source=media['source'], sourceType=sourceType, now=now, sourceTypes=sourceTypes, sourceTypeConv=sourceTypeConv)
        else:
            return redirect(url, code=302)
    except Exception as e:
        logging.exception(e)
        abort(404)
@downloader.route('/tag')
@downloader.route('/tag/')
async def index():
    randomTag = MediaWarehouse.randomTag()
    return await render_template("pixiv_search.html", randomTag=randomTag)
@downloader.route('/tag/<path:tags>')
@downloader.route('/tag/<path:tags>/')
async def randomWithTag(tags):
    media = MediaWarehouse.getMetadata(random=True, tags=tags.split(' ')if len(tags)>0 else None)
    return redirect("https://wakeupscrew.catlee.se/tag/{}/{}".format(urllib.parse.quote(tags), media['id']), code=302)
@downloader.route('/tag/<path:tags>/<id>')
async def withTag(tags, id):
    id = str(UUID(id))
    #media = MediaWarehouse.getMetadata(id=id)
    media = Media.select(Media.id, Media.extension, Media.mainDescription, Media.additionalData, Media.created, Media.lastHit, Media.sourceType, Media.source).where(Media.id==id).get()
    '''url = MediaWarehouse.convertURL(media['id'])
    thumb = MediaWarehouse.convertThumbnailURL(media['id'])
    thumbRetina = MediaWarehouse.convertThumbnailRetinaURL(media['id'])
    pixiv = json.loads(media['additionalData'])['pixiv_v2']
    now = datetime.datetime.now().timestamp()
    popularTags, tagToCount = MediaWarehouse.popularTags(20)'''
    url = MediaWarehouse.convertURL(media.id)
    thumb = MediaWarehouse.convertThumbnailURL(media.id)
    thumbRetina = MediaWarehouse.convertThumbnailRetinaURL(media.id)
    pixiv = json.loads(media.additionalData)['pixiv_v2']
    now = datetime.datetime.now().timestamp()
    popularTags, tagToCount = MediaWarehouse.popularTags(20)
    return await render_template("pixiv_bytag.html",
    pixiv=pixiv,
    url=url,
    thumb=thumb,
    thumbRetina=thumbRetina,
    source=media.source,
    now=now,
    tags=tags.split(" ") if len(tags) > 0 else [""],
    popularTags=popularTags,
    tagToCount=tagToCount)
@downloader.route('/tags')
@downloader.route('/tags/')
@downloader.route('/tags/<int:skip>/<int:num>')
@downloader.route('/tags/<int:skip>/<int:num>/')
async def listTags(skip=0, num=50):
    popularTags, _ = MediaWarehouse.popularTags(num, skip=skip)
    return Response(json.dumps(popularTags, ensure_ascii=False), mimetype='application/json')
@downloader.route('/tags/<string:keyword>')
@downloader.route('/tags/<string:keyword>/')
async def findTags(keyword):
    tags = MediaWarehouse.findTags(keyword)
    return Response(json.dumps(tags, ensure_ascii=False), mimetype='application/json')
if __name__ == '__main__':
    downloader.run(host="0.0.0.0", port=7778)