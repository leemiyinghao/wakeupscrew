from lxml import etree
import urllib.parse
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import random
from PIL import Image, ImageSequence
import numpy
from cv2 import VideoWriter, VideoWriter_fourcc
import io
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
from apiclient.discovery import build
from selenium.webdriver.common.keys import Keys

DEVELOPER_KEY = "YT_DEVELOPER_KEY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

option = webdriver.ChromeOptions()
option.add_argument('--no-sandbox')
option.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=option)
driver.set_window_size(1024, 768)
driver.get("https://www.youtube.com/")

def fetchYTRenderingData(keyword):
    params = urllib.parse.urlencode({'search_query': keyword})
    #driver.get("https://www.youtube.com/results?{}".format(params))
    driver.find_element_by_id("search").send_keys(Keys.CONTROL, 'a')
    driver.find_element_by_id("search").send_keys(Keys.BACK_SPACE)
    driver.find_element_by_id("search").send_keys(keyword)
    driver.find_element_by_id("search-icon-legacy").click()
    time.sleep(5)
    targets = driver.find_elements_by_xpath('//ytd-video-renderer')
    datas = []
    for target in targets:
        hover = ActionChains(driver).move_to_element(target)
        hover.perform()
        title = target.find_element_by_id('video-title').text
        webp = target.find_element_by_xpath("//img[contains(@class,'ytd-moving-thumbnail-renderer')]").get_attribute('src')
        datas.append({'title': title,
                      'webp_url': webp})
    #driver.quit()
    return datas

def fetchYTRenderingData2(keyword):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(
        q=keyword,
        part="id,snippet",
        maxResults=25
    ).execute()
    datas = []
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            datas.append({'webp_url': search_result['snippet']['thumbnails']['high']['url']})
    return datas


def packSaveYTData(datas, rand=False):
    if rand:
        random.shuffle(datas)
    for target in datas:
    # download webp
        req = urllib.request.Request(target['webp_url'])
        with urllib.request.urlopen(req) as _webp:
            return webp2mp4(_webp)
    return None

def scale(im, ratio):
    w, h = im.size
    c_w, c_h = [i / ratio for i in im.size]
    box = ((w-c_w)/2, (h-c_h)/2, w-((w-c_w)/2), h-(h-c_h)/2)
    im = im.crop(box)
    im = im.resize((w,h), Image.BICUBIC)
    return im
    

def webp2mp4(_buffer):
    _id = uuid.uuid1()
    filename = "himawarisay/{}.mp4".format(_id)
    thumbname = "himawarisay/{}.png".format(_id)
    im = Image.open(_buffer)
    width, height = im.size
    fourcc = VideoWriter_fourcc(*'avc1')
    video = VideoWriter(filename, fourcc, float(8), (width, height))
    for frame in ImageSequence.Iterator(im):
        if frame.im is not None:
            for i in range(int(frame.info['duration']/125)):
                video.write(numpy.array(frame.convert('RGB'))[...,::-1])
        else:
            video.write(numpy.array(frame.convert('RGB'))[...,::-1])
            frame.save(thumbname)
    """for ratio in [1.5+numpy.sin(i)/2 for i in numpy.arange(0, numpy.pi*4, numpy.pi*4/180)]:
        video.write(numpy.array(scale(im, ratio).convert('RGB'))[...,::-1])"""
    video.release()
    #im.save(thumbname)
    return filename, thumbname, width, height

async def searchYT(keyword):
    try:
        data = fetchYTRenderingData(keyword.replace('_', ' '))
        res = packSaveYTData(data)
        return res
    except:
        driver.get("https://www.youtube.com/")
        return None

if __name__ == '__main__':
    print(searchYT('初音ミク'))
    # read webp
