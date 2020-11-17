import datetime
import json
import logging
import math
import os
import random
import re
import traceback

#from flask import Flask, abort, request
from quart import Quart, abort, request
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (AudioMessage, BeaconEvent, BoxComponent,
                            BubbleContainer, ButtonComponent, ButtonsTemplate,
                            CameraAction, CameraRollAction, CarouselColumn,
                            CarouselTemplate, ConfirmTemplate,
                            DatetimePickerAction, FileMessage, FlexSendMessage,
                            FollowEvent, IconComponent, ImageCarouselColumn,
                            ImageCarouselTemplate, ImageComponent,
                            ImageMessage, ImageSendMessage, JoinEvent,
                            LeaveEvent, LocationAction, LocationMessage,
                            LocationSendMessage, MessageAction, MessageEvent,
                            PostbackAction, PostbackEvent, QuickReply,
                            QuickReplyButton, SeparatorComponent, SourceGroup,
                            SourceRoom, SourceUser, SpacerComponent,
                            StickerMessage, StickerSendMessage,
                            TemplateSendMessage, TextComponent, TextMessage,
                            TextSendMessage, UnfollowEvent, URIAction,
                            VideoMessage, VideoSendMessage)
from numpy.random import choice

from ActivateRules import *
from cataas import getRandomCat
from draw import (getCatleeSay, getCHCSay, getCHCSay2, getEraSay,
                  getHimawariSay, getHimawariSay2, getHimawariSay3,
                  getLouisSay, getMapoSay, getPayChanSay, getScrewSay,
                  getScrewSay2, getScrewSay3, getScrewSay4, getScrewSay5,
                  getScrewSay6, getScrewSay7, getWayfishSay,
                  getWineSwordGodSay)
from FinancePorter import getFinance
from FlexBubble import *
from GetBeer import getBeer
from GetPixiv import *
from GetPixivWrapper import getWakeUpWrapper, isTriggeredWakeUp
#from ddg_image import search_image
from google_image import search_image
from homebrew_plurk_api import getCleanPlurk, getPlurks, removeEmptyPlurk
from MediaWarehouse.MediaWarehouse import db
#from transgender import TG
from vec2seq import vec2seq
from yt_searcher.YTSearcher import searchYT

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def getHimawariSayRandom():
    plurks = getPlurks('3184840')
    plurks = map(getCleanPlurk, plurks)
    plurks = list(filter(removeEmptyPlurk, plurks))
    return random.choice(plurks)['content']


def getPoliceUrl():
    with open('polices.list', 'r+') as file:
        return random.choice([line for line in file])


app = Quart(__name__)

line_bot_api = LineBotApi('LINE_API_TOKEN')
parser = WebhookParser('LINE_API_SECRECT')


@app.before_request
async def _db_connect():
    db.connect()


@app.teardown_request
async def _db_close(exc):
    if not db.is_closed():
        db.close()

@app.route("/keepalive")
async def keepalive():
    return "alive"


@app.route("/line", methods=['GET', 'POST'])
async def line():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # # get request body as text
    #body = await request.get_data(as_text=True)
    body = await request.get_data()
    try:
        events = parser.parse(body.decode(), signature)
    except InvalidSignatureError:
        abort(400)
    except LineBotApiError:
        abort(400)
    for event in events:
        if isinstance(event, MessageEvent) and event.message.type == 'text':
            if isTriggeredWakeUp(event.message.text):
                contents = await getWakeUpWrapper(event.message.text)
                line_bot_api.reply_message(
                    event.reply_token,
                    contents
                )
            elif isTriggeredPixiv(event.message.text):
                try:
                    tags = pixivgrabber.findall(event.message.text)
                    thumb, url, originimage, meta = await getImageByTag(tags, tagOr=False)
                    bubble = getStandradPixivBubble(url, thumb, originimage, meta, event.message.text)
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage(alt_text=event.message.text, contents=bubble)
                    )
                except:
                    pass
            elif isTriggeredHimawariWakeup(event.message.text):
                filename, company, name, lastOpen, lastClose, currency = await getFinance('himawarisay')
                bubble = getStandradStockPriceBubble(filename, company, name, lastOpen, lastClose, currency)
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(alt_text="長輩買", contents=bubble)
                )
            elif isTriggeredHimawariSound(event.message.text):
                num = random.randint(0,2)
                if num == 0:
                    filename, thumbname = await getHimawariSay("買爆")
                elif num == 1:
                    filename, thumbname = await getHimawariSay2("買爆")
                else:
                    filename, thumbname = await getHimawariSay3("買爆")
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
            elif isTriggeredHimawariSay(event.message.text):
                say = himawarisaychecker.match(event.message.text).group(2)
                num = random.randint(0, 2)
                if not himawarisaychecker.match(event.message.text).group(1) == "":
                    num = int(himawarisaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getHimawariSay(say)
                elif num == 1:
                    filename, thumbname = await getHimawariSay2(say)
                else:
                    filename, thumbname = await getHimawariSay3(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredHimawariSayRandom(event.message.text):
                say = getHimawariSayRandom()
                num = random.randint(0, 3)
                if not himawarisayrandomchecker.match(event.message.text).group(1) == "":
                    num = int(himawarisayrandomchecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getHimawariSay(say)
                elif num == 1:
                    filename, thumbname = await getHimawariSay2(say)
                else:
                    filename, thumbname = await getHimawariSay3(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredCHCSay(event.message.text):
                say = chcsaychecker.match(event.message.text).group(2)
                num = random.randint(0, 3)
                if not chcsaychecker.match(event.message.text).group(1) == "":
                    num = int(chcsaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getCHCSay(say)
                else:
                    filename, thumbname = await getCHCSay2(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredScrewSay(event.message.text):
                say = screwsaychecker.match(event.message.text).group(2)
                num = random.randint(0, 4)
                if not screwsaychecker.match(event.message.text).group(1) == "":
                    num = int(screwsaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getScrewSay(say)
                elif num == 1:
                    filename, thumbname = await getScrewSay2(say)
                elif num == 2:
                    filename, thumbname = await getScrewSay3(say)
                elif num == 3:
                    filename, thumbname = await getScrewSay4(say)
                elif num == 4:
                    filename, thumbname = await getScrewSay5(say)
                elif num == 5:
                    filename, thumbname = await getScrewSay6(say)
                else:
                    filename, thumbname = await getScrewSay7(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredWineSwordGodSay(event.message.text):
                say = wineswordgodsaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not wineswordgodsaychecker.match(event.message.text).group(1) == "":
                    num = int(wineswordgodsaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getWineSwordGodSay(say)
                else:
                    filename, thumbname = await getWineSwordGodSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredMapoSay(event.message.text):
                say = maposaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not maposaychecker.match(event.message.text).group(1) == "":
                    num = int(maposaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getMapoSay(say)
                else:
                    filename, thumbname = await getMapoSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredPayChanSay(event.message.text):
                say = paychansaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not paychansaychecker.match(event.message.text).group(1) == "":
                    num = int(paychansaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getPayChanSay(say)
                else:
                    filename, thumbname = await getPayChanSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredLouisSay(event.message.text):
                say = louissaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not louissaychecker.match(event.message.text).group(1) == "":
                    num = int(louissaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getLouisSay(say)
                else:
                    filename, thumbname = await getLouisSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredWayfishSay(event.message.text):
                say = wayfishsaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not wayfishsaychecker.match(event.message.text).group(1) == "":
                    num = int(wayfishsaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getWayfishSay(say)
                else:
                    filename, thumbname = await getWayfishSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredCatleeSay(event.message.text):
                say = catlesaychecker.match(event.message.text).group(2)
                num = random.randint(0, 1)
                if not catlesaychecker.match(event.message.text).group(1) == "":
                    num = int(catlesaychecker.match(event.message.text).group(1))-1
                if num == 0:
                    filename, thumbname = await getCatleeSay(say)
                else:
                    filename, thumbname = await getCatleeSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        ImageSendMessage(
                            original_content_url=filename,
                            preview_image_url=thumbname
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredEraSay(event.message.text):
                say = erasaychecker.match(event.message.text).group(1)
                filename, thumbname = await getEraSay(say)
                if not filename == False:
                    line_bot_api.reply_message(
                        event.reply_token,
                        VideoSendMessage(
                            original_content_url="https://wakeupscrew.catlee.se/{}".format(filename),
                            preview_image_url="https://wakeupscrew.catlee.se/{}".format(thumbname)
                        )
                    )
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 400, 幹話太長")
                    )
            elif isTriggeredjpg(event.message.text):
                time_s = datetime.datetime.now()
                try:
                    keyword = jpgchecker.match(event.message.text).group(1)
                    for i in range(3):
                        try:
                            tmp = await search_image(keyword)
                            image, thumb, height, width = tmp
                            break
                        except Exception as e:
                            if i < 2:
                                continue
                            else:
                                track = traceback.format_exc()
                                print(track)
                                raise e
                    aspect_ratios = [[3, 1], [2, 1], [20, 13], [16, 9], [4, 3], [1.91, 1], [1.51, 1], [1, 1], [3, 4], [9, 16], [1, 2], [1, 3]]
                    aspect_ratio = min(aspect_ratios, key=lambda x: abs(x[0]/x[1] - width/height))
                    if len(image) > 0:
                        bubble = BubbleContainer(
                            direction='ltr',
                            spacing='none',
                            hero=ImageComponent(
                                url=thumb,
                                size='full',
                                aspect_ratio="{}:{}".format(aspect_ratio[0], aspect_ratio[1]),
                                aspect_mode='cover',
                                action=URIAction(label='FULL', uri=image),
                            )
                        )
                        line_bot_api.reply_message(
                            event.reply_token,
                            FlexSendMessage(alt_text=keyword, contents=bubble)
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage("Error 404, 螺絲找不到, 螺絲QQ")
                        )
                except Exception as e:
                    print(keyword, e)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 404, 螺絲找不到, 螺絲QQ")
                    )
            elif isTriggeredmp4(event.message.text):
                try:
                    keyword = mp4checker.match(event.message.text).group(1).replace("_", " ")
                    video, thumb, height, width = await searchYT(keyword)
                    aspect_ratios = [[3, 1], [2, 1], [20, 13], [16, 9], [4, 3], [1.91, 1], [1.51, 1], [1, 1], [3, 4], [9, 16], [1, 2], [1, 3]]
                    aspect_ratio = min(aspect_ratios, key=lambda x: abs(x[0]/x[1] - width/height))
                    if len(video) > 0:
                        line_bot_api.reply_message(
                            event.reply_token,
                            VideoSendMessage(
                                original_content_url="https://wakeupscrew.catlee.se/{}".format(video),
                                preview_image_url="https://wakeupscrew.catlee.se/{}".format(thumb),
                            )
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage("Error 404, 螺絲找不到, 螺絲QQ")
                        )
                except Exception as e:
                    print(keyword)
                    traceback.print_exc()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage("Error 404, 螺絲找不到, 螺絲QQ")
                    )
            elif isTriggeredSenComPlete(event.message.text):
                keyword = sencompletechecker.match(event.message.text).group(1)
                try:
                    v_answer = None
                    try:
                        v_answer = await vec2seq.searchNNSentence(keyword, cascading=False)
                    except:
                        pass
                    if v_answer is not None:
                        #keyword = "{}？{}".format(keyword, random.choice(v_answer))
                        r_answer = choice([_v[0] for _v in v_answer], 1, [2**(_v[1]*10) for _v in v_answer])
                        #triggerTransgender = random.random() > float(sum([2**(_v[1]*10) for _v in v_answer]))/(float(sum([2**(_v[1]*10) for _v in v_answer])+(2**7.0)))
                        triggerTransgender = False
                    else:
                        triggerTransgender = True
                        r_answer = ""
                    if triggerTransgender:
                        #result = TG.answer(keyword)
                        pass
                    else:
                        result = r_answer[0]
                    if not result == None:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(result)
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage('阿哈哈，螺絲不知道')
                        )
                except Exception as e:
                    print(e)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage('阿哈哈，螺絲不知道')
                    )
            else:
                pass
    return 'OK'


if __name__ == "__main__":
    app.run(port=7739)
    #print(getStandradPixivBubble("","","",{'id':""}, ""))
