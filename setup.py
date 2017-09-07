#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
from pathlib import Path

# Get info to include
with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


# Get libs to add use in setup
req_paths = ["requirements.pip.txt",
             "requirements.txt"]


def filter_req_paths(paths, func):
    """Return list of filtered libs."""
    if not isinstance(paths, list):
        raise ValueError("Paths must be a list of paths.")

    libs = set()
    junk = set(['\n'])
    for p in paths:
        with Path(p).open(mode='r') as reqs:
            lines = set([line for line in reqs if func(line)])
            libs.update(lines)

    return list(libs - junk)


def is_pipable(s):
    """Filter for pipable reqs."""
    if "# not_pipable" in s:
        return False
    elif s.startswith('#'):
        return False
    else:
        return True


requirements = filter_req_paths(paths=req_paths,
                                func=is_pipable)

setup_requirements = [
    'pytest-runner',
    # TODO(xguse): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]


# Do the setup
setup(
    name='easygv',
    version='0.1.0',
    description="Define nodes and edges in an excel file and graph-style attributes in a yaml file with inheritence.",
    long_description=readme + '\n\n' + history,
    author="Gus Dunn",
    author_email='w.gus.dunn@gmail.com',
    url='https://github.com/xguse/easygv',
    packages=find_packages(include=['easygv']),
    entry_points={
        'console_scripts': [
            'easygv=easygv.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='easygv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
