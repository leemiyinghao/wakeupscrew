cd utility/ptt_web_crawler
sh ptt-crawl.sh
cd ../../
python3 utility/ptt-crawl-postprocess.py
python3 update_vec2seq.py
python3 utility/routin_clean.py
rm vec2seq/sentence.ann.bak
rm vec2seq/self_sentence.ann.bak
mv vec2seq/sentence.ann vec2seq/sentence.ann.bak
mv vec2seq/self_sentence.ann vec2seq/self_sentence.ann.bak
mv vec2seq/sentence.ann.new vec2seq/sentence.ann
mv vec2seq/self_sentence.ann.new vec2seq/self_sentence.ann
touch reload.txt
