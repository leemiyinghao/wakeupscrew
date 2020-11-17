import urllib.request
import uuid
from mimetypes import guess_extension
from MediaWarehouse import MediaWarehouse
import datetime
import aiohttp


def getRandomCat():
    try:
        while True:
            headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}
            source = urllib.request.urlopen(urllib.request.Request("https://cataas.com/cat", headers=headers), timeout=5)
            extension = guess_extension(source.info()['Content-Type'])
            if extension not in ["gif"]:
                extension = ".jpg" if extension == '.jpe' else extension
                extension = extension[1:]
                data = source.read()
                url = MediaWarehouse.convertURL(MediaWarehouse.create(data=data, thumbnail=data, extension=extension, mainDescription="CATAAS-{}".format(datetime.datetime.now()), source="https://cataas.com/cat", sourceType='CATAAS')['id'])
                return url
    except:
        return MediaWarehouse.convertURL(MediaWarehouse.get(sourceType='404', random=True)['id'])
async def getRandomCatAsync():
    try:
        headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'}
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get("https://cataas.com/cat") as source:
                extension = guess_extension(source.headers['Content-Type'])
                if extension not in [".gif"]:
                    extension = ".jpg" if extension == '.jpe' else extension
                    extension = extension[1:]
                    data = await source.read()
                    url = MediaWarehouse.convertURL(MediaWarehouse.create(data=data, thumbnail=data, extension=extension, mainDescription="CATAAS-{}".format(datetime.datetime.now()), source="https://cataas.com/cat", sourceType='CATAAS')['id'])
                    return url
    except Exception as e:
        return None

if __name__ == '__main__':
    print(getRandomCat())
