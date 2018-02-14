#!/usr/bin/env python3
# @name: summarization.py
# @description: Module for metapath summarization
# @author: Núria Queralt Rosinach
# @date: 02-02-2018
# @version: 1.0
"""Module for path summarization"""

import json
import pandas as pd


def query_parser(query):
    source = query.get('source')
    target = query.get('target')
    #print('The query is {}-{}'.format(source, target))
    metapath_dict = dict()
    metapaths = list()
    entities = list()
    nodes = list()
    edges = list()
    path_idx = 0
    metapath_idx = 0
    for path in query.get('paths'):
        path_idx += 1
        nodes_list = path.get('Nodes')
        for node in nodes_list:
            node['object_order'] = nodes_list.index(node) * 2
            node['path_idx'] = path_idx
            nodes.append(node)
        edges_list = path.get('Edges')
        for edge in edges_list:
            edge['object_order'] = edges_list.index(edge) * 2 + 1
            edge['path_idx'] = path_idx
            edge['label'] = edge['preflabel']
            edge['id'] = edge['type']
            edges.append(edge)
        # metapath idx
        objects = list()
        [objects.append(object) for object_list in [nodes_list, edges_list] for object in object_list]
        #
        #metapath_list = list()
        #[metapath_list.append(object['label']) for i in range(len(objects)) for object in objects if
        # object['object_order'] == i]
        #metapath_str2 = '-'.join(metapath_list)
        #print('str2: {}'.format(metapath_str))
        #
        metapath_list = list()
        [metapath_list.append(object) for i in range(len(objects)) for object in objects if object['object_order'] == i]
        label_list = list()
        [label_list.append(object['label']) for object in metapath_list]
        metapath_str = '-'.join(label_list)
        #print('str: {}'.format(metapath_str2))
        if metapath_str not in metapath_dict:
            metapath_idx += 1
            metapath_dict[metapath_str] = metapath_idx
        path_entities_l = list()
        #for object in objects:
        for object in metapath_list:
            object['metapath_idx'] = metapath_dict[metapath_str]
        # create a uniform path object
            entity = dict()
            entity['idx'] = object['idx']
            entity['label'] = object['label']
            entity['id'] = object['id']
            entity['preflabel'] = object['preflabel']
            entity['path_idx'] = object['path_idx']
            entity['metapath_idx'] = object['metapath_idx']
            entity['object_order'] = object['object_order']
            path_entities_l.append(entity)
            entities.append(entity)
        # create metapath obj in path records
        metapath = {
            'metapath_idx': entity['metapath_idx'],
            'path_idx': entity['path_idx'],
            'label': metapath_str,
            'entities': path_entities_l,
            'length': len(path_entities_l)
        }
        metapaths.append(metapath)

    # add metapaths, entities, nodes and edges attributes
    query['metapaths'] = metapaths
    query['entities'] = entities
    query['nodes'] = nodes
    query['edges'] = edges
    print(query)

    return query


def path_load(filename):
    """This function load paths from a json file to a digital object."""
    return json.load(open('{}.json'.format(filename),'r'))


def metapath(data):
    """This function prepare metapath summary table."""
    for query in data:
        #print(query.get('source'), query.get('target'))
        df = pd.DataFrame(query.get('entities'))
    # test
        #metapath_length = df.groupby(['metapath_idx','path_idx'])['idx'].count().reset_index().groupby(['metapath_idx','idx'])['path_idx'].count().reset_index().rename(columns={'idx': 'metapath_length'})
        metapath_length = df.groupby(['metapath_idx','path_idx'])['idx'].count().reset_index().groupby(['metapath_idx','idx'])['path_idx'].count().reset_index().rename(columns={'idx': 'metapath_length', 'path_idx': 'metapath_count'})[['metapath_idx', 'metapath_length']]
        metapath_count = df.groupby(['metapath_idx','path_idx'])['idx'].count().reset_index().groupby('metapath_idx')['path_idx'].count().reset_index().rename(columns={'path_idx': 'metapath_count'})
        metapath_df = df.groupby(['metapath_idx','path_idx'])['idx'].count().reset_index().groupby(['metapath_idx','idx'])['path_idx'].count().reset_index().rename(columns={'idx': 'metapath_length', 'path_idx': 'metapath_count'})
        #print(metapath_length)
        #print(metapath_count)
        #print(metapath_df)
    # format 1
        #df['metapath_length'] = df.groupby(['metapath_idx', 'path_idx'])['object_order'].agg('count')
        #df['metapath_count'] = df.groupby('metapath_idx')['path_idx'].agg('count')
        #df['metapath_length'] = df.groupby('path_idx')['object_order'].count()
        #print(df.head(50))
        #table1 = df[['metapath_i']].copy()
    # format 2


if __name__ == "__main__":

    data = path_load('out/q1_1_in0_pwdl50_phdl20_paths')

    data_parsed = list()
    for query in data:
        query_parsed = query_parser(query)
        data_parsed.append(query_parsed)
    metapath(data_parsed)
