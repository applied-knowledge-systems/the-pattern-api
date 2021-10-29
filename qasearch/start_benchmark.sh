pip3 install -r requirements.txt 
pip3 install torch==1.7.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip3 install ml2rt
pip3 install git+https://github.com/RedisAI/redisai-py.git@cluster_api#egg=redisai
python3 export_load_bert.py
gears-cli run --host 127.0.0.1 --port 30001 tokeniser_gears_redisai.py --requirements requirements.txt
gears-cli run --host 127.0.0.1 --port 30001 qa_redisai_keymiss_no_cache_np.py
gears-cli run --host 127.0.0.1 --port 30001 tokeniser_gears_redisai_register.py --requirements requirements.txt
python3 transformers_plain_bert_qa.py
curl -i -H "Content-Type: application/json" -X POST -d '{"search":"Who performs viral transmission among adults"}' http://localhost:8080/qasearch 
# validate by redis cli command
# bertqa key can be found in logs docker logs -f rgcluster and attention shall be paid to port - {hashtag} is pinned to cluster shard,
# so port and hashid shall match, see export_load_bert.py
# redis-cli -c -p 30001 -h 127.0.0.1 get "bertqa{356}_PMC140314.xml:{356}:47_When air samples collected"
#redis-cli -c -p 30001 -h 127.0.0.1 get "bertqa{356}_PMC140314.xml:{356}:8_Who performs viral transmission among adults" 
# redis-cli -c -p 30003 -h 127.0.0.1 get "bertqa{8YG}_PMC302072.xml:{8YG}:10_Who performs viral transmission among adults"
# then run benchmark via docker: docker exec -it container_name  /bin/sh -c "redis-benchmark -r 10000 -n 10000 PING"
# or via command line:
# redis-benchmark -p 30003 -h 127.0.0.1 --precision 3 --csv -n 100 get "bertqa{8YG}_PMC302072.xml:{8YG}:10_Who performs viral transmission among adults"
# or without csv and precision
# redis-benchmark -p 30003 -h 127.0.0.1 -n 10 get "bertqa{8YG}_PMC302072.xml:{8YG}:10_Who performs viral transmission among adults"
#no caching 8 shards (hitting only one shard)
# Summary:
#  throughput summary: 9.22 requests per second
#  latency summary (msec):
#          avg       min       p50       p95       p99       max
#     2592.918   169.984  3000.319  3000.319  3000.319  3000.319
# laptop with i7 CPU
## any optimisations shall be put into export_load_bert.py

