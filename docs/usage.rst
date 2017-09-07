=====
Usage
=====

---------------------
Import into a project
---------------------

You can import the package as follows:

.. code-block:: python

    from easygv import easygv


---------------------
The command line tool
---------------------


Base command help text
======================

.. code-block:: bash

    $ easygv --help

    Usage: easygv [OPTIONS] COMMAND [ARGS]...

      Command interface to easygv.

      Define nodes and edges in an excel file and graph-style attributes in a
      yaml file with inheritence.

      For command specific help text, call the specific command followed by the
      --help option.

    Options:
      -v, --verbosity [debug|normal|quiet]
                                      How much do you want to know about what I am
                                      doing?  [default: normal]
      --help                          Show this message and exit.

    Commands:
      config  Manage configuration values and files.
      draw    Draw and save your graph.


Dealing with configuration files
================================

.. code-block:: bash

    $ easygv config --help

    Usage: easygv config [OPTIONS]

      Manage configuration values and files.

    Options:
      -g, --generate-config  Copy one or more of the 'factory default' config
                             files to the users config directory
                             (/home/gus/.config/easygv). Back ups will be made of
                             any existing config files.  [default: False]
      -k, --kind [attrs]     Which type of config should we replace?  [default:
                             attrs]
      -p, --prefix TEXT      A prefix to identify the new config file(s).
      --help                 Show this message and exit.



Drawing your graphs
===================

.. code-block:: bash

    $ easygv draw --help

    Usage: easygv draw [OPTIONS] DEFINITION ATTR_CONFIG

      Produce your graph and save results based on your input.

      DEFINITION  = Excel file containing the definition of your nodes and edges
      ATTR_CONFIG = YAML file containing the attribute information for your
                    graph, node-, and edge-types

    Options:
      -f, --formats [all|pdf|png|svg]
                                      Which type of format should we produce?
                                      [default: all]
      -d, --directory DIRECTORY       Path to a directory to write out the files.
      -n, --name TEXT                 A name for your figure.
      -l, --layout [dot|neato|fdp|sfdp|twopi|circo]
                                      Which layout program?  [default: dot]
      --help                          Show this message and exit.
