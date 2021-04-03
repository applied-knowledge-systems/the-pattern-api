#!flask/bin/python
from flask import Flask, jsonify, request,json,abort
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from automata.utils import *

import itertools
import config

try:
    import redis
    redis_client = redis.Redis(host=config.config(section='redis')['host'],port=config.config(section='redis')['port'],charset="utf-8", decode_responses=True)

except:
    log("Redis is not available ")

try: 
    from rediscluster import RedisCluster
    rc_list=json.loads(config.config(section='rediscluster_docker')['rediscluster'])
    rediscluster_client = RedisCluster(startup_nodes=rc_list, decode_responses=True)
except:
    log("RedisCluster is not available")

from graphsearch.graph_search import * 

@app.route('/')
def index():
    return "Sample server, use RedisGraph instead if available"

@app.route('/edge/<edge_string>')
def get_edgeinfo(edge_string):
    """
    Tested with edges:C5162902:C5190121
    """
    log("Edge string "+edge_string)
    years_set=set()
    edges_query=remove_prefix(edge_string,'edges:')
    result_table=[]
    edge_scored=redis_client.zrangebyscore(f"edges_scored:{edges_query}",'-inf','inf',0,5)
    if edge_scored:
        for sentence_key in edge_scored:
            *head,tail=sentence_key.split(':')
            sentence=rediscluster_client.hget(":".join(head),tail)
            article_id=head[1]
            title=redis_client.hget(f"article_id:{article_id}",'title')
            year_fetched=redis_client.hget(f"article_id:{article_id}",'year')
            if year_fetched:
                years_set.add(year_fetched)
            result_table.append({'title':title,'sentence':sentence,'sentencekey':sentence_key})
    else:
        result_table.append(redis_client.hgetall(f'{edge_string}'))
    
    return jsonify({'results': result_table,'years':list(years_set)}), 200

@app.route('/gsearch', methods=['POST'])
def gsearch_task():
    """
    this search using Redis Graph to get list of nodes and links
    """
    if not request.json or not 'search' in request.json:
        abort(400)
    search_string=request.json['search']
    nodes=match_nodes(search_string)
    node_list=get_nodes(nodes)
    print(node_list)
    if 'years' in request.json:
        print("Years arrived")
        years_query=request.json['years']
        print(years_query)
        print(type(years_query))
        years_query=[int(x) for x in years_query]
    else:
        years_query=None
    
    links, node_dict, years_list =get_edges(nodes,years_query)
    print(node_dict)
    #FIXME: flatten hash into list for JSON: can be served out of redis hget
    node_list=[{'name':k,'id':node_dict[k]['id'],'rank':node_dict[k]['rank']} for k in node_dict]
    return jsonify({'nodes': node_list,'links': links,'years':years_list}), 200

# from qasearch.qa_bert import *
# @app.route('/qasearch', methods=['POST'])
# def qasearch_task():
#     """
#     this search using Redis Graph to get list of articles and sentences and then calls BERT QA model to create answer
#     TODO: pre-process articles with qa tokeniser 
#     """
     

#     if not request.json or not 'search' in request.json:
#         abort(400)
#     question=request.json['search']
#     nodes=match_nodes(question)
#     links,_,_=get_edges(nodes)
#     result_table=[]
#     for each_record in links[0:5]:  
#         edge_query=each_record['source']+":"+each_record['target'] 
#         print(edge_query)
#         edge_scored=redis_client.zrangebyscore(f"edges_scored:{edge_query}",'-inf','inf',0,5)
#         if edge_scored:
#             for sentence_key in edge_scored:
#                 *head,tail=sentence_key.split(':')
#                 sentence=rediscluster_client.hget(":".join(head),tail)
#                 article_id=head[1]
#                 title=redis_client.hget(f"article_id:{article_id}",'title')
#                 hash_tag=head[-1]
#                 answer=qa(question,sentence,hash_tag)
#             result_table.append({'title':title,'sentence':sentence,'sentencekey':sentence_key,'answer':answer})        

#     return jsonify({'links': links,'results':result_table}), 200


if __name__ == "__main__":
    app.run(port=8181, host='0.0.0.0',debug=True)

