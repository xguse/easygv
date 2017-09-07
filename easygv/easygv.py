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
        `None`: Updates graph element in place.

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
    """Apply attribute discriptions in ``attrs`` to graph ``g``.

    Args:
        g (AGraph): A pygraphviz object.
        attrs (dict-like): Attribute discriptions.

    Returns:
        `None`: Modifies ``g`` in place.
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

    for cluster in g.subgraphs():
        kind = cluster.graph_attr['cluster_class']
        try:
            update_pgv_element(element_attr_obj=cluster.graph_attr,
                               attrs=attrs.clusters[kind])
        except KeyError:
            pass


def load_graph_input(path):
    """Return loaded/recoded graph_input dataframes for Nodes and Edges."""
    data = Munch({name: table for name, table in pd.read_excel(io=str(path), sheetname=None).items()})

    # Do some Recoding
    for name, table in data.items():
        data[name] = table.applymap(nan_to_str)

    try:
        data.Nodes["cluster_name"] = data.Nodes["cluster_name"].apply(lambda name: "cluster_{name}".format(name=name))
        data.Clusters["name"] = data.Clusters["name"].apply(lambda name: "cluster_{name}".format(name=name))
    except KeyError:
        pass

    return data


def nan_to_str(x):
    """Return empty string if pd.isnull(x): x otherwise."""
    if pd.isnull(x):
        return ''
    else:
        return x


def add_clusters(g, nodes, clusters):
    """Add clusters to the graph in place."""
    clusters_ = clusters.merge(right=nodes[["name", "cluster_name"]],
                               how='inner',
                               left_on='name', right_on='cluster_name',
                               suffixes=('_cluster', '_node'))[["label", "cluster_class", "name_node", "cluster_name"]]

    clustered_nodes = clusters_.groupby(["label", "cluster_class", "cluster_name"]).name_node.apply(lambda x: list(x.unique())).to_dict()

    for key, nodes in clustered_nodes.items():
        label = key[0]
        cluster_class = key[1]
        name = key[2]

        g.add_subgraph(nbunch=nodes, label=label, cluster_class=cluster_class, name=name)


def add_nodes(g, nodes):
    """Add nodes to the graph in place."""
    nodes.apply(lambda n: g.add_node(n['name'],
                                     label=n["label"],
                                     node_class=n["node_class"]),
                axis=1)


def add_edges(g, edges):
    """Add edges to the graph in place."""
    edges.apply(lambda e: g.add_edge(u=e['u_name'], v=e['v_name'], label=e['label'], edge_class=e["edge_class"]),
                axis=1)


def build_graph(graph_input, attrs):
    """Init the pygraphviz object and apply the sub-functions to assemble and style the graph.

    Args:
        graph_input (dict-like): the output from ``load_graph_input``.
        attrs (dict-like): the output from ``process_attrs``.

    Returns:
        pygraphviz.AGraph: The assembled and styled graph.
    """
    g = pgv.AGraph(thing=None, filename=None,
                   data=None, string=None,
                   handle=None, name=None,
                   strict=True, directed=True)

    add_nodes(g=g, nodes=graph_input.Nodes)
    add_edges(g=g, edges=graph_input.Edges)

    if 'cluster_name' in graph_input.Nodes.columns.values:
        add_clusters(g=g, nodes=graph_input.Nodes, clusters=graph_input.Clusters)

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

    not_graph = set(conf.keys()) - set(['GRAPH'])

    for name in not_graph:
        tree = conf[name]

        try:
            base = tree.BASE
        except AttributeError:
            base = Munch()

        attr_type = name.lower()
        attrs[attr_type] = attr_setup(entities=tree.ACTUAL)
        attrs[attr_type].BASE = base

    return attrs
