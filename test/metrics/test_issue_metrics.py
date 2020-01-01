#SPDX-License-Identifier: MIT

import pytest
import pandas as pd

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

def test_issues_new(metrics):
    #repo_id
    assert metrics.issues_new(23, 21403, period='year').iloc[0]['issues'] > 0

    #repo_group_id
    assert metrics.issues_new(23, period='year').iloc[1]['issues'] > 0

    #begin_date & end_date
    assert metrics.issues_new(20, 21000, period='week', begin_date='2017',
                               end_date='2017-10').iloc[1]['issues'] > 0
    assert metrics.issues_new(20, period='month', begin_date='2017-05',
                               end_date='2018').iloc[2]['issues'] > 0

def test_issues_active(metrics):
    # repo
    assert metrics.issues_active(22, 21326, period='year').iloc[0]['issues'] > 0

    # repo_group
    assert metrics.issues_active(22, period='year').iloc[5]['issues'] > 0

    # begin_date & end_date
    assert metrics.issues_active(22, 21326, period='month', begin_date='2015',
                                  end_date='2015-09').iloc[0]['issues'] > 0

    assert metrics.issues_active(22, period='week', begin_date='2015-01',
                                  end_date='2015-08-05') .iloc[0]['issues'] > 0

def test_issues_closed(metrics):
    # repo
    assert metrics.issues_closed(24, 21681, period='year').iloc[0]['issues'] > 0

    #repo_group
    assert metrics.issues_closed(24, period='year').iloc[1]['issues'] > 0

    # begin_date & end_date
    assert metrics.issues_closed(24, 21681, period='week', begin_date='2012',
                                  end_date='2012-07').iloc[0]['issues'] > 0

    assert metrics.issues_closed(24, period='month', begin_date='2012-05',
                                  end_date='2012-08-15').iloc[0]['issues'] > 0

def test_issue_duration(metrics):
    # repo
    assert metrics.issue_duration(24, 21681).iloc[0]['duration'] == '5 days 02:05:43.000000000'

    # repo_group
    assert metrics.issue_duration(24).iloc[3]['duration'] == '172 days 04:39:33.000000000'

def test_issue_participants(metrics):
    # repo
    assert metrics.issue_participants(23, 21403).iloc[0]['participants'] > 0

    # repo_group
    assert metrics.issue_participants(22).iloc[4]['participants'] > 0

def test_issue_throughput(metrics):
    # repo
    assert metrics.issue_throughput(20, 21030).iloc[0]['throughput'] >= 0

    # repo_group
    assert metrics.issue_throughput(24).iloc[0]['throughput'] >= 0

def test_issue_backlog(metrics):
    #repo_id
    assert metrics.issue_backlog(21, 21166).iloc[0]['issue_backlog']  > 0

    #repo_group_id
    assert metrics.issue_backlog(21).iloc[2]['issue_backlog'] > 0


def test_issues_first_time_closed(metrics):

    # repo id
    assert metrics.issues_first_time_closed(21, repo_id=21000, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert metrics.issues_first_time_closed(24, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert metrics.issues_first_time_closed(24, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert metrics.issues_first_time_closed(21, repo_id=21000, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()


def test_open_issues_count(metrics):
    # repo
    assert metrics.open_issues_count(22, 21326).iloc[0]['open_count'] > 0

    # repo_group
    assert metrics.open_issues_count(23).iloc[1]['open_count'] > 0

def test_closed_issues_count(metrics):
    # repo
    assert metrics.closed_issues_count(24, 21684).iloc[0]['closed_count'] > 0

    # repo_group
    assert metrics.closed_issues_count(20).iloc[0]['closed_count'] > 0

def test_issues_open_age(metrics):
    #repo group
    assert metrics.issues_open_age(24).iloc[0]['open_date'] > 0
    # repo
    assert metrics.issues_open_age(20,21000).iloc[0]['open_date'] > 0

def test_issues_closed_resolution_duration(metrics):
    # repo group
    assert metrics.issues_closed_resolution_duration(24).iloc[0]['diffdate'] >= 0
    # repo
    assert metrics.issues_closed_resolution_duration(24,21682).iloc[0]['diffdate'] >= 0

def test_average_issue_resolution_time(metrics):
    #repo
    assert metrics.average_issue_resolution_time(20, 21000).isin(
        ['rails', '79 days 14:00:46.032574']).any().any()

    # repo_group
    assert metrics.average_issue_resolution_time(20).isin(
        ['arel', '440 days 33:20:23.678161']).any().any()

def test_issues_maintainer_response_duration(metrics):
    assert metrics.issues_maintainer_response_duration(20, 21000).iloc[0].average_days_comment > 0
    assert metrics.issues_maintainer_response_duration(20).iloc[0].average_days_comment > 0
    assert metrics.issues_maintainer_response_duration(20, 21000).iloc[0].average_days_comment > 0

def test_issue_comments_mean(metrics):
    assert metrics.issue_comments_mean(23).any().any()
    assert metrics.issue_comments_mean(23, 21000).any().any()
    assert metrics.issue_comments_mean(23, group_by='year').any().any()
    assert metrics.issue_comments_mean(23, 21000, group_by='year').any().any()

def test_issue_comments_mean_std(metrics):
    assert metrics.issue_comments_mean_std(23).any().any()
    assert metrics.issue_comments_mean_std(23, 21000).any().any()
    assert metrics.issue_comments_mean_std(23, group_by='year').any().any()
    assert metrics.issue_comments_mean_std(23, 21000, group_by='year').any().any()