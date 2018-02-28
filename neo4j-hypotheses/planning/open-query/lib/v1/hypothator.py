# @name: hypothator.py
# @description: Module for hypothesis generation
# @author: Núria Queralt Rosinach
# @date: 02-24-2018
# @version: 1.0

# to dos:
#   * add check function to ensure that neo4j is up
#   * document the module
"""Module for hypothesis generation"""

from neo4j.v1 import GraphDatabase, basic_auth
#import argparse
import sys,os
import json
import yaml
import datetime
import neo4j.exceptions


# VARIABLES
today = datetime.date.today()


def parse_path( path ):
    """This function parses neo4j results."""

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


def query(genelist, queryname='', pwdegree='50', phdegree='20', format='json', port='7688'):
    """This function queries the graph database."""

    # initialize neo4j
    try:
        driver = GraphDatabase.driver("bolt://localhost:{}".format(port), auth=("neo4j", "xena"))
    except neo4j.exceptions.ServiceUnavailable:
        raise

    # query topology
    query_topology = """
    (source:GENE)-[:`RO:HOM0000020`]-(:GENE)--(ds:DISO)--(:GENE)-[:`RO:HOM0000020`]-(g1:GENE)--(pw:PHYS)--(target:GENE)
    """

    # ask the driver object for a new session
    with driver.session() as session:
        # create outdir
        if not os.path.isdir('./hypothesis'): os.makedirs('./hypothesis')
        sys.path.insert(0, '.')

        # output filename
        filename = 'query_{}_pwdl{}_phdl{}_paths_v{}'.format(queryname, pwdegree, phdegree, today)

        # run query
        outputAll = list()
        for gene1 in genelist:
            for gene2 in genelist:
                if gene2 == gene1:
                    continue
                source = gene1
                target = gene2
                #filename = 'query_source_{}_target_{}_pwdl{}_phdl{}_paths_v{}'.format(source, target, phdegree, phdegree, today)
                query = """
                MATCH path=""" + query_topology + """
                MATCH (source { id: '""" + source + """'}), (target { id: '""" + target + """'})
                // no loops or only one pass per node
                WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
                WITH g1, ds, pw, path,
                     // count animal models
                     size( (source)-[:`RO:HOM0000020`]-() ) AS source_ortho,
                     size( (g1)-[:`RO:HOM0000020`]-() ) AS other_ortho,
                     // count node degree
                     max(size( (pw)-[]-() )) AS pwDegree,
                     max(size( (ds)-[]-() )) AS dsDegree,
                     // mark general nodes to filter path that contain them out
                     [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
                     // mark promiscuous edges to filter path that contain them out,
                     [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
                // condition to filter paths that do contain marked nodes and edges out
                WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0 AND pwDegree <= """ + pwdegree + """ AND dsDegree <= """ + phdegree + """
                RETURN path
                """
                result = session.run(query)
                pair = {}
                pair['source'] = source
                pair['target'] = target
                # parse query results
                output = list()
                counter = 0
                for record in result:
                    path_dct = parse_path(record)
                    output.append(path_dct)
                    counter += 1
                    if (counter % 100000 == 0):
                        sys.stderr.write("Processed " + str(counter) + "\n")
                pair['paths'] = output
                outputAll.append(pair)

                # print output
                if (format == "yaml"):
                    print(yaml.dump(outputAll, default_flow_style=False))
                elif (format == "json"):
                    with open('./hypothesis/{}.json'.format(filename), 'w') as f:
                        json.dump(outputAll, f)
                    # print(json.dumps(outputAll))
                else:
                    sys.stderr.write("Error.\n")

    return sys.stderr.write("hypothator has finished. {} QUERIES completed.\n".format(len(output)))


if __name__ == '__main__':
    seed = list([
        'NCBIGene:55768',  # NGLY1 human gene
        'NCBIGene:358'  # AQP1 human gene
    ])
    query(seed,'ngly1_aqp1',port='7688')