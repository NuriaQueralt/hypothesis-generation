####
# @author: Núria Queralt Rosinach
# @date: 14-12-2017
# @version: v1 [q1_pair_paths_content]

import json
import sys
sys.path.insert(0,'/home/nuria/workspace/utils3/lib/')
from abravo_lib import add_one_dictionary2 as counter
from pprint import pprint

data = json.load(open('./out/q1_1_in0_pwdl50_phdl20_paths.tsv', 'r'))

with open('./out/q1_2_in0_pwdl50_phdl20_extended_paths.tsv','w') as f:
    f.write('source\ttarget\tnumber_of_paths\tnode_type\tnode_value\tnode_count\n')
    for pair_dct in data:
        if len(pair_dct['paths']) != 0:

            # for a pair - run all over its links and save the counts for every entity
            ortho_dct = dict()
            pheno_dct = dict()
            gene_dct = dict()
            pathway_dct = dict()
            for path_dct in pair_dct['paths']:
                ortho_node1 = str(path_dct['Nodes'][1]['preflabel']) + "::" + str(path_dct['Nodes'][1]['id'])
                pheno_node2 = str(path_dct['Nodes'][2]['preflabel']) + "::" + str(path_dct['Nodes'][2]['id'])
                ortho_node3 = str(path_dct['Nodes'][3]['preflabel']) + "::" + str(path_dct['Nodes'][3]['id'])
                gene_node4 = str(path_dct['Nodes'][4]['preflabel']) + "::" + str(path_dct['Nodes'][4]['id'])
                pathway_node5 = str(path_dct['Nodes'][5]['preflabel']) + "::" + str(path_dct['Nodes'][5]['id'])
                ortho_dct = counter(ortho_dct,ortho_node1)
                ortho_dct = counter(ortho_dct,ortho_node3)
                pheno_dct = counter(pheno_dct,pheno_node2)
                gene_dct = counter(gene_dct,gene_node4)
                pathway_dct = counter(pathway_dct,pathway_node5)

            # print entity counts summary
            for node in ortho_dct:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pair_dct['source'], pair_dct['target'], len(pair_dct['paths']), 'ortho', node, ortho_dct[node]))

            for node in pheno_dct:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pair_dct['source'], pair_dct['target'], len(pair_dct['paths']), 'pheno', node, pheno_dct[node]))

            for node in gene_dct:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pair_dct['source'], pair_dct['target'], len(pair_dct['paths']), 'gene', node, gene_dct[node]))

            for node in pathway_dct:
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pair_dct['source'], pair_dct['target'], len(pair_dct['paths']), 'phys', node, pathway_dct[node]))

        else:
            f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(pair_dct['source'], pair_dct['target'], len(pair_dct['paths']), 'NA', 'NA', str(0)))


