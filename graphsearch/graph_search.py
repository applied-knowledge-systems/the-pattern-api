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



def get_nodes(nodes):
    # FIXME: this not needed if add same functionality to edge query
    node_list=list()
    params = {'ids':nodes}
    query="""WITH $ids as ids MATCH (e:entity) where (e.id in ids) RETURN DISTINCT e.id,e.name,max(e.rank)"""
    result = redis_graph.query(query, params)
    print(query)
    # result.pretty_print()
    for record in result.result_set:
        node_list.append({'id':record[0],'name':record[1],'rank':record[2]})
    return node_list

def get_edges(nodes, years=None):
    """
    return all edges for the specified nodes
    """
    links=list()
    nodes_set=set()
    years_set=set()
    if years is not None:
        log("Graph query node params "+str(nodes))
        params = {'ids':nodes, 'years':years}
        query="""MATCH (e:entity)-[r]->(t:entity) where (e.id in $ids) and (r.year in $years) RETURN DISTINCT e.id,t.id,max(r.rank), r.year ORDER BY r.rank DESC LIMIT 400"""
    else:
        params = {'ids':nodes}
        log("Graph query node params "+str(nodes))
        query="""WITH $ids as ids MATCH (e:entity)-[r]->(t:entity) where e.id in ids RETURN DISTINCT e.id,t.id,max(r.rank), r.year ORDER BY r.rank DESC LIMIT 400"""

    result = redis_graph.query(query,params)
    result.pretty_print()
    for record in result.result_set:
        nodes_set.add(record[0])
        nodes_set.add(record[1])
        if record[3]:
            years_set.add(record[3])
        links.append({'source':record[0],'target':record[1],'rank':record[2],'created_at':str(record[3])})
    return links, list(nodes_set), list(years_set)

def get_edges_limited(nodes,limit=5):

    links=list()
    nodes_set=set()
    params = {'ids':nodes,'limit':limit}
    log("Graph query node params "+str(nodes))
    query="""WITH $ids as ids
    MATCH (e:entity)-[r]->(t:entity) where e.id in ids RETURN DISTINCT e.id,t.id,max(r.rank) as rrank, r.year ORDER BY rrank DESC LIMIT $limit"""
    result = redis_graph.query(query,params)
    # result.pretty_print()
    for record in result.result_set:
        nodes_set.add(record[0])
        nodes_set.add(record[1])
        created_at=random_date(2005,2018)
        updated_at=random_date(2017,2020)
        links.append({'source':record[0],'target':record[1],'rank':record[2],'created_at':str(created_at),'updated_at':str(updated_at)})
    return links, list(nodes_set)

if __name__ == "__main__":
    search_string="How does temperature and humidity affect the transmission of 2019-nCoV?"
    nodes=match_nodes(search_string)
    node_list=get_nodes(nodes)
    links=get_edges(nodes)
    print(node_list)
    print("---")
    print(links)

