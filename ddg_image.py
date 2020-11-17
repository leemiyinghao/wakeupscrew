import requests, re, json, uuid, io
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps

def getVqd(keyword):
    url = "https://duckduckgo.com/?t=h_&iar=images&iaf=layout%3Aaspect-wide&iax=images&ia=images".format(keyword)
    data= [
        ('q', keyword),
    ]
    response = requests.post(url, data=data)
    searchObj = re.search(r'vqd=(\d+)\&', response.text, re.M|re.I)
    vqd = searchObj.group(1)
    return vqd

def search_image(keyword):
    vqd = getVqd(keyword)
    url = "https://duckduckgo.com/i.js?l=tw-tzh&o=json&q={}&vqd={}&f=,type:photo-photo,,&p=-1".format(keyword, vqd)
    response = requests.get(url)
    index = 0
    _path = ""
    while True:
        try:
            results = json.loads(response.text)['results']
            if len(results)==0 or index > len(results):
                return ""
            url = results[index]['image']
            path = "himawarisay/{}".format(uuid.uuid1())
            _path = save_image(url, path)
            break
        except Exception as e:
            print(e)
            index += 1
            continue
    if _path == "":
        return ""
    return "https://wakeupscrew.catlee.se/{}".format(_path)

def save_image(url, path, thumb=False):
    MAX_BORDER_SIZE = 1000
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        type = r.headers['content-type'].split('/')[-1]
        path = "{}.{}".format(path, type)
        if thumb:
            path = "thumb/{}".format(path)
        image = Image.open(io.BytesIO(r.content))
        width, height = image.size
        max_border = max(width, height)
        scale_factor = MAX_BORDER_SIZE/max_border if max_border > MAX_BORDER_SIZE else 1
        image = ImageOps.fit(image, [int(width*scale_factor), int(height*scale_factor)], Image.ANTIALIAS)
        image.save(path)
        return path
    return ""

if __name__ == '__main__':
    #print(search_image("這我不要"))
    print(search_image("維尼64蠟燭"))
    print(search_image("nekopara"))
