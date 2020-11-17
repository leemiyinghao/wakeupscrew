from linebot import LineBotApi, WebhookParser

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton, VideoSendMessage, CarouselContainer
)

nonetoemptystring = lambda x:"_" if x is None else x

def getStandradPixivBubble(url, thumb, originimage, meta, button_text, button_color="#17c950"):
    meta['caption'] = nonetoemptystring(meta['caption'])
    meta['title'] = nonetoemptystring(meta['title'])
    meta['user']['name'] = nonetoemptystring(meta['user']['name'])
    width = float(meta['width'])
    height = float(meta['height'])
    if height > width:
        height = height * 2/3
    aspect_ratios = [[2,1], [4,3], [1,1]]
    aspect_ratio = min(aspect_ratios, key=lambda x:abs(x[0]/x[1] - width/height))
    bubble = BubbleContainer(
        direction='ltr',
        spacing='none',
        hero=ImageComponent(
            url=thumb,
            size='full',
            aspect_ratio="{}:{}".format(aspect_ratio[0], aspect_ratio[1]),
            aspect_mode='cover',
            action=URIAction(label='大圖', uri=url),
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
                                    text="{}/{}".format(meta['user']['name'],meta['title']),
                                    size='xxs',
                                    weight="bold",
                                    flex=5
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text='At',
                                    color='#aaaaaa',
                                    size='xxs',
                                    flex=1
                                ),
                                TextComponent(
                                    text=meta['created_time'],
                                    wrap=True,
                                    color='#666666',
                                    size='xxs',
                                    flex=5,
                                ),
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text='Tags',
                                    color='#aaaaaa',
                                    size='xxs',
                                    flex=1
                                ),
                                TextComponent(
                                    text=" ".join(map(lambda x:"#"+x, meta['tags'])),
                                    color='#666666',
                                    size='xxs',
                                    flex=5
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )
    )
    return bubble

def getRate(rate):
    if rate < 0:
        return [
            TextComponent(
                text="RATING UNKNOW",
                size='sm',
                color='#aaaaaa',
                flex=1,
                margin='md'
            )
        ]
    component = []
    _rate = int(rate)
    for i in range(_rate):
        component.append(
            IconComponent(
                size='sm',
                url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
            )
        )
    for i in range(5 - _rate):
        component.append(
            IconComponent(
                size='sm',
                url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'
            )
        )
    component.append(
        TextComponent(
            text=str(rate),
            size='sm',
            color='#aaaaaa',
            flex=1,
            margin='md'
        )
    )
    return component

def getStandradRateBeerBubble(beer):
    bubble = BubbleContainer(
        direction='ltr',
        spacing='none',
        hero=ImageComponent(
            url=beer['imagePath'],
            size='md',
            aspect_ratio=beer['aspect_ratio'],
            aspect_mode='cover',
            action=URIAction(label='RateBeer', uri=beer['originUrl']),
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
                                    text=beer['title'],
                                    size='md',
                                    weight="bold",
                                    flex=5
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            margin='md',
                            contents=getRate(beer['rate'])
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="Style",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text=beer['style'],
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="Brewer",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text=beer['brewer'],
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="ABV",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text=beer['abv'],
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="IBU",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text=beer['ibu'],
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="EST. CAL.",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text="{} cal".format(beer['cal']),
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text=beer['describe'],
                                    wrap=True,
                                    size='xxs',
                                    color='#aaaaaa',
                                    flex=5
                                )
                            ],
                        ),
                    ],
                )
            ],
        ),
    )
    return bubble

def getStandradStockPriceBubble(img, company, name, lastOpen, lastClose, currency):
    bubble = BubbleContainer(
        direction='ltr',
        spacing='none',
        hero=ImageComponent(
            url=img,
            size='full',
            aspect_ratio='4:3',
            aspect_mode='cover',
            action=URIAction(label='Yahoo Finance', uri="https://finance.yahoo.com/quote/{}".format(company)),
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
                                    text=name,
                                    wrap=True,
                                    size='md',
                                    weight="bold",
                                    flex=5
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="前日開盤",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text="{:.2f} {}".format(lastOpen, currency),
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="前日收盤",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text="{:.2f} {}".format(lastClose, currency),
                                    size='xxs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="前日漲跌",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text="{}{:.2f} ({}{:.2f}%)".format(
                                        "" if (lastClose - lastOpen) <0 else "+",
                                        lastClose - lastOpen,
                                        "" if (lastClose - lastOpen) <0 else "+",
                                        (lastClose - lastOpen)*100/lastOpen
                                    ),
                                    size='xxs',
                                    color='#FA282B' if (lastClose - lastOpen) <0 else '#2F9631',
                                    flex=3
                                )
                            ],
                        ),
                        BoxComponent(
                            layout='baseline',
                            spacing='none',
                            contents=[
                                TextComponent(
                                    text="建議",
                                    size='xxs',
                                    weight="bold",
                                    color='#aaaaaa',
                                    flex=1
                                ),
                                TextComponent(
                                    text="長輩買",
                                    size='xs',
                                    color='#666666',
                                    flex=3
                                )
                            ],
                        ),

                    ],
                )
            ],
        ),
    )
    return bubble


def getYoutubeBubble(url):
    bubble = BubbleContainer(
        direction='ltr',
        spacing='none',
        hero=ImageComponent(
            url=url,
            size='md',
            aspect_ratio="1:1",
            aspect_mode='cover',
            action=URIAction(label='RateBeer', uri=url),
        ),
    )
    return bubble
