####
# @author: Núria Queralt Rosinach
# @date: 12-12-2017
# @version: v1
# @usage: read in input files from data dir and run neo4j-to-hypothesis.py

import pandas as pd
import sys
import subprocess

# query
query = "q1"

# read file query rows
df = pd.read_csv('./data/{}.tsv'.format(query), header = 0, sep = '\t', keep_default_na = False)
for index, row in df.iterrows():
    # control execution flow
    if ( row.max_pathway_degree == 0 and row.max_disease_degree == 0 ):
        output_filename = "{}_in".format(query) + str(index) + "_pwdl50_phdl20_output"
        cmd = "python3 {}_cypher_to_hypotheses.py -o ".format(query) + output_filename
    elif ( row.max_pathway_degree == 0):
        output_filename = "{}_in".format(query) + str(index) + "_pwdl50_phdl" + str(row.max_disease_degree) + "_output"
        cmd = "python3 {}_cypher_to_hypotheses.py -phdl ".format(query) + str(row.max_disease_degree) + " -o " + output_filename
    elif ( row.max_disease_degree == 0 ):
        output_filename = "{}_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl20_output"
        cmd = "python3 {}_cypher_to_hypotheses.py -pwdl ".format(query) + str(row.max_pathway_degree) + " -o " + output_filename
    else:
        output_filename = "{}_in".format(query) + str(index) + "_pwdl" + str(row.max_pathway_degree) + "_phdl" + str(row.max_disease_degree) + "_output"
        cmd = "python3 {}_cypher_to_hypotheses.py -pwdl ".format(query) + str(row.max_pathway_degree) + " -phdl " + str(row.max_disease_degree) + " -o " + output_filename

    # execute cypher hypothesis generation script
    print(cmd)
    subprocess.call(cmd, shell = True)