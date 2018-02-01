####
# @author: Núria Queralt Rosinach
# @date: 01-18-2018
# @version: v2
# @usage: workflow manager

import subprocess

query = "q1"

## run part 1: query cypher and retrieve paths
cmd =  "python3 {}_1_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)

## run part 2: retrieve summary tables
# metapaths
cmd =  "python3 {}_0_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)

# nodes
cmd =  "python3 {}_2_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)

# node types
cmd =  "python3 {}_3_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)

# edges
cmd =  "python3 {}_4_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)

# edge type
cmd =  "python3 {}_5_driver.py".format(query)
print(cmd)
subprocess.call(cmd, shell = True)