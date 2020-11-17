from lxml import etree
from urllib.parse import quote
import urllib.request
from urllib.request import Request, urlopen
from urllib.request import URLError, HTTPError
from binascii import a2b_base64
import regex
import json
import aiohttp


class googleimagesdownload:
    def jsdataRule(self, x):
        return x.split(";")[1]

    def build_search_url(self, search_term):
        #check safe_search
        safe_search_string = "&safe=active"
        # check the args and choose the URL
        url = 'https://www.google.com/search?q=' + quote(
            search_term.encode('utf-8')) + '&espv=2&biw=1366&bih=667&site=webhp&source=lnms&tbm=isch&sa=X&ei=XosDVaCXD8TasATItgE&ved=0CAcQ_AUoAg'

        #safe search check
        url = url + safe_search_string

        return url
    def build_ddg_search_url(self, search_term):
        url = 'https://duckduckgo.com/?q=' + quote(
            (search_term + ' !gi').encode('utf-8'))
        return url

    def findImages(self, page, link):
        # only find thumbnail and link to website
        # can be expended
        html = etree.HTML(page)
        jsdata = html.xpath("//div[contains(@class, 'isv-r')]/@jsdata")[0]
        jsdata_id = self.jsdataRule(jsdata)
        obj = regex.search('"{}",\s?\["([^"]+)",.+,.+\][^\[]*,\["([^"]+)",.+,.+\]'.format(jsdata_id), page)
        """objs = html.xpath("//img[contains(@class, \"rg_i\")]")
        try:
            link = objs[0].xpath("./ancestor::a/parent::div/a")[1].get("href")
        except:
            pass
        return [objs[0].get("src"), link]"""
        return [json.loads('"{}"'.format(obj.group(1))), json.loads('"{}"'.format(obj.group(2)))]
    
    def download_to_bytes(self, argument):
        keyword = argument['keywords']
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        req = urllib.request.Request(self.build_search_url(keyword), headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read()
        thumb_url, url = self.findImages(html.decode('utf-8'), self.build_ddg_search_url(keyword))
        if thumb_url[:4] == "http":
            req = urllib.request.Request(thumb_url, headers=headers)
            response = urllib.request.urlopen(req)
            img = response.read()
        else:
            print(thumb_url)
            img = a2b_base64(thumb_url)
        return img, url

    async def download_to_bytes_async(self, argument):
        thumb_url, url, img = None, None, None
        keyword = argument['keywords']
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(self.build_search_url(keyword)) as response:
                html = await response.read()
                thumb_url, url = self.findImages(html.decode('utf-8'), self.build_ddg_search_url(keyword))
        if thumb_url[:4] == "http":
            async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(thumb_url) as response:
                    img = await response.read()
        else:
            print(thumb_url)
            img = a2b_base64(thumb_url)
        return img, url


if __name__ == '__main__':
    gid = googleimagesdownload()
    print(gid.download_to_bytes({'keywords':"ヨシ"}))