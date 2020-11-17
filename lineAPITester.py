
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
    SeparatorComponent, QuickReply, QuickReplyButton, VideoSendMessage
)
from GetPixiv import *
from FlexBubble import *

if __name__ == "__main__":
    bubbles = []
    for i in range(5):
        thumb, url, originimage, meta = getGUMIImage()
        bubble = getStandradPixivBubble(url, thumb, originimage, meta, "CHC醒醒")
        bubbles.append(bubble)
    arg = {
            'contents': bubbles
    }
    print(CarouselContainer(**arg))
    print(FlexSendMessage(alt_text="123", contents=bubbles[0]))
