from numpy.random import choice
import random
from transgender.transgender import Transgender
from vec2seq.Vec2Seq import Vec2Seq
import json
from tqdm import tqdm
import time

TG = Transgender()
vec2seq = Vec2Seq(fasttext_path='./fasttext_model_ptt_wiki_2.magnitude',
                  fasttest_ngram_path='./fasttext_model_ptt_wiki_2_gensim.wv.vectors_ngrams.npy',
                  jieba_path='vec2seq/dict.txt.big',
                  stopword_path='vec2seq/stopwords.txt',
                  sentence_ann='vec2seq/sentence.ann',
                  self_sentent_ann='vec2seq/self_sentence.ann')

replys = ["心愛腳臭"]
for i in tqdm(range(1000)):
    v_answer = None
    keyword = replys[-1]
    try:
        v_answer = vec2seq.searchNNSentence(keyword, cascading=False)
    except:
        pass
    if v_answer is not None:
        r_answer = choice([_v[0] for _v in v_answer], 1, [10**(_v[1]*10) for _v in v_answer])
        triggerTransgender = random.random() > float(sum([10**(_v[1]*10) for _v in v_answer]))/(float(sum([10**(_v[1]*10) for _v in v_answer])+(10**6.5)))
    else:
        triggerTransgender = True
        r_answer = ""
    if triggerTransgender:
        result = TG.answer(keyword)
    else:
        result = r_answer[0]
    if not result == None:
        replys.append(result)
    else:
        replys.append('阿哈哈，螺絲不知道')
json.dump(replys, open("auto_chat{}.json".format(int(time.time())), 'w'), ensure_ascii=False)