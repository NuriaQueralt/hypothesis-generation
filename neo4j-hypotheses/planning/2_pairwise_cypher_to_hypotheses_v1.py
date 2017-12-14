####
# @author: Núria Queralt Rosinach
# @date: 01-12-2017
# @version: v1 [npaths_baseline]


from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys,os

# Core function to parse neo4j results
def parsePath( path ):
    out = {}
    out['Nodes'] = []
    for node in path['path'].nodes:
        n = {}
        n['idx'] = node.id
        n['label'] = list(node.labels)[0]
        n['id'] = node.properties['id']
        n['preflabel'] = node.properties['preflabel']
        n['description'] = node.properties['description']
        out['Nodes'].append(n)
    out['Edges'] = []
    for edge in path['path'].relationships:
        e = {}
        e['idx'] = edge.id
        e['start_node'] = edge.start
        e['end_node'] = edge.end
        e['type'] = edge.type
        e['preflabel'] = edge.properties['property_label']
        e['references'] = edge.properties['reference_uri']
        out['Edges'].append(e)
    return out

# Parse and validate command line arguments
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-f", "--format", required = False, dest = "format", help = "yaml/json", default="json")
#parser.add_argument("-q", "--query", required = True, dest = "query", help = "cypher query")

args = parser.parse_args()

if(args.format not in ["json","yaml"]):
   sys.stderr.write("Invalid format. Exiting.\n")
   exit()

# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "xena"))

# initializing start end nodes
source = ''
target = ''

# query topology
query = """
MATCH path=(source:GENE)-[:`RO:HOM0000020`]-(:GENE)--(:DISO)--(:GENE)-[:`RO:HOM0000020`]-(:GENE)--(:PHYS)--(target:GENE)
MATCH (source { id: '"""+ source +"""'}), (target { id: '"""+ target +"""'})
// no loops or only one pass per node
WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
WITH source, target, path, 
     [r IN relationships(path) | type(r)] AS types,
     // mark general nodes to filter path that contain them out
     [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
     // mark promiscuous edges to filter path that contain them out, 
     [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
// condition to filter paths that do contain marked nodes and edges out
WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0 
RETURN count(distinct path) AS paths
"""

# seed nodes to pairwise
seed = list( [
    #'OMIM:615273', # NGLY1 deficiency
    'NCBIGene:55768', # NGLY1 human gene
    'NCBIGene:358', # AQP1 human gene
    'NCBIGene:11826', # AQP1 mouse gene
    'NCBIGene:4779', # NRF1 human gene* Ginger: known as NFE2L1. http://biogps.org/#goto=genereport&id=4779
    'NCBIGene:64772', # ENGASE human gene
    'NCBIGene:360', # AQP3 human gene
    'NCBIGene:282679' # AQP11 human gene
 ] )

# ask the driver object for a new session
with driver.session() as session:
    # run query
    output = list()
    #sys.stderr.write("QUERY: "+args.query+"\n")
    #result = session.run(args.query)
    for gene1 in seed:
        for gene2 in seed:
            if gene2 == gene1:
                continue
            source=gene1
            target=gene2
            query = """
            MATCH path=(source:GENE)-[:`RO:HOM0000020`]-(:GENE)--(:DISO)--(:GENE)-[:`RO:HOM0000020`]-(:GENE)--(:PHYS)--(target:GENE)
            MATCH (source { id: '""" + source + """'}), (target { id: '""" + target + """'})
            // no loops or only one pass per node
            WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
            WITH source, target, path,
                 [r IN relationships(path) | type(r)] AS types,
                 // mark general nodes to filter path that contain them out
                 [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
                 // mark promiscuous edges to filter path that contain them out,
                 [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
            // condition to filter paths that do contain marked nodes and edges out
            WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0
            RETURN count(distinct path) AS paths
            """
            #sys.stderr.write("QUERY: "+query+"\n")
            result = session.run(query)
            #sys.stderr.write("QUERY complete.\n")
            pair = {}
            pair['source'] = source
            pair['target'] = target
            for record in result:
                pair['npaths'] = record['paths']
            output.append(pair)

            # parse query results
            #counter = 0
            #for record in result:
            #    path_dct = parsePath(record)
            #    output.append(path_dct)
            #    counter += 1
            #    if(counter%100000==0):
            #       sys.stderr.write("Processed "+str(counter)+"\n")

            # print output
            #if(args.format == "yaml"):
            #    print(yaml.dump(output, default_flow_style=False))
            #elif(args.format == "json"):
            #    print(json.dumps(output))
            #else:
            #    sys.stderr.write("Error.\n")
    if not os.path.isdir('./out'): os.makedirs('./out')
    sys.path.insert(0,'.')
    with open('./out/npaths_baseline.tab', 'w') as f:
        f.write('source\ttarget\tpaths\n')
        for pairwise in output:
            f.write('{}\t{}\t{}\n'.format(pairwise['source'], pairwise['target'], pairwise['npaths']))
    print(len(output))



