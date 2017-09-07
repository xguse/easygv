#!/usr/bin/env python
"""Provide functions used in cli.config."""

# Imports
from logzero import logger as log
from pathlib import Path
import shutil
import datetime as dt
from munch import Munch, munchify
import ruamel.yaml as yaml


def update_configs(directory, to_update=None):  # noqa: D301
    """Collect, combine, and return all \*.yaml files in ``directory``."""
    confs = Path(directory).glob('*.yaml')

    confs = {p.stem.upper(): p for p in confs}

    if to_update is None:
        to_update = Munch()

    for name, conf in confs.items():
        c = process_config(config=conf)
        to_update.update(Munch({name: c}))

    return to_update


def process_config(config=None):
    """Prepare single config file."""
    if config is None:
        return Munch()
    else:
        if isinstance(config, str):
            config = Path(config)
        return munchify(yaml.safe_load(config.open()))


def replace_config(name, factory_resets, user_conf_dir, prefix=None):
    """Replace existing config file or generate initial one.

    Backup existing file.
    """
    if prefix is None:
        prefix = ""
    else:
        prefix = prefix + '.'

    if not user_conf_dir.exists():
        user_conf_dir.mkdir(parents=True, exist_ok=True)
        log.info("Created {} for your default attr configurations.".format(user_conf_dir))

    default_path = factory_resets / name
    conf_path = user_conf_dir / '{prefix}{name}'.format(name=name,
                                                        prefix=prefix)

    stamp = dt.datetime.today().isoformat()
    if conf_path.exists():
        bk_path = Path('{name}.bkdup_on_{stamp}'.format(name=str(conf_path),
                                                        stamp=stamp))
        shutil.move(src=str(conf_path), dst=str(bk_path))
        log.info("Backed up {conf_path} as {bk_path}.".format(conf_path=conf_path,
                                                              bk_path=bk_path))

    shutil.copy(src=str(default_path), dst=str(conf_path))
    log.info("Created {}.".format(conf_path))
