from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from beer.models import Beer
import time, PIL.Image, requests, io, random
import peewee

def getInnerPage(driver, url):
    driver.get(url)
    title = driver.find_element_by_id("beerName").text
    image = driver.find_element_by_xpath("//div[@id='toggleImage']/img").get_attribute('src')
    style = driver.find_element_by_xpath('//*[@id="styleLink"]').text
    brewer = driver.find_element_by_xpath('//*[@id="brewerLink"]').text
    rate = -1
    try:
        rate = float(driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/span[1]').text.split('/')[0])
    except:
        pass
    abv = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[2]/span[1]').text
    ibu = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[3]/span[1]').text
    cal = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[2]/div[1]/div[2]/div[2]/div/div[4]/span[1]').text
    describe = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div[3]/div[2]/div/div[2]').text

    #get image size
    r = requests.get(image, stream=True)
    if not r.status_code == 200:
        return
    _image = PIL.Image.open(io.BytesIO(r.content))
    width, height = _image.size
    if height > width:
        height = height * 2/3
    aspect_ratios = [[3,1], [2,1], [20,13], [16,9], [4,3], [1.91,1], [1.51,1], [1,1], [3,4], [9,16], [1,2], [1,3]]
    aspect_ratio = min(aspect_ratios, key=lambda x:abs(x[0]/x[1] - width/height))
    beer = Beer.create(title=title, imagePath=image, style=style, brewer=brewer, rate=rate, abv=abv, ibu=ibu, cal=cal, describe=describe, originUrl=url, aspect_ratio="{}:{}".format(aspect_ratio[0], aspect_ratio[1]))
def getBeer():
    beer = Beer.select().order_by(peewee.fn.Random()).get()
    return {
        'title':beer.title,
        'imagePath':beer.imagePath,
        'style':beer.style,
        'brewer':beer.brewer,
        'rate':beer.rate,
        'abv':beer.abv,
        'ibu':beer.ibu,
        'cal':beer.cal,
        'describe':beer.describe if len(beer.describe) <= 200 else beer.describe[:197]+'...',
        'originUrl':beer.originUrl.replace("\n", '').replace(" ", ''),
        'aspect_ratio':beer.aspect_ratio
    }
if __name__ == "__main__":
    '''with open('beer2.list') as list:
        for url in list.readlines():
            driver = webdriver.Firefox()
            try:
                getInnerPage(driver, "https://www.ratebeer.com" + url)
            except Exception as e:
                print(url, e)
            driver.close()'''
    print(getBeer())

