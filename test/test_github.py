import os
import pytest
import pandas

@pytest.fixture
def github():
    import ghdata
    return ghdata.GitHubAPI(os.getenv("GITHUB_API_KEY"))

"""
Pandas testing format

assert ghtorrent.<function>(ghtorrent.repoid('owner', 'repo')).isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""

def test_bus_factor(github):
    assert github.bus_factor("OSSHealth", "ghdata",start="1-1-17", end="5-12-17").isin(["2"]).any

def test_best_case_bus_factor(github):
    assert github.bus_factor("OSSHealth", "ghdata",start="1-1-17", end="5-12-17", best=True).isin(["9"]).any
