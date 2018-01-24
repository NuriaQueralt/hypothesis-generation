####
# @author: Núria Queralt Rosinach
# @date: 22-01-2018
# @version: v1 [q1_metapaths]


from neo4j.v1 import GraphDatabase, basic_auth
import argparse
import sys,os
import json
import yaml

# Parse and validate command line arguments
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-pwdl", "--pathwayDegreeLimit", required = False, dest = "pwDegree", help = "maximum node degree for pathway type nodes (default = 50)", default = "50")
parser.add_argument("-phdl", "--phenotypeDegreeLimit", required = False, dest = "phDegree", help = "maximum node degree for phenotype type nodes (default = 20)", default = "20")
parser.add_argument("-o", "--output", required = True, dest = "output", help = "tab output format")

args = parser.parse_args()

# initialize neo4j
driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "xena")) # NEW GRAPH
#driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "xena"))

# dict of seed nodes with label::ID
seed_dct = {
    'OMIM:615273': 'NGLY1-deficiency::OMIM:615273', # NGLY1 deficiency
    'CHEBI:506227': 'N-acetyl-D-glucosamine|GlcNAc::CHEBI:506227', # GlcNAc
    'NCBIGene:55768': 'NGLY1::NCBIGene:55768',  # NGLY1 human gene
    'NCBIGene:358': 'AQP1::NCBIGene:358',  # AQP1 human gene
    'NCBIGene:11826': 'Aqp1::NCBIGene:11826',  # AQP1 mouse gene
    'NCBIGene:4779': 'NFE2L1::NCBIGene:4779',  # NRF1 human gene* Ginger: known as NFE2L1. http://biogps.org/#goto=genereport&id=4779
    'NCBIGene:64772': 'ENGASE::NCBIGene:64772',  # ENGASE human gene
    'NCBIGene:360': 'AQP3::NCBIGene:360',  # AQP3 human gene
    'NCBIGene:282679': 'AQP11::NCBIGene:282679'  # AQP11 human gene
}

# seed nodes to pairwise
seed = list( [
    #'OMIM:615273', # NGLY1 deficiency
    #'CHEBI:506227', # GlcNAc
    'NCBIGene:55768', # NGLY1 human gene
    'NCBIGene:358', # AQP1 human gene
    'NCBIGene:11826', # AQP1 mouse gene
    'NCBIGene:4779', # NRF1 human gene* Ginger: known as NFE2L1. http://biogps.org/#goto=genereport&id=4779
    'NCBIGene:64772', # ENGASE human gene
    'NCBIGene:360', # AQP3 human gene
    'NCBIGene:282679' # AQP11 human gene
 ] )

# query topology
query_topology = """
(source:GENE)-[r1:`RO:HOM0000020`]-(n2:GENE)-[r2]-(n3:DISO)-[r3]-(n4:GENE)-[r4:`RO:HOM0000020`]-(n5:GENE)-[r5]-(n6:PHYS)-[r6]-(target:GENE)
"""

# ask the driver object for a new session
with driver.session() as session:
    # create outdir
    if not os.path.isdir('./out'): os.makedirs('./out')
    sys.path.insert(0,'.')

    # create outdir and output file
    if not os.path.isdir('./out'): os.makedirs('./out')
    sys.path.insert(0,'.')
    with open('./out/{}.tsv'.format(args.output), 'w') as f:
        f.write('source\ttarget\tpaths_count\trelation_1\tnode_2\trelation_2\tnode_3\trelation_3\tnode_4\trelation_4\tnode_5\trelation_5\tnode_6\trelation_6\tmetapaths_count\n')

        # run query
        output = list()
        for gene1 in seed:
            for gene2 in seed:
                if gene2 == gene1:
                    continue
                source=gene1
                target=gene2
                query1 = """
                MATCH path=""" + query_topology + """
                MATCH (source { id: '""" + source + """'}), (target { id: '""" + target + """'})
                // no loops or only one pass per node
                WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
                WITH n3, n6, path,
                     // count node degree
                     max(size( (n6)-[]-() )) AS pwDegree,
                     max(size( (n3)-[]-() )) AS dsDegree,
                     // mark general nodes to filter path that contain them out
                     [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
                     // mark promiscuous edges to filter path that contain them out,
                     [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
                // condition to filter paths that do contain marked nodes and edges out
                WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0 AND pwDegree <= """ + args.pwDegree + """ AND dsDegree <= """ + args.phDegree + """
                RETURN count(distinct path) AS paths
                """
                result = session.run(query1)
                pair = {}
                pair['source'] = source
                pair['target'] = target
                for record in result:
                    pair['paths'] = record['paths']

                query2 = """
                MATCH path=""" + query_topology + """
                MATCH (source { id: '""" + source + """'}), (target { id: '""" + target + """'})
                // no loops or only one pass per node
                WHERE ALL(x IN nodes(path) WHERE single(y IN nodes(path) WHERE y = x))
                WITH r1, n2, r2, n3, r3, n4, r4, n5, r5, n6, r6, path,
                     // count node degree
                     max(size( (n6)-[]-() )) AS pwDegree,
                     max(size( (n3)-[]-() )) AS dsDegree,
                     // mark general nodes to filter path that contain them out
                     [n IN nodes(path) WHERE n.preflabel IN ['cytoplasm','cytosol','nucleus','metabolism','membrane','protein binding','visible','viable','phenotype']] AS nodes_marked,
                     // mark promiscuous edges to filter path that contain them out,
                     [r IN relationships(path) WHERE r.property_label IN ['interacts with','in paralogy relationship with','in orthology relationship with','colocalizes with']] AS edges_marked
                // condition to filter paths that do contain marked nodes and edges out
                WHERE size(nodes_marked) = 0 AND size(edges_marked) = 0 AND pwDegree <= """ + args.pwDegree + """ AND dsDegree <= """ + args.phDegree + """
                RETURN distinct r1.property_label as r1,labels(n2) as n2, r2.property_label as r2, labels(n3) as n3,r3.property_label as r3,labels(n4) as n4,r4.property_label as r4,labels(n5) as n5,r5.property_label as r5,labels(n6) as n6,r6.property_label as r6, count(*) as counts
                order by counts desc
                """
                result = session.run(query2)
                for record in result:
                    pair['r1'] = record['r1']
                    pair['n2'] = record['n2']
                    pair['r2'] = record['r2']
                    pair['n3'] = record['n3']
                    pair['r3'] = record['r3']
                    pair['n4'] = record['n4']
                    pair['r4'] = record['r4']
                    pair['n5'] = record['n5']
                    pair['r5'] = record['r5']
                    pair['n6'] = record['n6']
                    pair['r6'] = record['r6']
                    pair['metapaths'] = record['counts']

                    if not pair['paths']:
                        f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(seed_dct[pair['source']],
                                                                                                  seed_dct[pair['target']],
                                                                                                  pair['paths'], None,
                                                                                                  None, None,
                                                                                                  None, None,
                                                                                                  None, None,
                                                                                                  None, None,
                                                                                                  None, None,
                                                                                                  None))
                    else:
                        f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(seed_dct[pair['source']],
                                                                                                  seed_dct[pair['target']],
                                                                                                  pair['paths'], pair['r1'],
                                                                                                  pair['n2'], pair['r2'],
                                                                                                  pair['n3'], pair['r3'],
                                                                                                  pair['n4'], pair['r4'],
                                                                                                  pair['n5'], pair['r5'],
                                                                                                  pair['n6'], pair['r6'],
                                                                                                  pair['metapaths']))

                output.append(pair)

sys.stderr.write("{} QUERIES completed.\n".format(len(output)*2))

