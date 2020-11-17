cd utility\ptt_web_crawler
ptt-crawl.bat
cd ..\..\
python utility/ptt-crawl-postprocess.py
python update_vec2seq.py
python utility/routin_clean.py
rm vec2seq/sentence.ann.bak
rm vec2seq/self_sentence.ann.bak
move vec2seq/sentence.ann vec2seq/sentence.ann.bak
move vec2seq/self_sentence.ann vec2seq/self_sentence.ann.bak
move vec2seq/sentence.ann.new vec2seq/sentence.ann
move vec2seq/self_sentence.ann.new vec2seq/self_sentence.ann
