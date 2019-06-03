import os
import pytest

@pytest.fixture(scope="module")
def augur_db():
    import augur
    augur_app = augur.Application()
    return augur_app['augur_db']()

# def test_repoid(augur_db):
#     assert ghtorrent.repoid('rails', 'rails') >= 1000

# def test_userid(augur_db):
#     assert ghtorrent.userid('howderek') >= 1000

"""
Pandas testing format

assert ghtorrent.<function>('owner', 'repo').isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe

"""
