#!/usr/bin/env python
"""Provide command line interface to easygv."""

# Imports
import logzero
from logzero import logger as log

import os
from pathlib import Path
import appdirs


from munch import Munch

import click

import graphviz as gv

from easygv.cli import config as _config
from easygv import easygv


# Metadata
__author__ = "Gus Dunn"
__email__ = "w.gus.dunn@gmail.com"

FACTORY_RESETS = (Path(os.path.realpath(__file__)).parent / 'factory_resets/').resolve()
USER_CONFIG_DIR = Path(appdirs.user_config_dir())
USER_APP_DIR = USER_CONFIG_DIR / 'easygv'


verbosity_levels = {'debug': 10,
                    'normal': 20,
                    'quiet': 30}

# logzero.loglevel(0)
# log.debug('debug')
# log.info('info')
# log.warning('warning')
# log.error('error')


@click.group()
@click.option('-v', '--verbosity',
              type=click.Choice(verbosity_levels.keys()),
              help="How much do you want to know about what I am doing?",
              show_default=True,
              default='normal')
@click.pass_context
def main(ctx=None, verbosity=None):
    """Command interface to easygv.

    Define nodes and edges in an excel file and graph-style attributes in a yaml file with inheritence.

    For command specific help text, call the specific
    command followed by the --help option.
    """
    ctx.obj = Munch()

    # NOTE: Not sure I need to store this or just set it here.
    ctx.obj.LOGLVL = verbosity_levels[verbosity]

    logzero.loglevel(level=ctx.obj.LOGLVL, update_custom_handlers=True)
    log.debug("loglevel set at: {lvl}".format(lvl=ctx.obj.LOGLVL))


@main.command()
@click.option('-g', '--generate-config',
              is_flag=True,
              help="Copy one or more of the 'factory default' config files to the users "
              "config directory ({user_config_dir}). Back ups will be made of any existing config files.".format(user_config_dir=USER_APP_DIR),
              show_default=True,
              default=False)
@click.option('-k', '--kind',
              type=click.Choice(['attrs']),
              help="Which type of config should we replace?",
              show_default=True,
              default='attrs')
@click.option('-p', '--prefix',
              type=click.STRING,
              help="""A prefix to identify the new config file(s).""",
              show_default=True,
              default=None)
@click.pass_context
def config(ctx, generate_config, kind, prefix):
    """Manage configuration values and files."""
    factory_resets = FACTORY_RESETS
    default_files = {"attrs": factory_resets / 'attrs.yaml'}

    if generate_config:
        if kind == 'all':
            for p in default_files['all']:
                _config.replace_config(name=p.name,
                                       factory_resets=factory_resets,
                                       user_conf_dir=USER_APP_DIR,
                                       prefix=prefix)
        else:
            p = default_files[kind]
            _config.replace_config(name=p.name,
                                   factory_resets=factory_resets,
                                   user_conf_dir=USER_APP_DIR,
                                   prefix=prefix)


draw_formats = ['all', 'pdf', 'png', 'svg']
draw_layouts = ["dot", "neato", "fdp", "sfdp", "twopi", "circo"]


@main.command('draw', short_help='Draw and save your graph.')
@click.option('-f', '--formats',
              type=click.Choice(draw_formats),
              help="Which type of format should we produce?",
              show_default=True,
              default='all')
@click.option('-d', '--directory',
              type=click.Path(exists=True, file_okay=False),
              help="""Path to a directory to write out the files.""",
              show_default=True,
              default=None)
@click.option('-n', '--name',
              type=click.STRING,
              help="""A name for your figure.""",
              show_default=True,
              default=None)
@click.option('-l', '--layout',
              type=click.Choice(draw_layouts),
              help="""Which layout program?""",
              show_default=True,
              default='dot')
@click.argument('definition', type=click.Path(exists=True, dir_okay=False))
@click.argument('attr_config', type=click.Path(exists=True, dir_okay=False))
@click.pass_context
def draw(ctx, formats, directory, name, layout, definition, attr_config):
    """Produce your graph and save results based on your input.

    \b
    DEFINITION  = Excel file containing the definition of your nodes and edges
    ATTR_CONFIG = YAML file containing the attribute information for your
                  graph, node-, and edge-types
    """
    log.info("Preparing your graph.")
    directory = Path(directory)
    definition = Path(definition)
    attr_config = Path(attr_config)

    if name is None:
        name = 'easygv'

    if formats == 'all':
        formats = draw_formats[1:]
    else:
        formats = [formats]

    graph_input = easygv.load_graph_input(path=definition)

    attrs = easygv.process_attrs(attr_config)
    g = easygv.build_graph(graph_input=graph_input, attrs=attrs)

    gvg = gv.Source(g.string(), engine=layout)
    for f in formats:
        gvg.format = f
        fig_path = gvg.render(directory / '{name}.gv'.format(name=name))
        log.info("Created: {p}".format(p=fig_path))


# Business
if __name__ == '__main__':
    main(obj=Munch())
