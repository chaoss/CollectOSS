import os
import pytest
import pandas

@pytest.fixture
def github():
    import augur
    augurApp = augur.Application()
    return augurApp.github()

"""
Pandas testing format

assert ghtorrent.<function>(ghtorrent.repoid('owner', 'repo')).isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""

# *** DIVERSITY AND INCLUSION *** #

# *** GROWTH, MATURITY, AND DECLINE *** #
# lines changed

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

# *** EXPERIMENTAL *** #
def test_bus_factor(github):
    assert github.bus_factor("OSSHealth", "augur",start="1-1-17", end="5-12-17").isin(["9"]).any

# def test_tags(github):
#     assert github.tags("OSSHealth", "augur").isin(["v0.2"]).any

# major tags








