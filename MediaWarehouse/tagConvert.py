from MediaWarehouse import Media, MediaToTag, Tag, Tagv2
from tqdm import tqdm
import json
import gc

if __name__ == '__main__':
    '''for tag in tqdm(Tag.select().iterator(), total=Tag.select().count()):
        tagv2, _ = Tagv2.get_or_create(name=tag.name)
        MediaToTag.get_or_create(tag=tagv2, media_id=tag.media_id)'''
    for media in tqdm(Media.select(Media.id, Media.additionalData).where(Media.disabled==False).iterator(), total=Media.select(Media.id).where(Media.disabled==False).count()):
        if media.additionalData is not None and media.additionalData is not '':
            data = json.loads(media.additionalData)
            if 'pixiv_v2' not in data:
                print(media.id, media.additionalData)
                continue
            for tag in data['pixiv_v2']['tags']:
                tagv2, _ = Tagv2.get_or_create(name=tag)
                MediaToTag.get_or_create(tag=tagv2, media_id=media.id)