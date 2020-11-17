from MediaWarehouse import MediaWarehouse, Media
import io
from tqdm import tqdm
from PIL import Image
from math import floor

def get_rotate_degree(im_obj):
    degree = 0
    if hasattr(im_obj, '_getexif'):
        info = im_obj._getexif()
        ret = dict()
        degree_dict = {1: 0, 3: 180, 6: -90, 8: 90}
        if info:
            orientation = info.get(274, 0)
            degree = degree_dict.get(orientation, 0)
    return degree

if __name__ == '__main__':
    #sourceTypes = ["MIKU", "GANBARU", "YOGIOH_WAKE", "LOLI", "ERK"]
    sourceTypes = ["YUGIOH_WAKE"]
    for id in tqdm(
        Media.select(Media.id).where(Media.sourceType << sourceTypes),
        total=Media.select(Media.id).where(Media.sourceType << sourceTypes).count()):
        media = Media.get(id=id)
        imgBuffer = io.BytesIO(media.data)
        img = Image.open(imgBuffer)
        format = img.format
        img = img.rotate(get_rotate_degree(img))
        width, height = img.size
        twidth = min([width, 1600])
        theight = floor((twidth/width)*height + 0.5)
        img.thumbnail((twidth, theight), resample=Image.ANTIALIAS)
        thumb = io.BytesIO()
        img.save(thumb, format=format, quality=100)
        media.thumbnailRetina = thumb.getvalue()
        
        img = Image.open(imgBuffer)
        format = img.format
        img = img.rotate(get_rotate_degree(img))
        width, height = img.size
        twidth = min([width, 800])
        theight = floor((twidth/width)*height + 0.5)
        img.thumbnail((twidth, theight), resample=Image.ANTIALIAS)
        thumb = io.BytesIO()
        img.save(thumb, format=format, quality=100)
        media.thumbnail = thumb.getvalue()
        media.save()