import re

screwwakeupchecker = re.compile("(螺|虫累)(絲|糸糸)(醒|酉星|西星|下)(醒|酉星|西星|班)$")
def isTriggeredScrewWakeUp(str):
    return screwwakeupchecker.match(str)

fishwakeupchecker = re.compile("(鱻鱻)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredFishWakeUp(str):
    return fishwakeupchecker.match(str)

yugiohwakeupchecker = re.compile("(油|游|遊|氵斿|辶斿)(戲|䖒戈)(王|亡)(起|走已|走巳)(床|广木)(尿|尸水)(尿|尸水)$")
def isTriggeredYugiohWakeUp(str):
    return yugiohwakeupchecker.match(str)

ribwakeupchecker = re.compile("(排|扌非)(骨)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredRibWakeUp(str):
    return ribwakeupchecker.match(str)

screwerkchecker = re.compile("(螺|虫累)(絲|糸糸)(矮|矢委)(額|客頁|鵝|我鳥|我島)$")
def isTriggeredScrewErk(str):
    return screwerkchecker.match(str)

chcwakeupchecker = re.compile("(chc|CHC)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredCHCWakeUp(str):
    return chcwakeupchecker.match(str)

chcwakeup10checker = re.compile("(chc|CHC)(醒|酉星|西星)(醒|酉星|西星)(十|10)連$")
def isTriggeredCHCWakeUp10(str):
    return chcwakeup10checker.match(str)

louiswakeupchecker = re.compile("(市場)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredLouisWakeUp(str):
    return louiswakeupchecker.match(str)

explosionchecker = re.compile("(EXPLOSION|explosion)\!*$")
def isTriggeredExplosion(str):
    return explosionchecker.match(str)

abewakeupchecker = re.compile("(阿部)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredAbeWakeUp(str):
    return abewakeupchecker.match(str)

kgwakeupchecker = re.compile("(KG|kg)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredKGWakeUp(str):
    return kgwakeupchecker.match(str)

paychanwakeupchecker = re.compile("(小裴)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredPaychanWakeUp(str):
    return paychanwakeupchecker.match(str)

paychanerkchecker = re.compile("(小裴)(矮|矢委)(額|客頁|鵝|我鳥|我島)$")
def isTriggeredPaychanErk(str):
    return paychanerkchecker.match(str)

catleewakeupchecker = re.compile("(貓李)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredCatleeWakeup(str):
    return catleewakeupchecker.match(str)

todaygachachecker = re.compile("本日卡池$")
def isTriggeredTodayGacha(str):
    return todaygachachecker.match(str)

yurichecker = re.compile("真?香$")
def isTriggeredYuri(str):
    return yurichecker.match(str)

himawarichecker = re.compile(".*長輩.+")
def isTriggeredHimawari(str):
    return himawarichecker.match(str)

himawarisaychecker = re.compile("長輩名言(\d?) ([^\0]+)")
def isTriggeredHimawariSay(str):
    return himawarisaychecker.match(str)

himawarisoundchecker = re.compile("發出長輩的聲音$")
def isTriggeredHimawariSound(str):
    return himawarisoundchecker.match(str)

himawarisayrandomchecker = re.compile("長輩名言(\d?)")
def isTriggeredHimawariSayRandom(str):
    return himawarisayrandomchecker.match(str)

chcsaychecker = re.compile("CHC名言(\d?) ([^\0]+)")
def isTriggeredCHCSay(str):
    return chcsaychecker.match(str)

screwsaychecker = re.compile("螺絲名言(\d?) ([^\0]+)")
def isTriggeredScrewSay(str):
    return screwsaychecker.match(str)

wineswordgodsaychecker = re.compile("劍龍名言(\d?) ([^\0]+)")
def isTriggeredWineSwordGodSay(str):
    return wineswordgodsaychecker.match(str)

maposaychecker = re.compile("麻婆名言(\d?) ([^\0]+)")
def isTriggeredMapoSay(str):
    return maposaychecker.match(str)

paychansaychecker = re.compile("小裴名言(\d?) ([^\0]+)")
def isTriggeredPayChanSay(str):
    return paychansaychecker.match(str)

louissaychecker = re.compile("市場名言(\d?) ([^\0]+)")
def isTriggeredLouisSay(str):
    return louissaychecker.match(str)

wayfishsaychecker = re.compile("鱻鱻名言(\d?) ([^\0]+)")
def isTriggeredWayfishSay(str):
    return wayfishsaychecker.match(str)

catlesaychecker = re.compile("貓李名言(\d?) ([^\0]+)")
def isTriggeredCatleeSay(str):
    return catlesaychecker.match(str)

erasaychecker = re.compile("([^\0]+)元年$")
def isTriggeredEraSay(str):
    return erasaychecker.match(str)

ganbaruchecker = re.compile("(今天也加油|今日も一日|ZOI|ZOY)$")
def isTriggeredGanbaru(str):
    return ganbaruchecker.match(str)

jpgchecker = re.compile("([^ ]+)\.(jpg|JPG)$")
def isTriggeredjpg(str):
    return jpgchecker.match(str) and not ('http://' in str or 'https://' in str)

mp4checker = re.compile("([^ ]+)\.(mp4|MP4|avi|AVI|webm|WEBM|mkv|MKV)$")
def isTriggeredmp4(str):
    return mp4checker.match(str) and not ('http://' in str or 'https://' in str)

wineswordgodwakeupchecker = re.compile("(劍|僉刂)(龍|龖|龘)(醒|酉星|西星)(醒|酉星|西星)$")
def isTriggeredWineSwordGodWakeUp(str):
    return wineswordgodwakeupchecker.match(str)

sencompletechecker = re.compile("([^\.]+)(\.\.\.|⋯|…)$")
def isTriggeredSenComPlete(str):
    return sencompletechecker.match(str)

himawariwakeupchecker = re.compile("長輩醒醒$")
def isTriggeredHimawariWakeup(str):
    return himawariwakeupchecker.match(str)

pixivchecker = re.compile("(?:#([^#\s]+) *)+$")
pixivgrabber = re.compile("#([^#\s]+)")
def isTriggeredPixiv(str):
    return pixivchecker.match(str)
