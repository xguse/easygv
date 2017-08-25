# -*- coding: utf-8 -*-
"""Main module."""
from logzero import logger as log

import pandas as pd

import pygraphviz as pgv

from easygv.cli.config import process_config


def style_the_graph(g, attrs):
    for name in g.nodes():
        n = g.get_node(name)
        kind = n.attr["node_class"]
        n.attr.update(attrs.NODES[kind])


def load_graph_input(path):
    data = pd.read_excel(io=str(path), sheetname=None)
    return data


def add_nodes(g, nodes):
    nodes.apply(lambda n: g.add_node(n['name'],
                                     label=n["label"],
                                     node_class=n["node_class"]),
                axis=1)


def add_edges(g, edges):
    edges.apply(lambda e: g.add_edge(u=e['u_name'], v=e['v_name']),
                axis=1)


def build_graph(graph_input, attrs):
    nodes_table = graph_input['Nodes']
    edges_table = graph_input['Edges']

    g = pgv.AGraph(thing=None, filename=None,
                   data=None, string=None,
                   handle=None, name=None,
                   strict=True, directed=True)

    g.node_attr.update(attrs.NODES.BASE)
    add_nodes(g=g, nodes=nodes_table)
    add_edges(g=g, edges=edges_table)

    style_the_graph(g=g, attrs=attrs)

    return g


def process_attrs(attr_config):
    #######
    # TODO: add the updating cascade that allows attr inheritance
    #       - a note on this item
    #######
    return process_config(config=attr_config)
