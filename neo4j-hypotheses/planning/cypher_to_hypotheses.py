####
# @author: Núria Queralt Rosinach
# @version: 01-12-2017
# trying official python client

from neo4j.v1 import GraphDatabase, basic_auth
import yaml
import json
import re
import argparse
import sys

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
        #s_pmids = edge.properties['pmids']
        #a_pmids = re.sub(".*pubmed/","",s_pmids).split(",")
        #e["pmids"] = list(map(int, a_pmids))
        out['Edges'].append(e)
    return out

# Parse and validate command line arguments
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-f", "--format", required = False, dest = "format", help = "yaml/json", default="json")
parser.add_argument("-q", "--query", required = True, dest = "query", help = "cypher query")

args = parser.parse_args()

if(args.format not in ["json","yaml","json_text"]):
   sys.stderr.write("Invalid format. Exiting.\n")
   exit()

# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "xena"))

# ask the driver object for a new session
with driver.session() as session:
    # run query
    output = list()
    sys.stderr.write("QUERY: "+args.query+"\n")
    result = session.run(args.query)
    sys.stderr.write("QUERY complete.\n")

    # parse query results
    counter = 0
    for record in result:
        path_dct = parsePath(record)
        output.append(path_dct)
        counter += 1
        if(counter%100000==0):
            sys.stderr.write("Processed "+str(counter)+"\n")

    # print output 
    if(args.format == "yaml"): 
        print(yaml.dump(output, default_flow_style=False))
    elif(args.format == "json"):
        print(json.dumps(output))
    elif(args.format == "json_text"):
        for record in output:
            print(json.dumps(record))
    else:
        sys.stderr.write("Error.\n")
