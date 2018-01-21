####
# @author: Núria Queralt Rosinach
# @date: 19-01-2018
# @version: v1
# @usage: read path files from out dir and run q1_3_cypher_to_hypotheses.py to get extended hypotheses information for each pair

import pandas as pd
import subprocess

# query
query = "q1"

# read file query rows
df = pd.read_csv('./data/{}_1.tsv'.format(query), header = 0, sep = '\t', keep_default_na = False)
for index, row in df.iterrows():
    # control execution flow
    if ( row.max_pathway_degree == 0 and row.max_disease_degree == 0 ):
        input_filename = "{}_1_in".format(query) + str(index) + "_pwdl50_phdl20_paths"
        output_filename = "{}_2_in".format(query) + str(index) + "_pwdl50_phdl20_extended_paths_node_types"
    elif ( row.max_pathway_degree == 0):
        input_filename = "{}_1_in".format(query) + str(index) + "_pwdl50_phdl" + str(row.max_disease_degree) + "_paths"
        output_filename = "{}_2_in".format(query) + str(index) + "_pwdl50_phdl" + str(row.max_disease_degree) + "_extended_paths_node_types"
    elif ( row.max_disease_degree == 0 ):
        input_filename = "{}_1_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl20_paths"
        output_filename = "{}_2_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl20_extended_paths_node_types"
    else:
        input_filename = "{}_1_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl" + str(row.max_disease_degree) + "_paths"
        output_filename = "{}_2_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl" + str(row.max_disease_degree) + "_extended_paths_node_types"

    cmd = "python3 {}_3_cypher_to_hypotheses.py -i ".format(query) + input_filename + " -o " + output_filename

    # execute cypher hypothesis generation script
    print(cmd)
    subprocess.call(cmd, shell = True)