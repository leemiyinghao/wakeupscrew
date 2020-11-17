from vec2seq.Vec2Seq import Vec2Seq
from transgender.transgender import Transgender
import random

if __name__ == '__main__':
    q = "你才學店你全家都學店"
    tg = Transgender()
    vec2seq = Vec2Seq(fasttext_path='../PTT_word2vec/fasttext_model_ptt_wiki_2.magnitude',
                      fasttest_ngram_path='./fasttext_model_ptt_wiki_2_gensim.wv.vectors_ngrams.npy',
                      jieba_path='vec2seq/dict.txt.big',
                      stopword_path='vec2seq/stopwords.txt',
                      sentence_ann='vec2seq/sentence.ann',
                      self_sentent_ann='vec2seq/self_sentence.ann')
    _answer = vec2seq.searchNNSentence(q, cascading=True)
    if _answer is not None:
        _answer = random.choice(_answer)
    print(_answer)
    print(tg.answer("{}？{}".format(q, _answer)))
