from MediaWarehouse import HEICEncode, Media, OriginalImage
from tqdm import tqdm
import os
from PIL import Image
import io

if __name__ == '__main__':
    '''# encoding
    for media_id in tqdm(Media.select(Media.id).where(Media.sourceType=='PIXIV'), total=Media.select(Media.id).where(Media.sourceType=='PIXIV').count()):
        media = Media.get(id=media_id)
        if len(media.datas) == 0:
            OriginalImage.create(media=media, data=HEICEncode(media._data))'''
    '''backupPath = "/CityLand02/PixivDump/"
    for media_id in tqdm(Media.select(Media.id).where(Media.sourceType=='PIXIV'), total=Media.select(Media.id).where(Media.sourceType=='PIXIV').count()):
        media = Media.get(id=media_id)
        if media._data is not None and len(media.datas)>0:
            with open(os.path.join(backupPath, "{}.{}".format(media.mainDescription, media.extension)), "wb") as img:
                img.write(media._data)
            media._data = None
            media.save()'''
    for media_id in tqdm(Media.select(Media.id).where(Media.sourceType=='PIXIV' and Media.extension=='png'),
                         total=Media.select(Media.id).where(Media.sourceType=='PIXIV' and Media.extension=='png').count()):
        media = Media.get(id=media_id)
        imgBuffer = io.BytesIO(media.thumbnail)
        imgObj = Image.open(imgBuffer)
        if imgObj.format in ['JPEG','jpeg']:
            continue
        imgObj = imgObj.convert('RGB')
        thumb = io.BytesIO()
        imgObj.save(thumb, format="jpeg", quality=85, optimize=True)
        media.thumbnail = thumb.getvalue()
        if media.thumbnail2x is not None:
            imgBuffer = io.BytesIO(media.thumbnail2x)
            imgObj = Image.open(imgBuffer)
            imgObj = imgObj.convert('RGB')
            width, height = imgObj.size
            if width > 800:
                #twidth = min([width, 1600])
                #theight = floor((twidth/width)*height + 0.5)
                #imgObj.thumbnail((twidth, theight), resample=Image.ANTIALIAS)
                thumb = io.BytesIO()
                imgObj.save(thumb, format="jpeg", quality=85, optimize=True)
                media.thumbnail2x = thumb.getvalue()
            else:
                media.thumbnail2x = None
        media.save()