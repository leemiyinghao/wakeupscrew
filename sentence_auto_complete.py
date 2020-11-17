import jieba, re
from SenComPlete.models import *

def addSentence(sentence):
    if len(sentence) < 4:
        #print(len(sentence))
        return
    sentenceObj = Sentence.create(text=sentence)
    subSentences = re.split(',|，|。|\.\.\.|！|？|\!|\?', sentence)
    subSentenceCounter = 0
    for subSentence in subSentences:
        if len(subSentence) < 1:
            continue
        #print(subSentence, len(subSentence))
        subSentenceObj = SubSentence.create(text=subSentence, sentence=sentenceObj, location=subSentenceCounter)
        subSentenceCounter += 1
        words = jieba.lcut(subSentence)
        wordCounter = 0
        for word in words:
            Word.create(sub_sentence=subSentenceObj, location=wordCounter, text=word, length=len(word))
            wordCounter += 1

def min_with_index(arr):
    _min = arr[-1]
    _index = len(arr)-1
    for i in reversed(range(len(arr))):
        #print(_min, _index)
        if arr[i] < _min and not (arr[i]==0 and i==0):
            _min = arr[i]
            _index = i
    return _min, _index

def compareSentence(sen1, sen2):
    # modified Levenshtein Distance
    sen1 = ' ' + sen1
    sen2 = ' ' + sen2
    matrix = [[0 for j in range(len(sen2))] for i in range(len(sen1))]
    for i in range(len(sen1)):
        matrix[i][0] = i
    for j in range(len(sen2)):
        matrix[0][j] = j
    for i in range(len(sen1)):
        for j in range(len(sen2)):
            cost = 0
            if not sen1[i] == sen2[j]:
                cost = 1
            matrix[i][j] = min([matrix[i-1][j] + 1, matrix[i][j-1] + 1, matrix[i-1][j-1] + cost])
    similarity, end_loc = min_with_index(matrix[-1][1:])
    if end_loc > 0:
        similarity = 1 - (similarity / end_loc)
        return similarity, end_loc
    else:
        return 0.0,0
def searchSentence(sentence):
    sentence = re.split(',|，|。|\.\.\.|！|？|\!|\?', sentence)[-1]
    words = jieba.lcut(sentence)
    #_words = (Word.select().join(SubSentence, on=(Word.sub_sentence==SubSentence.id)).where(Word.text.in_(words)))
    SubSentence_query = (SubSentence.select(Word.sub_sentence.alias('sub_sentence'), fn.SUM(Word.length).alias('length')).join(Word).where(Word.text.in_(words)).group_by(Word.sub_sentence).order_by(SQL('length').desc())).dicts()
    ids = []
    for query in SubSentence_query:
        if query['length'] < 2:
            break
        ids.append(query['sub_sentence'])
    subSentences = SubSentence.select().where(SubSentence.id.in_(ids))
    for subSentence in subSentences:
        similarity, ends = compareSentence(sentence, subSentence.text)
        #print(similarity, ends, subSentence.text)
        if (min(len(sentence),ends)<4 and similarity < 0.9) or (min(len(sentence),ends) >= 4 and similarity < 0.55) or ends < 1:
            #print(subSentence.text, similarity, ends)
            continue
        if ends + 3 > len(subSentence.text):
            nextSubSentences = SubSentence.select().where((SubSentence.sentence == subSentence.sentence) & (SubSentence.location > subSentence.location)).order_by(SubSentence.location)
            if len(nextSubSentences) < 1:
                continue
            print(nextSubSentences.get().sentence, subSentence.sentence)
            return nextSubSentences.get().text
        else:
            return subSentence.text[ends+1:]
    return None

if __name__ == '__main__':
#    with open('sentence.list', 'r+') as file:
#        for line in file.readlines():
#            line = line.replace("\r", "").replace("\n", "")
#            print(line)
#            addSentence(line)
#print(jieba.lcut_for_search("何…だと…"))
#print(jieba.lcut_for_search("我有○○我超強的喔喔喔~！"))
#print(jieba.lcut_for_search("咕嚕靈波（○′∀‵）ノ♡"))
#print(jieba.lcut_for_search("左舷、弾幕薄いぞ！何やってんの！"))
#addSentence("○○和●●是不同的，和●●！")
    print('這隻竹鼠中暑了', searchSentence('這隻竹鼠中暑了'))
    print('683T', searchSentence('683T'))
    print('正面', searchSentence('正面'))
    print('你怎麼', searchSentence('你怎麼'))
#print(compareSentence('寬恕是他們', '恕是他們與上帝的事'))
