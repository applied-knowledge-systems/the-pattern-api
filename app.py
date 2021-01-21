#!flask/bin/python
from flask import Flask, jsonify, request,json,abort
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
from automata.utils import *

import itertools

try:
    import redis
    import config
    if app.debug:
        redis_client = redis.Redis(host=config.config()['host'],port=config.config()['port'],charset="utf-8", decode_responses=True)
    else:
        redis_client = redis.Redis(host=config.config(section='redis_local')['host'],port=config.config(section='redis_local')['port'],charset="utf-8", decode_responses=True)
except:
    log("Redis is not available ")


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
            sentence=redis_client.get(sentence_key)
            article_id=sentence_key.split(':')[1]
            title=redis_client.hget(f"article:{article_id}",'title')
            year_fetched=redis_client.hget(f"article:{article_id}",'year')
            if year_fetched:
                years_set.add(year_fetched)
        result_table.append({'title':title,'sentence':sentence,'sentencekey':sentence_key})
    else:
        result_table.append(redis_client.hgetall(f'{edge_string}'))
    
    return jsonify({'results': result_table,'years':years_set}), 200

@app.route('/gsearch', methods=['POST'])
def gsearch_task():
    """
    this search using Redis Graph to get list of nodes and links
    """
    if not request.json or not 'search' in request.json:
        abort(400)
    search_string=request.json['search']
    nodes=match_nodes(search_string)
    if 'years' in request.json:
        print("Years arrived")
        years_query=request.json['years']
        print(years_query)
        print(type(years_query))
        years_query=[int(x) for x in years_query]
    else:
        years_query=None
    
    links, node_list, years_list =get_edges(nodes,years_query)
    node_list=get_nodes(node_list)
    return jsonify({'nodes': node_list,'links': links,'years':years_list}), 200


if __name__ == "__main__":
    app.run(port=8181, host='0.0.0.0',debug=True)
