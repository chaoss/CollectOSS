#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from  augur.api.metrics.issue import *

def test_issues_new():
    #repo_id
    assert issues_new(1, 1 , period='year').iloc[0]['issues'] > 0

    #repo_group_id
    assert issues_new(10, period='year').iloc[1]['issues'] > 0

    #begin_date & end_date
    assert issues_new(10, 25430, period='week', begin_date='2017',
                               end_date='2017-10').iloc[1]['issues'] > 0
    assert issues_new(10, period='month', begin_date='2017-05',
                               end_date='2018').iloc[2]['issues'] > 0

def test_issues_active():
    # repo
    assert issues_active(1, 1, period='year').iloc[0]['issues'] > 0

    # repo_group
    assert issues_active(10, period='year').iloc[0]['issues'] > 0

    # begin_date & end_date
    assert issues_active(10, 25430, period='month', begin_date='2020-02',
                                  end_date='2020-03').iloc[0]['issues'] > 0

    assert issues_active(10, period='week', begin_date='2020-01',
                                  end_date='2020-03') .iloc[0]['issues'] > 0

def test_issues_closed():
    # repo
    assert issues_closed(10, 25430, period='year').iloc[0]['issues'] > 0

    #repo_group
    assert issues_closed(10, period='year').iloc[0]['issues'] > 0

    # begin_date & end_date
    assert issues_closed(10, 25430, period='week', begin_date='2019',
                                  end_date='2020-02').iloc[0]['issues'] > 0

    assert issues_closed(10, period='month', begin_date='2018-05',
                                  end_date='2019-08-15').iloc[0]['issues'] > 0

def test_issue_duration():
    # repo
    assert issue_duration(10, 25430).iloc[0]['duration'] == '20 days 03:08:22.000000000'

    # repo_group
    assert issue_duration(10).iloc[0]['duration'] == '20 days 03:08:22.000000000'

def test_issue_participants():
    # repo
    assert issue_participants(10, 25430).iloc[0]['participants'] > 0

    # repo_group
    assert issue_participants(10).iloc[0]['participants'] > 0

def test_issue_throughput():
    # repo
    assert issue_throughput(10, 25430).iloc[0]['throughput'] >= 0

    # repo_group
    assert issue_throughput(10).iloc[0]['throughput'] >= 0

def test_issue_backlog():
    #repo_id
    assert issue_backlog(10, 25430).iloc[0]['issue_backlog']  > 0

    #repo_group_id
    assert issue_backlog(10).iloc[0]['issue_backlog'] > 0


def test_issues_first_time_closed():

    # repo id
    assert issues_first_time_closed(10, repo_id=25430, period='year').isin(
        [pd.Timestamp('2019', tz='UTC')]).any().any()

    # repo_group_id
    assert issues_first_time_closed(10, period='year').isin(
        [pd.Timestamp('2020', tz='UTC')]).any().any()

    # begin_date and end_date
    assert issues_first_time_closed(10, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert issues_first_time_closed(10, repo_id=25430, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()


def test_open_issues_count():
    # repo
    assert open_issues_count(10, 25430).iloc[0]['open_count'] > 0

    # repo_group
    assert open_issues_count(10).iloc[0]['open_count'] > 0

def test_closed_issues_count():
    # repo
    assert closed_issues_count(10, 25430).iloc[0]['closed_count'] > 0

    # repo_group
    assert closed_issues_count(10).iloc[0]['closed_count'] > 0

def test_issues_open_age():
    #repo group
    assert issues_open_age(10).iloc[0]['open_date'] > 0
    # repo
    assert issues_open_age(10, 25430).iloc[0]['open_date'] > 0

def test_issues_closed_resolution_duration():
    # repo group
    assert issues_closed_resolution_duration(10).iloc[0]['diffdate'] >= 0
    # repo
    assert issues_closed_resolution_duration(10, 25430).iloc[0]['diffdate'] >= 0

def test_average_issue_resolution_time():
    #repo
    assert average_issue_resolution_time(10, 25430).isin(
        ['augur', '61 days 12:20:43.791667']).any().any()

    # repo_group
    assert average_issue_resolution_time(10).isin(
        ['grimoirelab', ' 67 days 22:41:55.260417']).any().any()

def test_issues_maintainer_response_duration():
    assert issues_maintainer_response_duration(10, 25430).iloc[0].average_days_comment > 0
    assert issues_maintainer_response_duration(10).iloc[0].average_days_comment > 0
    assert issues_maintainer_response_duration(10, 25430).iloc[0].average_days_comment > 0

def test_issue_comments_mean():
    assert issue_comments_mean(10).any().any()
    assert issue_comments_mean(10, 25430).any().any()
    assert issue_comments_mean(10, group_by='year').any().any()
    assert issue_comments_mean(10, 25430, group_by='year').any().any()

def test_issue_comments_mean_std():
    assert issue_comments_mean_std(10).any().any()
    assert issue_comments_mean_std(10, 25430).any().any()
    assert issue_comments_mean_std(10, group_by='year').any().any()
    assert issue_comments_mean_std(10, 25430, group_by='year').any().any()
