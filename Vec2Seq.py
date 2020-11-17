from annoy import AnnoyIndex
from scipy import spatial
from gensim.models import FastText, Word2Vec, KeyedVectors
import numpy as np
import logging
import json
import re
import jieba
import random
import os
import time
from vec2seq.models import Sentence, Reply, Group, db
import multiprocessing
from math import *
import datetime
import fnv
from pymagnitude import *
from utility.PTT_TMP_Models import RawArticle
import asyncio


class Vec2Seq():
    def __init__(self,
                 fasttext_path='./fasttext_model_ptt_wiki_2.magnitude',
                 fasttest_ngram_path='./fasttext_model_ptt_wiki_2_gensim.wv.vectors_ngrams.npy',
                 jieba_path='vec2seq/dict.txt.big',
                 stopword_path='vec2seq/stopwords.txt',
                 sentence_ann='vec2seq/sentence.ann',
                 self_sentent_ann='vec2seq/self_sentence.ann',
                 df_path='vec2seq/df.npy'
                 ):
        self.FASTTEXTPATH = fasttext_path
        self.FASTTEXT_NGRAMPATH = fasttest_ngram_path
        self.JIEBAPATH = jieba_path
        self.STOPWORDSPATH = stopword_path
        self.SENTENCE_ANN = sentence_ann
        self.SELF_SENTENCE_ANN = self_sentent_ann
        jieba.set_dictionary(self.JIEBAPATH)
        jieba.initialize()
        self.filterReplyNum = lambda x: len(x) >= 6
        self.AC_In_Regexp = re.compile("\[[^\]]+\].+")
        #self.fasttext_model = KeyedVectors.load(self.FASTTEXTPATH, mmap='r')
        self.fasttext_model = Magnitude(self.FASTTEXTPATH)
        #self.fasttext_model_ngram = np.load(self.FASTTEXT_NGRAMPATH, mmap_mode='r')
        self.stopword_set = set()
        self.df_table = np.load(df_path)
        with open(self.STOPWORDSPATH, 'r', encoding='utf-8') as stopwords:
            for stopword in stopwords:
                self.stopword_set.add(stopword.strip('\n'))
        self.drop = re.compile(".*\[[Ee]mail.?protected\].*|.*https?://.*|.*推.*|.*噓.*|.*高調.*|.*@.*|.*錢.*|卡|.*快樂.*|.*樓下.*|.*五樓.*|.*朝聖.*|好|圖")
        self.title_drop = re.compile(".*提名.*|.*票選.*")
        self.block_token = re.compile('\d+|\s+')

    def remove_stopwords(self, word):
        return not ((word in self.stopword_set) or (self.block_token.match(word) is not None))

    def normalized(self, vec):
        norm = np.linalg.norm(vec)
        _vec = vec if norm == 0 else vec/norm
        return _vec

    async def getSentenceVec(self, sen1):
        sen1_words = list(filter(self.remove_stopwords, jieba.lcut(sen1, cut_all=False, HMM=True)))
        sen1_arr = []
        # weight_sum = 0
        num_bucket = 10000000
        df_word_count = 2534246
        df_doc_count = 1067462
        def _hash(x): return fnv.hash(str.encode(x)) % num_bucket
        # count tf
        for i in sen1_words:
            try:
                sen1_arr.append(self.fasttext_model.query(i)*log(df_doc_count/(1 + self.df_table[_hash(i)])))
            except Exception as e:
                pass
        return np.mean(sen1_arr, axis=0)  # /weight_sum

    def ngram2Vector(self, ngram):
        id = fnv.hash(str.encode(ngram)) % self.fasttext_model_ngram.shape[0]
        return self.fasttext_model_ngram[id]

    def ngrams2Vector(self, word):
        ngrams = [c for c in word]
        word = '<' + word + '>'
        for length in range(2, len(word)):
            for ptr in range(0, len(word) - length+1):
                ngrams.append(word[ptr:ptr+length])
        vectors = [self.ngram2Vector(ngram) for ngram in ngrams]
        return np.mean(vectors, axis=0)

    async def loadAnnoy(self, path):
        annoy = AnnoyIndex(300, metric='angular')
        annoy.load(path)
        return annoy

    async def get_nns_by_vector(self, annoy, target_vec, n):
        return annoy.get_nns_by_vector(target_vec, n)

    async def searchNNSentence(self, target, cascading=False):
        '''
        annoy = AnnoyIndex(300)
        annoy.load(self.SENTENCE_ANN)
        self_annoy = AnnoyIndex(300)
        self_annoy.load(self.SELF_SENTENCE_ANN)'''

        annoy, self_annoy, target_vec = await asyncio.gather(self.loadAnnoy(self.SENTENCE_ANN), self.loadAnnoy(self.SELF_SENTENCE_ANN), self.getSentenceVec(target))
        # normal search
        _vecs = self.get_nns_by_vector(annoy, target_vec, 100)
        _self_vecs = self.get_nns_by_vector(self_annoy, target_vec, 100)
        _vecs = await self.NNfilter(annoy, self_annoy, await _vecs, await _self_vecs, target_vec, cascading)
        _replys = []
        for _vec in _vecs:
            for i in Group.select().where(Group.id == _vec[0]):
                try:
                    for reply in i.replys:
                        if len(reply.text) < 1:
                            continue
                        _replys.append([reply.text, _vec[1]])
                except Exception as e:
                    logging.exception(e)
                    pass
        annoy.unload()
        self_annoy.unload()
        if len(_replys) > 0:
            return _replys
        return None
    async def get_item_vector(self, model, i):
        return model.get_item_vector(i)
    async def NNfilter(self, model, model_self, vecs, self_vecs, target_vec, cascading=False):
        _vecs = [[]]
        threadshold = 0.95
        step = 0.1
        #bottom = 0.65
        bottom = 0.35
        self_vecs_ponishment = 0.3
        unpacked_vecs, unpacked_self_vecs = await asyncio.gather(asyncio.gather(*[self.get_item_vector(model, i) for i in vecs]), asyncio.gather(*[self.get_item_vector(model_self, i) for i in self_vecs]))
        if not cascading:
            for i in range(len(vecs)):
                _similarity = 1-spatial.distance.cosine(target_vec, unpacked_vecs[i])
                if _similarity > bottom:
                    _vecs[0].append([vecs[i], _similarity])
            for i in range(len(self_vecs)):
                _similarity = 1-spatial.distance.cosine(target_vec, unpacked_self_vecs[i]) - self_vecs_ponishment
                if _similarity > bottom:
                    _vecs[0].append([self_vecs[i], _similarity])
        else:
            _vecs = [[] for i in range(int(floor((threadshold-bottom)/step))+1)]
            for i in range(len(vecs)):
                _similarity = 1-spatial.distance.cosine(target_vec, unpacked_vecs[i])
                score = int(_similarity / step)
                if score > int(bottom/step):
                    _vecs[int(threadshold/step) - score].append([vecs[i], _similarity])
            for i in range(len(self_vecs)):
                try:
                    _similarity = 1-spatial.distance.cosine(target_vec, unpacked_self_vecs[i])
                    score = int((_similarity - self_vecs_ponishment) / step)
                    if score > int(bottom/step):
                        _vecs[int(threadshold/step) - score].append([self_vecs[i], _similarity])
                except:
                    pass
        for _inner_vecs in _vecs:
            if len(_inner_vecs) > 0:
                return _inner_vecs
        return []

    def loadSentences(self, article):
        _id = Group.create(note=article['note'], type=article['type'])
        Sentence.create(group=_id, text=article['title'])
        Sentence.create(group=_id, text=article['content'])
        for reply in article['replys']:
            Reply.create(group=_id, text=reply['text'])

    def loadQASet(self, _set):
        _id = Group.create(note='Gossiping-Chinese-Corpus', type='Gossiping_QASet')
        Sentence.create(group=_id, text=_set['question'])
        Reply.create(group=_id, text=_set['answer'])

    def updateAnnoy(self):
        annoy = AnnoyIndex(300)
        self_annoy = AnnoyIndex(300)
        i_counter = 0
        for group in Group.select():
            if i_counter % 100 == 0:
                logging.info("processed {}".format(i_counter))
            for sentence in group.sentences:
                try:
                    annoy.add_item(group.id, self.getSentenceVec(sentence.text))
                except Exception as e:
                    # logging.exception(e)
                    # logging.info(sentence.text)
                    pass
            try:
                arr = [self.getSentenceVec(reply.text) for reply in group.replys]
                self_annoy.add_item(group.id, np.mean(arr, axis=0))
            except Exception as e:
                # logging.exception(e)
                pass
            i_counter += 1
        annoy.build(50)
        annoy.save(self.SENTENCE_ANN + ".new")
        annoy.unload()
        self_annoy.build(50)
        self_annoy.save(self.SELF_SENTENCE_ANN + ".new")
        annoy.unload()

    def findNearestSet(self, reply_set, target):
        for i in range(len(reply_set)):
            if 1-spatial.distance.cosine(reply_set[i][0]['vector'], target['vector']) > 0.9:
                return i
        return -1


vec2seq = Vec2Seq()


def saveAC_InBooks(filename):
    try:
        # do bucket clustering
        data = json.load(open(filename))
        i = 0
        if 'articles' not in data:
            return
        for article in data['articles']:
            try:
                i += 1
                if vec2seq.title_drop.match(article['article_title']):
                    continue
                reply_set = []
                if 'messages' not in article:
                    continue
                for push in article['messages']:
                    if vec2seq.drop.match(push['push_content']):
                        continue
                    push_arr = {'text': push['push_content']}
                    # insert into reply_set
                    if vec2seq.AC_In_Regexp.match(push['push_content']):
                        reply_set.append([push_arr.copy(), push_arr])
                with db.atomic():
                    for _push in reply_set:
                        vec2seq.loadSentences({'title': article['article_title'], 'content': article['content'], 'replys': _push, 'note': article['url'], 'type': 'AC_In Books'})
            except Exception as e:
                logging.exception(e)
                pass
    except Exception as e:
        pass
    return True


def bucketSentenceRelation(filename, isAC_In=False):
    try:
        # do bucket clustering
        data = json.load(open(filename))
        i = 0
        if 'articles' not in data:
            return
        for article in data['articles']:
            try:
                i += 1
                if vec2seq.title_drop.match(article['article_title']):
                    continue
                reply_set = []
                if 'messages' not in article:
                    continue
                for push in article['messages']:
                    if vec2seq.drop.match(push['push_content']):
                        continue
                    push_vec = vec2seq.getSentenceVec(push['push_content'])
                    push_arr = {'text': push['push_content'], 'vector': push_vec}
                    # insert into reply_set
                    index = vec2seq.findNearestSet(reply_set, push_arr)
                    if index == -1:
                        reply_set.append([push_arr.copy(), push_arr])
                    else:
                        reply_set[index].append(push_arr)
                        reply_set[index][0]['vector'] = np.mean([i['vector'] for i in reply_set[index][1:]], axis=0)
                if not isAC_In:
                    filtered = list(filter(vec2seq.filterReplyNum, reply_set))
                else:
                    filtered = list(filter(vec2seq.filterReplyNumAndAC_In, reply_set))
                if len(filtered) > 0:
                    with db.atomic():
                        for _push in filtered:
                            vec2seq.loadSentences({'title': article['article_title'], 'content': article['content'], 'replys': _push, 'note': article['url'], 'type': article['board']})
            except Exception as e:
                pass
    except Exception as e:
        pass
    return True


def rawBucketSentenceRelation(article, isAC_In=False):
    try:
        # do bucket clustering
        try:
            if vec2seq.title_drop.match(article.title):
                return
            reply_set = []
            for push in json.loads(article.pushes):
                if vec2seq.drop.match(push['push_content']):
                    continue
                push_vec = vec2seq.getSentenceVec(push['push_content'])
                push_arr = {'text': push['push_content'], 'vector': push_vec}
                # insert into reply_set
                index = vec2seq.findNearestSet(reply_set, push_arr)
                if index == -1:
                    reply_set.append([push_arr.copy(), push_arr])
                else:
                    reply_set[index].append(push_arr)
                    reply_set[index][0]['vector'] = np.mean([i['vector'] for i in reply_set[index][1:]], axis=0)
            if not isAC_In:
                filtered = list(filter(vec2seq.filterReplyNum, reply_set))
            else:
                filtered = list(filter(vec2seq.filterReplyNumAndAC_In, reply_set))
            if len(filtered) > 0:
                for _push in filtered:
                    vec2seq.loadSentences({'title': article.title, 'content': article.content, 'replys': _push, 'note': article.id, 'type': article.board})
        except Exception as e:
            raise e
        _article = RawArticle.get(RawArticle.id == article.id)
        _article.used = True
        _article.save()
    except Exception as e:
        raise e
    return True


def updateDatabaseFromGossiping():
    logger = logging.getLogger()
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    _list = ["../Gossiping/" + _file for _file in os.listdir("../Gossiping/")]
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} articles'.format(len(_list)*50*20))
    logger.disabled = True
    for i, _ in enumerate(pool.imap_unordered(bucketSentenceRelation, _list), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/len(_list)))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromC_Chat():
    logger = logging.getLogger()
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    _list = ["../C_Chat/" + _file for _file in os.listdir("../C_Chat/")]
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} articles'.format(len(_list)*50*20))
    logger.disabled = True
    for i, _ in enumerate(pool.imap_unordered(bucketSentenceRelation, _list), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/len(_list)))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromAC_In():
    logger = logging.getLogger()
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    _list = ["../AC_In/" + _file for _file in os.listdir("../AC_In/")]
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} articles'.format(len(_list)*50*20))
    logger.disabled = True
    for i,  _ in enumerate(pool.imap_unordered(bucketSentenceRelation, _list), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/len(_list)))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromJapan_Travel():
    logger = logging.getLogger()
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    _list = ["../Japan_Travel/" + _file for _file in os.listdir("../Japan_Travel/")]
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} articles'.format(len(_list)*50*20))
    logger.disabled = True
    for i, _ in enumerate(pool.imap_unordered(bucketSentenceRelation, _list), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/len(_list)))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromAC_InBooks():
    logger = logging.getLogger()
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    _list = ["../AC_In/" + _file for _file in os.listdir("../AC_In/")]
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} articles'.format(len(_list)*50*20))
    logger.disabled = True
    for i,  _ in enumerate(pool.imap_unordered(saveAC_InBooks, _list), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/len(_list)))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromGossipingQASet():
    logger = logging.getLogger()
    logger.disabled = True
    lines = open('../../Gossiping-Chinese-Corpus/data/Gossiping-QA-Dataset.txt', 'r').readlines()
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} QASets'.format(len(lines)*50*20))
    logger.disabled = True
    step = 0
    with db.atomic():
        for line in lines:
            if step % 1000 == 0:
                logger = logging.getLogger()
                logger.disabled = False
                logger.info('done {0:%}'.format(step/len(lines)))
                logger.disabled = True
            step += 1
            try:
                question, answer = line.strip("\n").split("\t")
                if answer is not "沒有資料":
                    vec2seq.loadQASet({'question': question, 'answer': answer})
            except Exception as e:
                pass
    logger.disabled = False
    logging.info("insert done")


def updateDatabaseFromPTTRaw():
    count = RawArticle.select().where(RawArticle.used == False).count()
    logger = logging.getLogger()
    logger.disabled = False
    logger.info('processing {} PTTRaw'.format(count))
    logger.disabled = True
    pool = multiprocessing.Pool(processes=5)
    for i, _ in enumerate(pool.imap_unordered(rawBucketSentenceRelation, list(RawArticle.select().where(RawArticle.used == False))), 1):
        logger = logging.getLogger()
        logger.disabled = False
        logger.info('done {0:%}'.format(i/count))
        logger.disabled = True
    pool.close()
    pool.join()
    logger.disabled = False
    logging.info("insert done")


def ConversationTest():
    vec2seq = Vec2Seq()
    screw_say = ["你是不是輸不起"]
    for i in range(100):
        target = len(screw_say)
        cond = True
        while cond:
            target -= 1
            comp = ""
            for i in range(max(target-5, 0), target+1):
                comp += screw_say[i]
            result = vec2seq.searchNNSentence(comp, cascading=True)
            # result = searchNNSentence('sentence.ann', screw_say[target], cascading=True)
            if result is None:
                continue
            random.shuffle(result)
            for preserved in result:
                if preserved not in screw_say[-1:] or target <= 0:
                    screw_say.append(preserved)
                    cond = False
                    break
    for i in range(len(screw_say)):
        char = "A" if i % 2 == 0 else "B"
        print("{}: {}".format(char, screw_say[i]))


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    logger = logging.getLogger()
    # loadSentences('gossping_filtered')
    # loadSentences('c_chat_filtered')
    '''updateDatabaseFromAC_In()
    updateDatabaseFromGossiping()
    updateDatabaseFromC_Chat()
    updateDatabaseFromJapan_Travel()
    updateDatabaseFromAC_InBooks()
    updateDatabaseFromGossipingQASet()
    vec2seq.updateAnnoy()
    logger = logging.getLogger()
    logger.disabled = False
    logging.info('start search')'''
    # ConversationTest()
    # print(list(set(vec2seq.searchNNSentence('有沒有情人節吃什麼cp值最高的八卦', cascading=True))))
    loop = asyncio.get_event_loop()
    with open("test_set") as test_set:
        for line in test_set.readlines():
            # print(jieba.lcut(line, cut_all=False))
            try:
                print(jieba.lcut(line, cut_all=False, HMM=True), loop.run_until_complete(vec2seq.searchNNSentence(line, cascading=True)))
            except Exception as e:
                logging.exception(e)
            # fasttext_model.save('fasttext_model_wiki_ptt_dim300.model')
    logging.info('end search')
    # fasttext_model.save('fasttext_model_ptt_wiki_2_gensim')
    # print(getSentenceVec('vector'))
    # updateDatabaseFromPTTRaw()
