#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `easygv` package."""
import re

import pytest

from click.testing import CliRunner

import pandas as pd

from easygv import cli
from easygv import easygv


def is_in(rgx, string):
    """Return True if the regex is found in the string."""
    if rgx.search(string):
        return True
    else:
        return False


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    help_option_line = re.compile("--help\W+Show this message and exit.")

    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert is_in(rgx=help_option_line, string=help_result.output)


def test_nan_to_str():
    """Test conversion of NaN values to string."""
    nan = pd.np.nan
    str_ = "testing"
    int_ = 12
    float_ = 67.9

    assert easygv.nan_to_str(x=nan) == ""
    assert easygv.nan_to_str(x=str_) is str_
    assert easygv.nan_to_str(x=int_) is int_
    assert easygv.nan_to_str(x=float_) is float_
    assert easygv.nan_to_str(x=pd) is pd
