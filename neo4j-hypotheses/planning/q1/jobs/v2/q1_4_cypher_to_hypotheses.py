####
# @author: Núria Queralt Rosinach
# @date: 19-01-2018
# @version: v1 [q1_pair_paths_content_node]

import json
import sys
sys.path.insert(0,'/home/nuria/workspace/utils3/lib/')
from abravo_lib import add_one_dictionary2 as counter
import argparse
import os
#from pprint import pprint


# Parse and validate command line arguments
parser = argparse.ArgumentParser(description='process user given parameters')
parser.add_argument("-i", "--input", required = True, dest = "input", help = "input path file")
parser.add_argument("-o", "--output", required = True, dest = "output", help = "output extended path file")

args = parser.parse_args()

if len(args.input) == 0:
   sys.stderr.write("Not input provided. Exiting.\n")
   exit()

if len(args.output) == 0:
   sys.stderr.write("Not output filename provided. Exiting.\n")
   exit()


# read paths
data = json.load(open('./out/{}.json'.format(args.input), 'r'))

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

# create outdir and output file
if not os.path.isdir('./out'): os.makedirs('./out')
sys.path.insert(0, '.')
with open('./out/{}.tsv'.format(args.output),'w') as f:
    f.write('source\ttarget\tnumber_of_paths\tnode_type\tnode_value\tnode_count\n')
    for pair_dct in data:
        if len(pair_dct['paths']) != 0:

            # for a pair - run all over its links and save the counts for every entity
            relations_dct = dict()
            for path_dct in pair_dct['paths']:
                rel1 = str(path_dct['Nodes'][0]['preflabel']) + "::" + str(path_dct['Nodes'][0]['id']) + "_" + str(path_dct['Edges'][0]['preflabel']) + "_" + str(path_dct['Nodes'][1]['preflabel']) + "::" + str(path_dct['Nodes'][1]['id'])
                rel2 = str(path_dct['Nodes'][1]['preflabel']) + "::" + str(path_dct['Nodes'][1]['id']) + "_" + str(path_dct['Edges'][1]['preflabel']) + "_" + str(path_dct['Nodes'][2]['preflabel']) + "::" + str(path_dct['Nodes'][2]['id'])
                rel3 = str(path_dct['Nodes'][2]['preflabel']) + "::" + str(path_dct['Nodes'][2]['id']) + "_" + str(path_dct['Edges'][2]['preflabel']) + "_" + str(path_dct['Nodes'][3]['preflabel']) + "::" + str(path_dct['Nodes'][3]['id'])
                rel4 = str(path_dct['Nodes'][3]['preflabel']) + "::" + str(path_dct['Nodes'][3]['id']) + "_" + str(path_dct['Edges'][3]['preflabel']) + "_" + str(path_dct['Nodes'][4]['preflabel']) + "::" + str(path_dct['Nodes'][4]['id'])
                rel5 = str(path_dct['Nodes'][4]['preflabel']) + "::" + str(path_dct['Nodes'][4]['id']) + "_" + str(path_dct['Edges'][4]['preflabel']) + "_" + str(path_dct['Nodes'][5]['preflabel']) + "::" + str(path_dct['Nodes'][5]['id'])
                rel6 = str(path_dct['Nodes'][5]['preflabel']) + "::" + str(path_dct['Nodes'][5]['id']) + "_" + str(path_dct['Edges'][5]['preflabel']) + "_" + str(path_dct['Nodes'][6]['preflabel']) + "::" + str(path_dct['Nodes'][6]['id'])
                relations_dct = counter(relations_dct,rel1)
                relations_dct = counter(relations_dct,rel2)
                relations_dct = counter(relations_dct,rel3)
                relations_dct = counter(relations_dct,rel4)
                relations_dct = counter(relations_dct,rel5)
                relations_dct = counter(relations_dct,rel6)

            # print entity counts summary
            for edge in relations_dct:
                f.write('{}\t{}\t{}\t{}\t{}\n'.format(seed_dct[pair_dct['source']], seed_dct[pair_dct['target']], len(pair_dct['paths']), edge, relations_dct[edge]))

        else:
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(seed_dct[pair_dct['source']], seed_dct[pair_dct['target']], len(pair_dct['paths']), 'NA', str(0)))


