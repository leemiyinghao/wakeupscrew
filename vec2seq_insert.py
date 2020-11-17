from annoy import AnnoyIndex
from scipy import spatial
from gensim.models import KeyedVectors
import numpy as np
import logging
import json
from vec2seq.models import *
import jieba, random
from math import floor
import re
import fnv

class Vec2Seq():
    def __init__(self):
        self.FASTTEXTPATH = 'fasttext_model_ptt_wiki_2_keyFormat'
        self.FASTTEXT_NGRAMPATH = 'fasttext_model_ptt_wiki_2_gensim.wv.vectors_ngrams.npy'
        self.JIEBAPATH = 'vec2seq/dict.txt.big'
        self.STOPWORDSPATH = 'vec2seq/stopwords.txt'
        self.SENTENCE_ANN = 'vec2seq/sentence.ann'
        self.SELF_SENTENCE_ANN = 'vec2seq/self_sentence.ann'
        jieba.set_dictionary(self.JIEBAPATH)
        jieba.initialize()
        self.fasttext_model = KeyedVectors.load(self.FASTTEXTPATH, mmap='r')
        self.stopword_set = set()
        with open(self.STOPWORDSPATH,'r', encoding='utf-8') as stopwords:
            for stopword in stopwords:
                self.stopword_set.add(stopword.strip('\n'))
        self.drop = re.compile(".*\[[Ee]mail ?protected\].*|.*https?://.*|.*推.*|.*噓.*|.*高調.*|.*@.*|.*錢.*|卡|.*生日快樂.*|.*樓下.*|.*五樓.*|.*朝聖.*|好|圖")
        self.title_drop = re.compile(".*提名.*|.*票選.*")
    def remove_stopwords(self, word):
        return not word in self.stopword_set
    def normalized(self, vec):
        norm = np.linalg.norm(vec)
        _vec = vec if norm == 0 else vec/norm
        return _vec
    def getSentenceVec(self, sen1):
        sen1_words = list(filter(self.remove_stopwords, jieba.lcut(sen1, cut_all=False, HMM=True)))
        sen1_arr = []
        weight_sum = 0
        for i in sen1_words:
            try:
                if i in self.fasttext_model.wv:
                    sen1_arr.append(self.normalized(self.fasttext_model[i])*(len(i)**0.5))
                else:
                    sen1_arr.append(self.normalized(self.ngrams2Vector(i))*(len(i)**0.5))
                weight_sum += len(i)**0.5
            except Exception as e:
                pass
            return np.mean(sen1_arr, axis=0)/weight_sum
    def ngram2Vector(self, ngram, model):
        id = fnv.hash(str.encode(ngram)) % model.shape[0]
        return model[id]
    def ngrams2Vector(self, word):
        ngrams = []
        for length in range(2, len(word)):
            ngrams.append('<' + word[:length-1])
            for ptr in range(0, len(word) - length+1):
                ngrams.append(word[ptr:ptr+length])
            ngrams.append(word[len(word) - length + 1:] + '>')
        model = np.load(self.FASTTEXT_NGRAMPATH, mmap_mode='r')
        vectors = [self.ngram2Vector(ngram, model) for ngram in ngrams]
        return np.mean(vectors)
    def searchNNSentence(self, target, cascading=False):
        annoy = AnnoyIndex(300)
        annoy.load(self.SENTENCE_ANN)
        self_annoy = AnnoyIndex(300)
        self_annoy.load(self.SELF_SENTENCE_ANN)
        # normal search
        target_vec = self.getSentenceVec(target)
        _vecs = annoy.get_nns_by_vector(target_vec, 50)
        _self_vecs = self_annoy.get_nns_by_vector(target_vec, 50)
        _vecs = self.NNfilter(annoy, self_annoy, _vecs, _self_vecs, target_vec, cascading)
        _replys = []
        for i in Sentence.select().where(Sentence.id.in_(_vecs)):
            for reply in i.replys:
                if len(reply.reply) < 1:
                    continue
                _replys.append(reply.reply)
        annoy.unload()
        self_annoy.unload()
        if len(_replys) > 0:
            return _replys
        return None
    def NNfilter(self, model, model_self, vecs, self_vecs, target_vec, cascading=False):
        _vecs = [[]]
        threadshold = 0.95
        step = 0.1
        bottom = 0.35
        self_vecs_ponishment = 0.05
        if not cascading:
            for i in range(len(vecs)):
                if 1-spatial.distance.cosine(target_vec, model.get_item_vector(vecs[i])) > threadshold:
                    _vecs[0].append(vecs[i])
            for i in range(len(self_vecs)):
                if 1-spatial.distance.cosine(target_vec, model.get_item_vector(self_vecs[i])) - self_vecs_ponishment > threadshold:
                    _vecs[0].append(self_vecs[i])
        else:
            _vecs = [[] for i in range(int(floor((threadshold-bottom)/step))+1)]
            for i in range(len(vecs)):
                score = int((1-spatial.distance.cosine(target_vec, model.get_item_vector(vecs[i]))) / step)
                if score > int(bottom/step):
                    _vecs[int(threadshold/step) - score].append(vecs[i])
            for i in range(len(self_vecs)):
                score = int((1-spatial.distance.cosine(target_vec, model.get_item_vector(self_vecs[i])) - self_vecs_ponishment) / step)
                if score > int(bottom/step):
                    _vecs[int(threadshold/step) - score].append(self_vecs[i])
        for _inner_vecs in _vecs:
            if len(_inner_vecs) > 0:
                return _inner_vecs
        return []

"""
def loadSentences(article):
    _id = Sentence.create(rawArticleTitle=article['title'], rawArticleContent=article['content'])
    for reply in article['replys']:
        Reply.create(sentence = _id, reply=reply['text'])
def updateAnnoy(filename):
    annoy = AnnoyIndex(300)
    i_counter = 0
    for sentence in Sentence.select():
        if i_counter % 100 == 0:
            logging.info("processed {}".format(i_counter))
        try:
            annoy.add_item(sentence.id, getSentenceVec(sentence.rawArticleTitle))
        except:
            pass
        try:
            annoy.add_item(sentence.id, getSentenceVec(sentence.rawArticleContent))
        except:
            pass
        try:
            text_tmp = ""
            for reply in sentence.replys:
                text.tmp += reply.reply + ","
            annoy.add_item(sentence.id, getSentenceVec(text_tmp))
        except:
            pass
        i_counter += 1
    annoy.build(1000)
    annoy.save(filename)


def findNearestSet(reply_set, target):
    for i in range(len(reply_set)):
        if 1-spatial.distance.cosine(reply_set[i][0]['vector'], target['vector']) > 0.9:
            return i
    return -1

filterReplyNum = lambda x:len(x)>=6

def bucketSentenceRelation(filename):
    try:
        #do bucket clustering
        data = json.load(open(filename))
        #multiprocessing.log_to_stderr().info("proccessing: {}, length: {}".format(filename, len(data['articles'])))
        i = 0
        output_set = []
        if not 'articles' in data:
            #multiprocessing.log_to_stderr().info('skip file ' + filename)
            return
        for article in data['articles']:
            try:
                '''if i % 1000 == 0:
                    #multiprocessing.log_to_stderr().info("processing {}".format(i))'''
                i+=1
                if title_drop.match(article['article_title']):
                    continue
                #article_vec = getSentenceVec()
                reply_set = []
                if 'messages' not in article:
                    continue
                for push in article['messages']:
                    if drop.match(push['push_content']):
                        continue
                    push_vec = getSentenceVec(push['push_content'])
                    push_arr = {'text':push['push_content'], 'vector':push_vec}
                    # insert into reply_set
                    index = findNearestSet(reply_set, push_arr)
                    if index == -1:
                        reply_set.append([push_arr.copy(), push_arr])
                    else:
                        reply_set[index].append(push_arr)
                        reply_set[index][0]['vector'] = np.mean([i['vector'] for i in reply_set[index][1:]], axis=0)
                filtered = list(filter(filterReplyNum, reply_set))
                if len(filtered) > 0:
                    with db.atomic():
                        replys = []
                        for _push in filtered:
                            loadSentences({'title':article['article_title'],'content':article['content'], 'replys':_push})
            except Exception as e:
                #multiprocessing.log_to_stderr().info(e)
                pass
        #multiprocessing.log_to_stderr().info('done with ' + filename)
    except:
        pass
    return True
"""
if __name__ == '__main__':
    logger = logging.getLogger()
    logger.disabled = False
    logging.info('start search')
    vec2seq = Vec2Seq()
    with open("test_set") as test_set:
        for line in test_set.readlines():
            print(jieba.lcut(line, cut_all=False, HMM=True), list(set(vec2seq.searchNNSentence(line, cascading=True))))
    logging.info('end search')

