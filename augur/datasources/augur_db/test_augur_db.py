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
    assert augur_db.issues_new(23, 21403, period='year').iloc[0]['issues'] == 1

    #repo_group_id
    assert augur_db.issues_new(23, period='year').iloc[1]['issues'] == 1

    #begin_date & end_date
    assert augur_db.issues_new(24, 21979, period='week', begin_date='2017',
                               end_date='2017-05').iloc[1]['issues'] == 4
    assert augur_db.issues_new(24, period='month', begin_date='2017-05',
                               end_date='2018').iloc[2]['issues'] == 2

def test_issues_active(augur_db):
    # repo
    assert augur_db.issues_active(22, 21326, period='year').iloc[0]['issues'] == 98

    # repo_group
    assert augur_db.issues_active(22, period='year').iloc[5]['issues'] == 20

    # begin_date & end_date
    assert augur_db.issues_active(22, 21326, period='month', begin_date='2015',
                                  end_date='2015-09').iloc[0]['issues'] == 32

    assert augur_db.issues_active(22, period='week', begin_date='2015-01',
                                  end_date='2015-08-05') .iloc[0]['issues'] == 32

def test_issues_closed(augur_db):
    # repo
    assert augur_db.issues_closed(24, 21681, period='year').iloc[0]['issues'] == 189

    #repo_group
    assert augur_db.issues_closed(24, period='year').iloc[1]['issues'] == 97

    # begin_date & end_date
    assert augur_db.issues_closed(24, 21681, period='week', begin_date='2012',
                                  end_date='2012-07').iloc[0]['issues'] == 10

    assert augur_db.issues_closed(24, period='month', begin_date='2012-05',
                                  end_date='2012-08-15').iloc[0]['issues'] == 50

def test_issue_duration(augur_db):
    # repo
    assert augur_db.issue_duration(24, 21681).iloc[0]['duration'] == '0 days 01:06:31.000000000'

    # repo_group
    assert augur_db.issue_duration(24).iloc[3]['duration'] == '5 days 05:18:21.000000000'

def test_issue_participants(augur_db):
    # repo
    assert augur_db.issue_participants(23, 21403).iloc[0]['participants'] == 1

    # repo_group
    assert augur_db.issue_participants(22).iloc[4]['participants'] == 4

def test_issue_throughput(augur_db):
    # repo
    assert augur_db.issue_throughput(20, 21009).iloc[0]['throughput'] == 0.263158

    # repo_group
    assert augur_db.issue_throughput(24).iloc[0]['throughput'] == 0.861896

def test_issue_backlog(augur_db):
    #repo_id
    assert augur_db.issue_backlog(21, 21166).iloc[0]['issue_backlog']  == 4

    #repo_group_id
    assert augur_db.issue_backlog(21).iloc[2]['issue_backlog'] == 20


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
    assert augur_db.contributors(20).iloc[0]['total'] > 0

    # repo id
    assert augur_db.contributors(
        24, repo_id=21000).iloc[0]['total'] > 0

    # test begin_date and end_date
    assert augur_db.contributors(20, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] > 0

    assert augur_db.contributors(20, repo_id=21000, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] > 0


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

def test_open_issues_count(augur_db):
    # repo
    assert augur_db.open_issues_count(22, 21326).iloc[0]['open_count'] == 1

    # repo_group
    assert augur_db.open_issues_count(23).iloc[1]['open_count'] == 4

def test_closed_issues_count(augur_db):
    # repo
    assert augur_db.closed_issues_count(24, 21684).iloc[0]['closed_count'] == 3

    # repo_group
    assert augur_db.closed_issues_count(20).iloc[0]['closed_count'] == 1

def test_issues_open_age(augur_db):
    #repo group
    assert augur_db.issues_open_age(24).iloc[0]['open_date'] > 0
    # repo 
    assert augur_db.issues_open_age(20,21000).iloc[0]['open_date'] > 0

def test_issues_closed_resolution_duration(augur_db):
    # repo group
    assert augur_db.issues_closed_resolution_duration(24).iloc[0]['diffdate'] >= 0
    # repo
    assert augur_db.issues_closed_resolution_duration(24,21682).iloc[0]['diffdate'] >= 0

def test_get_repo(augur_db):
    assert augur_db.get_repo_by_name('Comcast','zucchini').iloc[0].repo_id == 21116

def test_lines_changed_by_author(augur_db):
    assert augur_db.lines_changed_by_author(20).iloc[0].additions > 0
    assert augur_db.lines_changed_by_author(20,21000).iloc[0].additions > 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group(augur_db):
    assert augur_db.annual_commit_count_ranked_by_new_repo_in_repo_group(20, calendar_year=2019).iloc[0].net > 0    

def test_cii_best_practices_badge(augur_db):
    # repo
    assert augur_db.cii_best_practices_badge(21, 21252).iloc[0]['badge_level'] == 'in_progress'

    # repo_group
    assert augur_db.cii_best_practices_badge(21).iloc[0]['badge_level'] == 'passing'

def test_languages(augur_db):
    # TODO
    pass

def test_license_declared(augur_db):
    assert augur_db.license_declared(21, 21252).iloc[0]['license'] == 'Apache-2.0'

    assert augur_db.license_declared(21).iloc[0]['license'] == 'Apache-2.0'
