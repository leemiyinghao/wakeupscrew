import json
import requests, re


def getPlurks(user_id):
    url = 'https://www.plurk.com/TimeLine/getPlurks'
    headers = {
        'User-Agent': 'HIMAWARI 2.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://www.plurk.com/',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
    }
    data = [
        ('user_id', user_id),
    ]

    response = requests.post('https://www.plurk.com/TimeLine/getPlurks', headers=headers, data=data)
    return json.loads(response.text)['plurks']

cleanPlurkRe = re.compile("<[^>]+>.*<\/[^>]+> ?|<[^>]+\/?> ?")
def getCleanPlurk(plurk):
    plurk['content'] = cleanPlurkRe.sub('', plurk['content'])
    return plurk
def removeEmptyPlurk(plurk):
    return not plurk['content'] == ''

if __name__ == '__main__':
    plurks = getPlurks('3184840')
    plurks = map(getCleanPlurk, plurks)
    plurks = filter(removeEmptyPlurk, plurks)
    for plurk in plurks:
        print(plurk['content'])
