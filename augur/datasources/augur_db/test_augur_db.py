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

def test_issue_backlog(augur_db):
    #repo_id
    assert augur_db.issue_backlog(21, 21166).iloc[0]['issue_backlog']  == 4

    #repo_group_id
    assert augur_db.issue_backlog(21).iloc[2]['issue_backlog'] == 3

def test_issues_first_time_closed(augur_db):

    # repo id
    assert augur_db.issues_first_time_closed(24, repo_id=21524, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert augur_db.issues_first_time_closed(24, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert augur_db.issues_first_time_closed(24, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert augur_db.issues_first_time_closed(24, repo_id=21524, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

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

def test_pull_requests_merge_contributor_new(augur_db):
    # repo id
    assert augur_db.pull_requests_merge_contributor_new(24, repo_id=21524, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert augur_db.pull_requests_merge_contributor_new(24, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert augur_db.pull_requests_merge_contributor_new(24, period='year', begin_date='2019-1-1 00:00:00',
                                                        end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()


def test_contributors(augur_db):
    # repo group
    assert augur_db.contributors(24).iloc[0]['total'] > 5

    # repo id
    assert augur_db.contributors(
        24, repo_id=21524).iloc[0]['total'] > 5

    # test begin_date and end_date
    assert augur_db.contributors(24, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] < 5

    assert augur_db.contributors(24, repo_id=21524, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] < 5


def test_contributors_new(augur_db):
    assert augur_db.contributors_new(24, repo_id=21524, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert augur_db.contributors_new(24, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert augur_db.contributors_new(24, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert augur_db.contributors_new(24, repo_id=21524, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()
