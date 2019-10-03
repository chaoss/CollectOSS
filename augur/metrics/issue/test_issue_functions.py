import os
import pytest
import pandas as pd

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

def test_issues_new(metrics):
    #repo_id
    assert metrics.issues_new(1, 1, period='year').iloc[0]['issues'] > 0

    #repo_group_id
    assert metrics.issues_new(1, period='year').iloc[1]['issues'] > 0

    #begin_date & end_date
    assert metrics.issues_new(1, 1, period='week', begin_date='2017',
                               end_date='2017-05').iloc[1]['issues'] > 0
    assert metrics.issues_new(1, period='month', begin_date='2017-05',
                               end_date='2018').iloc[2]['issues'] > 0

def test_issues_active(metrics):
    # repo
    assert metrics.issues_active(1, 1, period='year').iloc[0]['issues'] > 0

    # repo_group
    assert metrics.issues_active(1, period='year').iloc[5]['issues'] > 0

    # begin_date & end_date
    assert metrics.issues_active(1, 1, period='month', begin_date='2015',
                                  end_date='2015-09').iloc[0]['issues'] > 0

    assert metrics.issues_active(1, period='week', begin_date='2015-01',
                                  end_date='2015-08-05') .iloc[0]['issues'] > 0

def test_issues_closed(metrics):
    # repo
    assert metrics.issues_closed(1, 1, period='year').iloc[0]['issues'] > 0

    #repo_group
    assert metrics.issues_closed(1, period='year').iloc[1]['issues'] > 0

    # begin_date & end_date
    assert metrics.issues_closed(1, 1, period='week', begin_date='2012',
                                  end_date='2012-07').iloc[0]['issues'] > 0

    assert metrics.issues_closed(1, period='month', begin_date='2012-05',
                                  end_date='2012-08-15').iloc[0]['issues'] > 0

def test_issue_duration(metrics):
    # repo
    assert metrics.issue_duration(1, 1).iloc[0]['duration'] == '1 days 18:58:57.000000000'

    # repo_group
    assert metrics.issue_duration(1).iloc[3]['duration'] == '12 days 16:38:15.000000000'

def test_issue_participants(metrics):
    # repo
    assert metrics.issue_participants(1, 1).iloc[0]['participants'] > 0

    # repo_group
    assert metrics.issue_participants(1).iloc[4]['participants'] > 0

def test_issue_throughput(metrics):
    # repo
    assert metrics.issue_throughput(1, 1).iloc[0]['throughput'] >= 0

    # repo_group
    assert metrics.issue_throughput(1).iloc[0]['throughput'] >= 0

def test_issue_backlog(metrics):
    #repo_id
    assert metrics.issue_backlog(1, 1).iloc[0]['issue_backlog']  > 0

    #repo_group_id
    assert metrics.issue_backlog(1).iloc[0]['issue_backlog'] > 0


def test_issues_first_time_closed(metrics):

    # repo id
    assert metrics.issues_first_time_closed(1, repo_id=1, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert metrics.issues_first_time_closed(1, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert metrics.issues_first_time_closed(1, period='year', begin_date='2011-1-1 00:00:00',
                                             end_date='2019-12-31 1:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert metrics.issues_first_time_closed(1, repo_id=1, period='year', begin_date='2011-1-1 00:00:00',
                                             end_date='2019-12-31 1:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()


def test_open_issues_count(metrics):
    # repo
    assert metrics.open_issues_count(1, 1).iloc[0]['open_count'] > 0

    # repo_group
    assert metrics.open_issues_count(1).iloc[1]['open_count'] > 0

def test_closed_issues_count(metrics):
    # repo
    assert metrics.closed_issues_count(1, 1).iloc[0]['closed_count'] > 0

    # repo_group
    assert metrics.closed_issues_count(1).iloc[0]['closed_count'] > 0

def test_issues_open_age(metrics):
    #repo group
    assert metrics.issues_open_age(1).iloc[0]['open_date'] > 0
    # repo
    assert metrics.issues_open_age(1,1).iloc[0]['open_date'] > 0

def test_issues_closed_resolution_duration(metrics):
    # repo group
    assert metrics.issues_closed_resolution_duration(1).iloc[0]['diffdate'] >= 0
    # repo
    assert metrics.issues_closed_resolution_duration(1,1).iloc[0]['diffdate'] >= 0

def test_average_issue_resolution_time(metrics):
    #repo
    assert metrics.average_issue_resolution_time(1, 1).isin(
        ['rails', '68 days 21:57:03.361146']).any().any()

    # repo_group
    assert metrics.average_issue_resolution_time(1).isin(
        ['rails', '68 days 21:57:03.361146']).any().any()

def test_issues_maintainer_response_duration(metrics):
    assert metrics.issues_maintainer_response_duration(1, 1).iloc[0].average_days_comment > 0
    assert metrics.issues_maintainer_response_duration(1).iloc[0].average_days_comment > 0
    assert metrics.issues_maintainer_response_duration(1, 1).iloc[0].average_days_comment > 0

def test_issue_comments_mean(metrics):
    assert metrics.issue_comments_mean(1).any().any()
    assert metrics.issue_comments_mean(1, 1).any().any()
    assert metrics.issue_comments_mean(1, group_by='year').any().any()
    assert metrics.issue_comments_mean(1, 1, group_by='year').any().any()

def test_issue_comments_mean_std(metrics):
    assert metrics.issue_comments_mean_std(1).any().any()
    assert metrics.issue_comments_mean_std(1, 1).any().any()
    assert metrics.issue_comments_mean_std(1, group_by='year').any().any()
    assert metrics.issue_comments_mean_std(1, 1, group_by='year').any().any()