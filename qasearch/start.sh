pip3 install -r requirements.txt 
pip3 install torch==1.9.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip3 install ml2rt
pip3 install git+https://github.com/RedisAI/redisai-py.git@cluster_api#egg=redisai
python3 export_load_bert.py
gears-cli run --host 127.0.0.1 --port 30001 tokeniser_gears_redisai.py --requirements requirements.txt
gears-cli run --host 127.0.0.1 --port 30001 qa_redisai_gear_map_keymiss_np.py
gears-cli run --host 127.0.0.1 --port 30001 tokeniser_gears_redisai_register.py --requirements requirements.txt
curl -i -H "Content-Type: application/json" -X POST -d '{"search":"Who performs viral transmission among adults"}' http://localhost:8080/qasearch 
# validate by redis-cli -c -p 30001 -h 127.0.0.1 get "bertqa{5M5}_PMC140314.xml:{5M5}:44_When air samples collected?"
