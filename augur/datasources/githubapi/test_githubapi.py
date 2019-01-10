import os
import pytest

@pytest.fixture
def github():
    import augur
    augur_app = augur.Application()
    return augur_app['githubapi']()

"""
Pandas testing format

assert ghtorrent.<function>(ghtorrent.repoid('owner', 'repo')).isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""

# *** DIVERSITY AND INCLUSION *** #

# *** GROWTH, MATURITY, AND DECLINE *** #

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

# *** EXPERIMENTAL *** #

# def test_bus_factor(github): #METRIC FUNCTION IS BROKEN
#     assert github.bus_factor("OSSHealth", "augur",start="1-1-17", end="5-12-17").isin(["9"]).any

def test_lines_of_code_changed(github):
    assert github.lines_of_code_changed("rails", "rails").isin(["2004-11-21T00:00:00.000Z"]).any

def test_tags(github):
    assert github.tags("rails", "rails").isin(["2008-04-10T17:25:06-07:00"]).any

def test_major_tags(github):
    assert github.major_tags("rails", "rails").isin(["2016-06-30T17:20:36-04:00"]).any
