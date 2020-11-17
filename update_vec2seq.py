from vec2seq.Vec2Seq import Vec2Seq, updateDatabaseFromPTTRaw

if __name__ == "__main__":
    vec2seq = Vec2Seq(fasttext_path='./fasttext_model_ptt_wiki_2.magnitude',
                    fasttest_ngram_path='./fasttext_model_ptt_wiki_2_gensim.wv.vectors_ngrams.npy',
                    jieba_path='vec2seq/dict.txt.big',
                    stopword_path='vec2seq/stopwords.txt',
                    sentence_ann='vec2seq/sentence.ann',
                    self_sentent_ann='vec2seq/self_sentence.ann')
    updateDatabaseFromPTTRaw()
    vec2seq.updateAnnoy()
    print(list(set(vec2seq.searchNNSentence('看到可愛的妹子，任誰都會勃起', cascading=True))))