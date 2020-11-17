import re

from ActivateRules import (isTriggeredAbeWakeUp, isTriggeredCHCWakeUp,
                           isTriggeredExplosion, isTriggeredFishWakeUp,
                           isTriggeredGanbaru, isTriggeredKGWakeUp,
                           isTriggeredLouisWakeUp, isTriggeredPaychanWakeUp,
                           isTriggeredRibWakeUp, isTriggeredScrewErk,
                           isTriggeredScrewWakeUp, isTriggeredTodayGacha,
                           isTriggeredWineSwordGodWakeUp,
                           isTriggeredYugiohWakeUp, isTriggeredYuri, isTriggeredPaychanErk, isTriggeredCatleeWakeup)
from FlexBubble import *
from GetBeer import getBeer
from cataas import getRandomCatAsync
import random
from GetPixiv import (getAllImage, getCatImage, getCHCImage, getExplosionImage,
                      getGanbaruImage, getHifumiImage, getKGImage,
                      getLoliImage, getMikuImage, getMikuLegImage,
                      getPaychanImage, getReDiveImage, getWineImage,
                      getYoshimaruImage, getYuriImage, getPaychanErkImage, getCatleeImage)
from functools import reduce
from linebot.models import CarouselContainer, FlexSendMessage, TextSendMessage, ImageSendMessage
from concurrent.futures import wait
import asyncio
from MediaWarehouse import MediaWarehouse
import json

isTenth = re.compile("([^# ]+)(?:十連|10連)$")


def getPoliceUrl():
    with open('polices.list', 'r+') as file:
        return random.choice([line for line in file])


async def getPoliceWrappers(num):
    medias = MediaWarehouse.searchMetadata(sourceType="POLICEDEP", random=True, limit=num)
    print(medias)
    return [BubbleContainer(
        direction='ltr',
        spacing='none',
        hero=ImageComponent(
            url=MediaWarehouse.convertThumbnailURL(media['id']),
            size='full',
            aspect_ratio="1:1",
            aspect_mode='cover',
            action=URIAction(label='FULL', uri=json.loads(media["additionalData"])["link"]),
        ),
        body=BoxComponent(
            layout='vertical',
            spacing='none',
            contents=[
                    BoxComponent(
                        layout='vertical',
                        margin='none',
                        spacing='none',
                        contents=[
                            BoxComponent(
                                layout='baseline',
                                spacing='none',
                                contents=[
                                    TextComponent(
                                        text=media['mainDescription'],
                                        size='xxs',
                                        weight="bold",
                                        flex=5
                                    )
                                ],
                            ),
                        ],
                    ),
            ],
        )
    ) for media in medias]


rules = [
    {'rule': isTriggeredScrewWakeUp, 'altText': "螺絲醒醒", 'func': getMikuImage},
    {'rule': isTriggeredWineSwordGodWakeUp, 'altText': "劍龍醒醒", 'func': getWineImage},
    {'rule': isTriggeredScrewErk, 'altText': "螺絲矮額", 'func': getMikuLegImage},
    {'rule': isTriggeredYugiohWakeUp, 'altText': "遊戲亡起床尿尿", 'func': getHifumiImage},
    {'rule': isTriggeredGanbaru, 'altText': "今日も一日がんばるぞい", 'func': getGanbaruImage},
    {'rule': isTriggeredFishWakeUp, 'altText': "鱻鱻醒醒", 'func': getLoliImage},
    {'rule': isTriggeredCHCWakeUp, 'altText': "CHC醒醒", 'func': getCHCImage},
    {'rule': isTriggeredLouisWakeUp, 'altText': "市場醒醒", 'func': getReDiveImage},
    {'rule': isTriggeredExplosion, 'altText': "EXPLOSION", 'func': getExplosionImage},
    {'rule': isTriggeredKGWakeUp, 'altText': "KG醒醒", 'func': getKGImage},
    {'rule': isTriggeredPaychanWakeUp, 'altText': "小裴醒醒", 'func': getPaychanImage},
    {'rule': isTriggeredYuri, 'altText': "真香", 'func': getYuriImage},
    {'rule': isTriggeredTodayGacha, 'altText': "本日卡池", 'func': getAllImage},
    {'rule': isTriggeredRibWakeUp, 'altText': "排骨醒醒", 'func': getCatImage},
    {'rule': isTriggeredAbeWakeUp, 'altText': "阿部醒醒", 'func': getYoshimaruImage},
    {'rule': isTriggeredPaychanErk, 'altText': "小裴矮額", 'func': getPaychanErkImage},
    {'rule': isTriggeredCatleeWakeup, 'altText': "貓李醒醒", 'func': getCatleeImage},
]


def isTriggeredWakeUp(text):
    text = isTenth.match(text).group(1) if isTenth.match(text) is not None else text
    return reduce(lambda accu, curr: accu or (curr if curr['rule'](text) else False), rules, False) or False


async def getWakeUpWrapper(text):
    num = 10 if isTenth.match(text) else 1
    text = isTenth.match(text).group(1) if isTenth.match(text) is not None else text
    rule = reduce(lambda accu, curr: accu or (curr if curr['rule'](text) else False), rules, False) or rules[0]
    if rule['rule'] == isTriggeredWineSwordGodWakeUp:
        bubbles = []
        for i in range(num):
            if random.random() > 0.5:
                beer = getBeer()
                bubble = getStandradRateBeerBubble(beer)
                bubbles.append(bubble)
            else:
                thumb, url, originimage, meta = await rule['func']()[0]
                bubble = getStandradPixivBubble(url, thumb, originimage, meta, "劍龍醒醒!!")
                bubbles.append(bubble)
        return FlexSendMessage(alt_text=rule['altText'], contents=(bubbles[0] if ((len(bubbles) == 1)) else CarouselContainer(contents=bubbles)))
    elif rule['rule'] == isTriggeredRibWakeUp:
        slice_point = random.randint(0, num)
        bubbles = []
        cats = []
        if(slice_point > 0):
            # cataas
            # loop = asyncio.get_event_loop()
            # asyncio.set_event_loop(loop)
            cats = await asyncio.gather(*[getRandomCatAsync() for i in range(slice_point)])
            cats = list(filter(lambda x: x is not None, cats))
            for cat in cats:
                bubble = BubbleContainer(
                    direction='ltr',
                    spacing='none',
                    hero=ImageComponent(
                        url=cat,
                        size='full',
                        aspect_ratio="1:1",
                        aspect_mode='cover',
                        action=URIAction(label='FULL', uri=cat),
                    )
                )
                bubbles.append(bubble)
        if (num - len(cats)) > 0:
            for img in await rule['func'](num - len(cats)):
                thumb, url, originimage, meta = img
                bubbles.append(getStandradPixivBubble(url, thumb, originimage, meta, rule['altText']))
        random.shuffle(bubbles)
        return FlexSendMessage(alt_text=rule['altText'], contents=(bubbles[0] if ((len(bubbles) == 1)) else CarouselContainer(contents=bubbles)))
    elif rule['rule'] == isTriggeredFishWakeUp:
        bubbles = []
        police_count = random.randint(0, num)
        if police_count > 0:
            bubbles.extend(await getPoliceWrappers(police_count))
        if police_count < num:
            for img in await rule['func'](num - police_count):
                thumb, url, originimage, meta = img
                bubbles.append(getStandradPixivBubble(url, thumb, originimage, meta, rule['altText']))
        random.shuffle(bubbles)
        return FlexSendMessage(alt_text=rule['altText'], contents=(bubbles[0] if ((len(bubbles) == 1)) else CarouselContainer(contents=bubbles)))
    else:
        bubbles = []
        for img in await rule['func'](num):
            thumb, url, originimage, meta = img
            bubbles.append(getStandradPixivBubble(url, thumb, originimage, meta, rule['altText']))
        return FlexSendMessage(alt_text=rule['altText'], contents=(bubbles[0] if ((len(bubbles) == 1)) else CarouselContainer(contents=bubbles)))


async def main():
    print(await getWakeUpWrapper("貓李醒醒十連"))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
