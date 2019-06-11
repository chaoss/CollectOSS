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

def test_code_changes(augur_db):
    #repo_id
    assert augur_db.code_changes(23, 21350, period='year').isin([pd.Timestamp('2009-01-01T00:00:00+00:00'), 2]).any().any()

    # repo_group_id
    assert augur_db.code_changes(23, period='year').isin([pd.Timestamp('2009-01-01T00:00:00+00:00'), 21350, 2]).any().any()

    #begin_date & end_date
    assert augur_db.code_changes(23, 21350, period='month', begin_date='2009',
                                 end_date='2011-05').isin([pd.Timestamp('2009-02-01T00:00:00+00:00'), 2]).any().any()
    assert augur_db.code_changes(23, period='month', begin_date='2009',
                                 end_date='2011-05').isin([pd.Timestamp('2011-02-01T00:00:00+00:00'), 21420, 4]).any().any()

def test_code_changes_lines(augur_db):
    #repo_id
    assert augur_db.code_changes_lines(22, 21331, period='year').isin([pd.Timestamp('2016-01-01T00:00:00+00:00'), 27190, 3163]).any().any()

    #repo_group_id
    assert augur_db.code_changes_lines(23, period='year').isin([pd.Timestamp('2016-01-01T00:00:00+00:00'), 21420, 31, 3]).any().any()

    #begin_date & end_date
    assert augur_db.code_changes_lines(22, 21331, period='month', begin_date='2016',
                                       end_date='2016-05').isin([pd.Timestamp('2016-02-01T00:00:00+00:00'), 196, 108]).any().any()
    assert augur_db.code_changes_lines(22, period='month', begin_date='2016-05',
                                       end_date='2016-08-15').isin([pd.Timestamp('2016-06-01T00:00:00+00:00'), 21331, 70, 20]).any().any()

def test_issues_new(augur_db):
    #repo_id
    assert augur_db.issues_new(23, 21430, period='year').iloc[0]['issues'] == 2

    #repo_group_id
    assert augur_db.issues_new(23, period='year').iloc[0]['issues'] == 2

    #begin_date & end_date
    assert augur_db.issues_new(24, 21979, period='week', begin_date='2017',
                               end_date='2017-05').iloc[1]['issues'] == 4
    assert augur_db.issues_new(24, period='month', begin_date='2017-05',
                               end_date='2018').iloc[2]['issues'] == 7
