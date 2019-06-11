import os
import pytest
import pandas as pd

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


def test_issues_first_time_opened(augur_db):

    # repo_id
    assert augur_db.issues_first_time_opened(
        1, repo_id=25001, period='day').isin(["2019-05-23 00:00:00+00:00"]).any
    assert augur_db.issues_first_time_opened(
        1, repo_id=25001, period='week').isin(["2019-05-20 00:00:00+00:00"]).any

    # repo_gorup_id
    assert augur_db.issues_first_time_opened(1, period='day').isin([
        "2019-05-23 00:00:00+00:00"]).any


def test_sub_projects(augur_db):

    # repo group
    assert augur_db.sub_projects(24).iloc[0]['sub_protject_count'] > 50

    # repo id
    assert augur_db.sub_projects(
        24, repo_id=21477).iloc[0]['sub_protject_count'] > 50

    # test begin_date and end_date
    assert augur_db.sub_projects(24, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['sub_protject_count'] < 5

    assert augur_db.sub_projects(24, repo_id=21441, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['sub_protject_count'] < 5
