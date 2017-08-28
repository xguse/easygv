# -*- coding: utf-8 -*-
"""Main module."""
from logzero import logger as log

import pandas as pd

from munch import Munch, unmunchify
import ruamel.yaml as yaml

import pygraphviz as pgv

from easygv.cli.config import process_config


def update_pgv_element(element_attr_obj, attrs):
    """Update a graph element's attribute object.

    Args:
        element_attr_obj (dict-like): A graph element's attribute object.
        attrs (dict-like): A set of key/value pairs defining attribute information.

    Returns:
        None: Updates graph element in place.
    """
    try:
        element_attr_obj.update(attrs)
    except TypeError as exc:
        if "NoneType" in exc.args[0]:
            pass
        else:
            raise
    except AttributeError:
        pass


def style_the_graph(g, attrs):
    """Apply attribute discriptions in `attrs` to graph `g`.

    Args:
        g (AGraph): A pygraphviz object.
        attrs (dict-like): Attribute discriptions.

    Returns:
        None: Modifies `g` in place.
    """
    update_pgv_element(element_attr_obj=g.graph_attr,
                       attrs=attrs.graph)
    update_pgv_element(element_attr_obj=g.node_attr,
                       attrs=attrs.nodes.BASE)
    update_pgv_element(element_attr_obj=g.edge_attr,
                       attrs=attrs.edges.BASE)

    for name in g.nodes():
        n = g.get_node(name)
        try:
            kind = n.attr["node_class"]
            update_pgv_element(element_attr_obj=n.attr,
                               attrs=attrs.nodes[kind])
        except KeyError:
            pass

    for u, v in g.edges():
        e = g.get_edge(u, v)
        try:
            kind = e.attr["edge_class"]
            update_pgv_element(element_attr_obj=e.attr,
                               attrs=attrs.edges[kind])
        except KeyError:
            pass


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

    add_nodes(g=g, nodes=nodes_table)
    add_edges(g=g, edges=edges_table)

    style_the_graph(g=g, attrs=attrs)

    return g


def attr_setup(entities):
    """Return a Munch-tree of configured attributes.

    Args:
        entities (dict-like): A dict of attribute configurations and inheritences.

    Returns:
        dict-like
    """
    attrs = Munch()

    if entities is None:
        return attrs

    for name, names_attrs in entities.items():
        current = Munch()

        # which other nodes should we inherit from and in what order?
        try:
            inherits_from = names_attrs.inherits_from
            # inherit from the other nodes
            for parent in inherits_from.split(','):
                current.update(entities[parent])
                log.debug("{name} just inherited from {parent}.".format(name=name, parent=parent))
        except AttributeError:
            log.debug("{name} only inherits from BASE.".format(name=name))

        current.update(entities[name])

        attrs[name] = current

    return attrs


def process_attrs(attr_config):
    """Return attribute definition tree after applying inheritence.

    Args:
        attr_config (Path): Path to the attribute config yaml file.

    Returns:
        Munch
    """
    conf = process_config(config=attr_config)
    log.debug("state of conf:\n{conf}".format(conf=yaml.dump(unmunchify(conf), default_flow_style=False)))
    attrs = Munch()

    # Graph defaults
    try:
        graph_base = conf.GRAPH
    except AttributeError:
        graph_base = Munch()

    attrs.graph = graph_base

    # Node types
    try:
        nodes_base = conf.NODES.BASE
    except AttributeError:
        nodes_base = Munch()

    attrs.nodes = attr_setup(entities=conf.NODES.ACTUAL)
    attrs.nodes.BASE = nodes_base

    # Edge types
    try:
        edges_base = conf.EDGES.BASE
    except AttributeError:
        edges_base = Munch()

    attrs.edges = attr_setup(entities=conf.EDGES.ACTUAL)
    attrs.edges.BASE = edges_base

    return attrs
