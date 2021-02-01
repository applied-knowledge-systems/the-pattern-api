import redis
import config
from redisgraph import Graph

r = redis.Redis(host=config.config()['host'],port=config.config()['port'])
redis_graph = Graph('cord19medical', r)

from automata.utils import *

def match_nodes(search_string, Automata=Automata):
    if not Automata:
        Automata=loadAutomata()
    nodes=set()
    matched_ents=find_matches(search_string,Automata)
    nodes = set([node[0] for node in matched_ents])
    return list(nodes)



# def get_nodes(nodes):
#     # FIXME: this not needed if add same functionality to edge query
#     node_list=list()
#     params = {'ids':nodes}
#     query="""WITH $ids as ids MATCH (e:entity) where (e.id in ids) RETURN DISTINCT e.id,e.name,max(e.rank)"""
#     result = redis_graph.query(query, params)
#     print(query)
#     # result.pretty_print()
#     for record in result.result_set:
#         node_list.append({'id':record[0],'name':record[1],'rank':record[2]})
#     return node_list

def get_edges(nodes, years=None):
    """
    return all edges for the specified nodes, limit hardcoded
    """
    links=list()
    nodes_dict=dict()
    years_set=set()
    if years is not None:
        log("Graph query node params "+str(nodes))
        params = {'ids':nodes, 'years':years}
        query="""WITH $ids as ids MATCH (e:entity)-[r]->(t:entity) where (e.id in ids) and (r.year in $years) RETURN DISTINCT e.id,t.id,max(r.rank), r.year, e.name, t.name ORDER BY r.rank DESC LIMIT 400"""
    else:
        params = {'ids':nodes}
        log("Graph query node params "+str(nodes))
        query="""WITH $ids as ids MATCH (e:entity)-[r]->(t:entity) where e.id in ids RETURN DISTINCT e.id,t.id,max(r.rank), r.year, e.name, t.name ORDER BY r.rank DESC LIMIT 400"""

    result = redis_graph.query(query,params)
    result.pretty_print()
    for record in result.result_set:
        #FIXME: this is rather manual distinct on nodes
        nodes_dict[record[4]]=record[0]
        nodes_dict[record[5]]=record[1]
        if record[3]:
            years_set.add(record[3])
        links.append({'source':record[0],'target':record[1],'rank':record[2],'created_at':str(record[3])})
    return links, nodes_dict, list(years_set)

if __name__ == "__main__":
    search_string="How does temperature and humidity affect the transmission of 2019-nCoV?"
    nodes=match_nodes(search_string)
    node_list=get_nodes(nodes)
    links=get_edges(nodes)
    print(node_list)
    print("---")
    print(links)

