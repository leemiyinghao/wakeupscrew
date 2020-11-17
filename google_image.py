#from google_images_download import *
import uuid
from PIL import Image, ImageOps
import io
from hb_google_image_download import googleimagesdownload
import time
import logging
import datetime
from MediaWarehouse import MediaWarehouse
import json


EXPIRE_LIMIT = 36*60*60  # 36hr

async def search_image(keyword):
    limit = datetime.datetime.now() - datetime.timedelta(0, EXPIRE_LIMIT)
    bufferedImg = MediaWarehouse.get(sourceType="GOOGLE", mainDescription=keyword, lastHit=limit, updateHit=True)
    if bufferedImg is None:
        res = googleimagesdownload()
        rawimg, url = await res.download_to_bytes_async({"keywords": keyword, 'limit': 1})
        MAX_THUMB_SIZE = 512
        image = Image.open(io.BytesIO(rawimg))
        width, height = image.size
        max_border = max(width, height)
        scale_factor = MAX_THUMB_SIZE/max_border if max_border > MAX_THUMB_SIZE else 1
        image = ImageOps.fit(image, [int(width*scale_factor), int(height*scale_factor)], Image.ANTIALIAS)
        image = image.convert("RGB")
        dataBuffer = io.BytesIO()
        image.save(dataBuffer, format='JPEG', quality=85)
        additionalData = json.dumps({
            "width": image.size[0],
            "height": image.size[1],
        })
        bufferedImg = MediaWarehouse.create(
            sourceType="GOOGLE",
            extension="jpg",
            data=dataBuffer.getvalue(),
            mainDescription=keyword,
            thumbnail=dataBuffer.getvalue(),
            additionalData=additionalData,
            source=url)
    additionalData = json.loads(bufferedImg['additionalData'])
    return bufferedImg['source'], MediaWarehouse.convertURL(bufferedImg['id']), additionalData['height'], additionalData['width']


if __name__ == '__main__':
    # db.create_tables([GoogleImageBuffer])
    print(search_image("修但幾咧"))
    print(search_image("寶傑我跟你說"))
    print(search_image("好的文西"))
