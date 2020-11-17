from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import textwrap
import uuid
from LangText import LangFont, TextsToLangFont
import numpy
from cv2 import VideoWriter, VideoWriter_fourcc
import time
import io
from MediaWarehouse import MediaWarehouse


def find_coeffs(pa, pb):
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

    A = numpy.matrix(matrix, dtype=numpy.float)
    B = numpy.array(pb).reshape(8)

    res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
    return numpy.array(res).reshape(8)


def drawTextInBox(text, boxLocation, boxSize, draw, fontsize=320, color=(255, 255, 255, 255), weight='regular', background=(0, 0, 0, 0), vertical=False):
    #boxSize = [boxSize[1], boxSize[0]] if vertical else boxSize
    DRAWAREA = boxSize
    FONTSIZE = fontsize
    #image = Image.open('himawarisay.jpg')
    x_id, y_id = (1, 0) if vertical else (0, 1)
    while True:
        langFonts = TextsToLangFont(text, FONTSIZE, color=color, weight=weight)
        lines = []
        _langFonts = langFonts[:]
        new_line = []
        if max([lf.getSize()[x_id] for lf in _langFonts]) > DRAWAREA[x_id]:
            FONTSIZE = int(FONTSIZE*(DRAWAREA[x_id]/max([lf.getSize()[x_id] for lf in _langFonts]))**0.5)
            if FONTSIZE < 5:
                return False
            continue
        while len(_langFonts) > 0:
            if sum([o.getSize()[x_id] for o in new_line]) + _langFonts[0].getSize()[x_id] <= DRAWAREA[x_id] and not _langFonts[0]._text == "\n":
                new_line.append(_langFonts[0])
                _langFonts = _langFonts[1:]
            else:
                if _langFonts[0]._text == "\n":
                    _langFonts = _langFonts[1:]
                if len(new_line) > 0:
                    lines.append(new_line[:])
                    new_line = []
        if len(new_line) > 0:
            lines.append(new_line[:])
        total_height = sum([max([char.getSize()[y_id] for char in line]) for line in lines])
        total_width = max([sum([char.getSize()[x_id] for char in line]) for line in lines])
        if total_height > DRAWAREA[y_id]:
            FONTSIZE = int(FONTSIZE*(DRAWAREA[y_id]/total_height)**0.5)
            if FONTSIZE < 5:
                return False
            continue
        else:
            boxLocation[y_id] = boxLocation[y_id] + (DRAWAREA[y_id] - total_height)/2
            boxLocation[x_id] = boxLocation[x_id] + (DRAWAREA[x_id] - total_width)/2
            pointer = boxLocation[:]
            for line in lines:
                line_width = sum([o.getSize()[x_id] for o in line])
                line_height = max([char.getSize()[y_id] for char in line])
                if not background[3] == 0:
                    draw.rectangle(((pointer[x_id], pointer[y_id]), (pointer[x_id] + line_width, pointer[y_id] + line_height)), fill=background)
                for char in line:
                    char.draw(draw, pointer)
                    width = char.getSize()[x_id]
                    pointer[x_id] += width
                pointer[y_id] += max([char.getSize()[y_id] for char in line])
                pointer[x_id] = boxLocation[x_id]
            break
    return True


async def getHimawariSay(text):
    media = MediaWarehouse.get(sourceType="HIMAWARISAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('himawarisay.jpg')
    if drawTextInBox(text, [795, 140], [915, 725], draw) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [960, 540], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="HIMAWARISAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['himawarisay', 'himawarisay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getHimawariSay2(text):
    media = MediaWarehouse.get(sourceType="HIMAWARISAY_ㄉ", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1500, 1500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('himawarisay2.jpg')
    if drawTextInBox(text, [225, 207], [639, 426], draw, fontsize=128, color=(0, 0, 0, 255)) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [750, 750], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="HIMAWARISAY_2",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['himawarisay', 'himawarisay_2'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getHimawariSay3(text):
    media = MediaWarehouse.get(sourceType="HIMAWARISAY_3", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (3941, 2955), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('himawarisay3.jpg')
    if drawTextInBox(text, [2029, 1705], [1700, 1100], draw, fontsize=1024, color=(0, 0, 0, 200), weight='black') == False:
        return False, False
    if drawTextInBox(text, [2009, 1685], [1700, 1100], draw, fontsize=1024, color=(255, 255, 255, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [985, 738], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="HIMAWARISAY_3",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['himawarisay', 'himawarisay_3'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay.jpg')
    if drawTextInBox(text, [795, 140], [915, 725], draw) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [960, 540], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay2(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_2", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    FONTSIZE = 288
    watermark = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay2.jpg')
    if drawTextInBox(text, [0, 0], [807, 784], draw, fontsize=256, color=(255, 255, 255, 200), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [960, 540], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_2",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_2'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay3(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_3", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (3024, 4032), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay3.jpg')
    if drawTextInBox(text, [200, 150], [1300, 1400], draw, fontsize=320, color=(0, 0, 0, 200), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [1512, 2016], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [756, 1008], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_3",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_3'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay4(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_4", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (4032, 3024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay4.jpg')
    if drawTextInBox(text, [400, 200], [3500, 1350], draw, fontsize=640, color=(255, 255, 255, 255), weight='black', background=(0, 0, 0, 192)) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [2016, 1512], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_4",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_4'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay5(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_5", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (4032, 3024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay5.jpg')
    if drawTextInBox(text, [120, 20], [1800, 3024], draw, fontsize=640, color=(0, 0, 0, 255), weight='black') == False:
        return False, False
    if drawTextInBox(text, [100, 0], [1800, 3024], draw, fontsize=640, color=(255, 255, 255, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [2016, 1512], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_5",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_5'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay6(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_6", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (4032, 3024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay6.jpg')
    if drawTextInBox(text, [1900, 200], [1950, 2600], draw, fontsize=640, color=(5, 97, 224, 128), weight='black', background=(255, 255, 255, 220)) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [2016, 1512], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_6",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_6'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getScrewSay7(text):
    media = MediaWarehouse.get(sourceType="SCREWSAY_7", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (640, 779), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('screwsay7.jpg')
    coeffs = find_coeffs([(4, 0), (640, 104), (636, 779), (0, 640)],
                         [(0, 0), (615, 0), (615, 625), (0, 625)])
    if drawTextInBox(text, [0, 0], [615, 625], draw, fontsize=160, color=(0, 0, 0, 200), weight='serif', vertical=True) == False:
        return False, False
    watermark = watermark.transform((1000, 1000), Image.PERSPECTIVE, coeffs, Image.BICUBIC)
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (1809, 2265), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [2016, 1512], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="SCREWSAY_7",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['screwsay', 'screwsay_7'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getCHCSay(text):
    media = MediaWarehouse.get(sourceType="CHCSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    FONTSIZE = 144
    watermark = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('chcsay.jpg')
    if drawTextInBox(text, [795, 140], [915, 725], draw) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [960, 540], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="CHCSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['chcsay', 'chcsay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getCHCSay2(text):
    media = MediaWarehouse.get(sourceType="CHCSAY_2", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    FONTSIZE = 144
    watermark = Image.new('RGBA', (3024, 2016), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('chcsay2.jpg')
    if drawTextInBox(text, [40, 0], [2800, 800], draw, fontsize=320, color=(255, 255, 255, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    ImageOps.fit(image, [2016, 1512], Image.ANTIALIAS).save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="CHCSAY_2",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['chcsay', 'chcsay_2'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getCHCSay3(text):
    media = MediaWarehouse.get(sourceType="CHCSAY_3", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    FONTSIZE = 144
    watermark = Image.new('RGBA', (3024, 4032), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('chcsay3.jpg')
    if drawTextInBox(text, [70, 1550], [2870, 1250], draw, fontsize=640, color=(255, 255, 255, 255), weight='black', background=(0, 0, 0, 220)) == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [960, 540], Image.ANTIALIAS)
    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="CHCSAY_3",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['chcsay', 'chcsay_3'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getWineSwordGodSay(text):
    media = MediaWarehouse.get(sourceType="WINESWORDGODSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (4032, 3024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('wineswordgodsay.jpg')
    if drawTextInBox(text, [2025, 0], [2007, 3024], draw, fontsize=512, color=(255, 255, 255, 200), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="WINESWORDGODSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['wineswordgodsay', 'windswordgodsay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getMapoSay(text):
    media = MediaWarehouse.get(sourceType="MAPOSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1706, 960), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('maposay.jpg')
    if drawTextInBox(text, [1080, 0], [626, 960], draw, fontsize=256, color=(255, 255, 255, 200), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0.2)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [853, 480], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="MAPOSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['maposay', 'maposay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getPayChanSay(text):
    media = MediaWarehouse.get(sourceType="PAYCHANSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1300, 700), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('paychansay.jpg')
    if drawTextInBox(text, [0, 0], [1300, 700], draw, fontsize=512, color=(255, 255, 255, 255), weight='serif_black') == False:
        return False, False
    coeffs = find_coeffs([[1341, 2285], [2369, 2061], [2369, 2761], [1341, 3013]],
                         [(0, 0), (1300, 0), (1300, 700), (0, 700)])
    _watermark = watermark.transform((4032, 3024), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    mask = ImageEnhance.Brightness(_watermark).enhance(0.2)
    image.paste(_watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1008, 756], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="PAYCHANSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['paychansay', 'paychansay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getLouisSay(text):
    media = MediaWarehouse.get(sourceType="LOUISSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (1477, 1110), (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('louissay.jpg')
    if drawTextInBox(text, [89, 3], [700, 698], draw, fontsize=512, color=(255, 255, 255, 255), weight='black') == False:
        return False, False
    if drawTextInBox(text, [86, 0], [700, 698], draw, fontsize=512, color=(245, 209, 187, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [738, 555], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="LOUISSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['louissay', 'louissay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getWayfishSay(text):
    media = MediaWarehouse.get(sourceType="WAYFISHSAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (2592, 1936), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('wayfishsay.jpg')
    if drawTextInBox(text, [1650, 0], [942, 860], draw, fontsize=512, color=(255, 255, 255, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0)
    image.paste(watermark, (0, 0), mask)
    data = io.BytesIO()
    image.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    thumb = ImageOps.fit(image, [1296, 968], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    media = MediaWarehouse.create(
        sourceType="WAYFISHSAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['wayfishsay', 'wayfishsay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getCatleeSay(text):
    media = MediaWarehouse.get(sourceType="CATLEESAY_1", mainDescription=text)
    if media is not None:
        url = MediaWarehouse.convertURL(media['id'])
        thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
        return url, thumbnailURL
    watermark = Image.new('RGBA', (960, 1706), (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)
    image = Image.open('catleeSay.jpg')
    if drawTextInBox(text, [0, 540], [960, 1166], draw, fontsize=512, color=(0, 0, 0, 255), weight='black') == False:
        return False, False
    mask = ImageEnhance.Brightness(watermark).enhance(0)
    image.paste(watermark, (0, 0), mask)
    thumb = ImageOps.fit(image, [240, 429], Image.ANTIALIAS)

    thumbnail = io.BytesIO()
    thumb.save(thumbnail, format='JPEG', quality=85)
    thumbnail = thumbnail.getvalue()
    data = io.BytesIO()
    thumb.save(data, format='JPEG', quality=85)
    data = data.getvalue()
    media = MediaWarehouse.create(
        sourceType="CATLEESAY_1",
        mainDescription=text,
        data=data,
        thumbnail=thumbnail,
        tags=['catleesay', 'catleesay_1'],
        extension='jpg'
    )
    url = MediaWarehouse.convertURL(media['id'])
    thumbnailURL = MediaWarehouse.convertThumbnailURL(media['id'])
    return url, thumbnailURL


async def getEraSay(text):
    watermark_board = Image.new('RGBA', (640, 360), (0, 0, 0, 0))
    draw_board = ImageDraw.Draw(watermark_board)
    if drawTextInBox(text, [0, 0], [150, 175], draw_board, fontsize=60, color=(0, 0, 0, 200), weight='serif_black', vertical=True) == False:
        return False, False
    watermark_bottom = Image.new('RGBA', (540, 40), (0, 0, 0, 0))
    draw_bottom = ImageDraw.Draw(watermark_bottom)
    if drawTextInBox("新元号は「{}」に決定".format(text), [0, 0], [540, 40], draw_bottom, fontsize=30, color=(0, 0, 0, 255), weight='sans') == False:
        return False, False
    borders = numpy.load('reiwa_borders_s.npy')
    borders = borders/2
    _id = uuid.uuid1()
    filename = "{}.mp4".format(_id)
    thumb = "{}.jpg".format(_id)
    fourcc = VideoWriter_fourcc(*'avc1')
    video = VideoWriter("himawarisay/" + filename, fourcc, float(15), (640, 360))
    total = 0
    for i in range(500):
        if not i % 5 == 0:
            continue
        pa, pb, pd, pc = borders[i]
        image = Image.open('reiwa_splited/{:03}.jpg'.format(i))
        coeffs = find_coeffs([pa, pb, pc, pd],
                             [(0, 0), (150, 0), (150, 175), (0, 175)])
        _watermark_board = watermark_board.transform((640, 360), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
        mask_board = ImageEnhance.Brightness(_watermark_board).enhance(0.2)
        image.paste(_watermark_board, (0, 0), mask_board)
        mask_bottom = ImageEnhance.Brightness(watermark_bottom).enhance(0.2)
        image.paste(watermark_bottom, (50, 305), mask_bottom)
        video.write(numpy.array(image.convert('RGB'))[..., ::-1])
        if i == 0:
            ImageOps.fit(image, [640, 360], Image.ANTIALIAS).save("himawarisay/thumb/" + thumb)
    video.release()
    return "himawarisay/" + filename, "himawarisay/thumb/" + thumb


if __name__ == '__main__':
    '''print('getScrewSay', getScrewSay("少年阿\n要\n胸 懷大志"))
    print('getScrewSay2', getScrewSay2("少年阿\n要\n胸 懷大志"))
    print('getScrewSay3', getScrewSay3("少年阿\n要\n胸懷大志"))
    print('getScrewSay4', getScrewSay4("少年阿\n要\n胸懷大志"))
    print('getScrewSay5', getScrewSay5("少年阿\n要\n胸懷大志"))
    print('getScrewSay6', getScrewSay6("少年阿\n要\n胸懷大志"))
    print('getScrewSay7', getScrewSay7("少年阿\n要\n胸懷大志"))
    print('getCHCSay7', getCHCSay("少年阿\n要\n胸懷大志"))
    print('getCHCSay7', getCHCSay2("少年阿\n要\n胸懷大志"))
    print('getCHCSay7', getCHCSay3("少年阿\n要\n胸懷大志"))
    print('getHimawariSay', getHimawariSay("少年阿\n要\n胸懷大志"))
    #print('getScrewSay7', getScrewSay7("少年阿\n要\n胸懷\n大志"))
    old_time = time.time()
    #print('getEraSay', getEraSay("少年"))
    #print('getHimawariSay3', getHimawariSay3("買買買"))
    print("getWineSwordGodSay", getWineSwordGodSay("不是喝酒，是與穀麥的靈魂對話"))
    print('getMapoSay', getMapoSay("少年阿\n要\n胸懷大志"))'''
    #print('getPayChanSay', getPayChanSay("🙂"))
    #print(time.time() - old_time)
    #print('getWayfishSay', getWayfishSay("（/w\）"))
    print(getCatleeSay("{}".format(time.time())))
