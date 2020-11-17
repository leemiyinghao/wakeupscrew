from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import textwrap, emoji, uuid


def isEmoji(char):
    if char in emoji.UNICODE_EMOJI:
        return True
    return False

def isCJK(char):
    ranges = [
        {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},         # compatibility ideographs
        {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},         # compatibility ideographs
        {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},         # compatibility ideographs
        {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")}, # compatibility ideographs
        {"from": ord(u"\u3000"), "to": ord(u"\u3ff0")},         # Japanese Kana
        {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},         # cjk radicals supplement
        {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
        {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
        {"from": ord(u"\uff00"), "to": ord(u"\uffee")},         # Halfwidth and Fullwidth Forms 
        {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
        {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
        {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
        {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
    ]
    for _range in ranges:
        if _range['from'] <= ord(char) <= _range['to']:
            return True
    return False

class LangFont:
    def __init__(self, str, font, lang, color=(255,255,255,255)):
        self._text = str
        self.lang = lang
        self._font = font
        self._color = color
    def getSize(self):
        return self._font.getsize(self._text)
    def draw(self, draw, location):
        draw.text(tuple(location), self._text, self._color, self._font)

def TextsToLangFont(text, fontsize=144, color=(255,255,255,255), weight='regular'):
    result = []
    if weight == 'black':
        NotoEmoji = ImageFont.truetype('fonts/NotoEmoji-Regular.ttf', fontsize)
        NotoSans = ImageFont.truetype('fonts/NotoSans-Black.ttf', fontsize)
        NotoSansCJK = ImageFont.truetype('fonts/NotoSansCJK-Black.ttc', fontsize)
    elif weight == 'serif':
        NotoEmoji = ImageFont.truetype('fonts/NotoEmoji-Regular.ttf', fontsize)
        NotoSans = ImageFont.truetype('fonts/NotoSerif-Regular.ttf', fontsize)
        NotoSansCJK = ImageFont.truetype('fonts/NotoSerifCJK-Regular.ttc', fontsize)
    elif weight == 'serif_black':
        NotoEmoji = ImageFont.truetype('fonts/NotoEmoji-Regular.ttf', fontsize)
        NotoSans = ImageFont.truetype('fonts/NotoSerif-Black.ttf', fontsize)
        NotoSansCJK = ImageFont.truetype('fonts/NotoSerifCJK-Black.ttc', fontsize)
    else: # sans
        NotoEmoji = ImageFont.truetype('fonts/NotoEmoji-Regular.ttf', fontsize)
        NotoSans = ImageFont.truetype('fonts/TaipeiSansTCBeta-Regular.ttf', fontsize)
        NotoSansCJK = ImageFont.truetype('fonts/TaipeiSansTCBeta-Regular.ttf', fontsize)
    for char in text:
        font = None
        if isEmoji(char):
            font = LangFont(char, NotoEmoji, 'EMOJI', color)
        elif isCJK(char):
            font = LangFont(char, NotoSansCJK, 'CJK', color)
        else:
            font = LangFont(char, NotoSans, 'NORMAL', color)
        result.append(font)
    return result
if __name__ == '__main__':
    a = TextsToLangFont(u'ひ')
    print(a[0].lang, ord(u'ひ'), u'ひ'.encode('utf-8'))
