####
# @author: Núria Queralt Rosinach
# @date: 06-12-2017
# @version: v2 [npaths_restrictions]


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
            MATCH path=(source:GENE)-[:`RO:HOM0000020`]-(:GENE)--(ds:DISO)--(:GENE)-[:`RO:HOM0000020`]-(g1:GENE)--(pw:PHYS)--(target:GENE)
            MATCH (source { id: '""" + source + """'}), (target { id: '""" + target + """'})
            // no loops or only one pass per node
            WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
            WITH g1, ds, pw, path,
                 // count animal models
                 size( (source)-[:`RO:HOM0000020`]->() ) AS source_ortho,
                 size( (g1)-[:`RO:HOM0000020`]->() ) AS other_ortho,
                 // count node degree
                 max(size( (pw)-[]-() )) AS pwDegree,
                 max(size( (ds)-[]-() )) AS dsDegree,
                 // mark general nodes to filter path that contain them out
                 [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
                 // mark promiscuous edges to filter path that contain them out,
                 [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
            // condition to filter paths that do contain marked nodes and edges out
            WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0 AND pwDegree <= 50 AND dsDegree <= 20
            RETURN count(distinct path) AS paths, count(distinct pw) as pathways, count(distinct ds) as diseases, count( distinct source_ortho ) AS source_ortho, count( distinct other_ortho ) AS other_ortho
            ORDER BY source_ortho, other_ortho DESC
            """
            #sys.stderr.write("QUERY: "+query+"\n")
            result = session.run(query)
            #sys.stderr.write("QUERY complete.\n")
            pair = {}
            pair['source'] = source
            pair['target'] = target
            for record in result:
                pair['paths'] = record['paths']
                pair['pathways'] = record['pathways']
                pair['diseases'] = record['diseases']
                pair['source_ortho'] = record['source_ortho']
                pair['other_ortho'] = record['other_ortho']
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
    with open('./out/npaths_restrictions.tab', 'w') as f:
        f.write('source\ttarget\tpaths\tpathways\tdiseases\tsource_orthologs\tother_orthologs\n')
        for pairwise in output:
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(pairwise['source'], pairwise['target'], pairwise['paths'], pairwise['pathways'], pairwise['diseases'], pairwise['source_ortho'], pairwise['other_ortho']))
    print(len(output))



