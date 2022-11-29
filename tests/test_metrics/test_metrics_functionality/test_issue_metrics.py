#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from  augur.api.metrics.issue import *

df_type = type(pd.DataFrame())

def test_issues_new():
    #repo_id
    assert isinstance(issues_new(1, 1 , period='year'), df_type)

    #repo_group_id
    assert isinstance(issues_new(10, period='year'), df_type)

    #begin_date & end_date
    assert isinstance(issues_new(10, 25430, period='week', begin_date='2017',
                               end_date='2017-10'), df_type)
    assert isinstance(issues_new(10, period='month', begin_date='2017-05',
                               end_date='2018'), df_type)

def test_issues_active():
    # repo
    assert isinstance(issues_active(1, 1, period='year'), df_type)

    # repo_group
    assert isinstance(issues_active(10, period='year'), df_type)

    # begin_date & end_date
    assert isinstance(issues_active(10, 25430, period='month', begin_date='2020-02',
                                  end_date='2020-03'), df_type)

    assert isinstance(issues_active(10, period='week', begin_date='2020-01',
                                  end_date='2020-03'), df_type) 

def test_issues_closed():
    # repo
    assert isinstance(issues_closed(10, 25430, period='year'), df_type)

    #repo_group
    assert isinstance(issues_closed(10, period='year'), df_type)

    # begin_date & end_date
    assert isinstance(issues_closed(10, 25430, period='week', begin_date='2019',
                                  end_date='2020-02'), df_type)

    assert isinstance(issues_closed(10, period='month', begin_date='2018-05',
                                  end_date='2019-08-15'), df_type)

def test_issue_duration():
    # repo
    assert isinstance(issue_duration(10, 25430), df_type)

    # repo_group
    assert isinstance(issue_duration(10), df_type)

def test_issue_participants():
    # repo
    assert isinstance(issue_participants(10, 25430), df_type)

    # repo_group
    assert isinstance(issue_participants(10), df_type)

def test_issue_throughput():
    # repo
    assert isinstance(issue_throughput(10, 25430), df_type)

    # repo_group
    assert isinstance(issue_throughput(10), df_type)

def test_issue_backlog():
    #repo_id
    assert isinstance(issue_backlog(10, 25430), df_type)

    #repo_group_id
    assert isinstance(issue_backlog(10), df_type)


def test_issues_first_time_closed():

    # repo id
    assert isinstance(issues_first_time_closed(10, repo_id=25430, period='year'), df_type)

    # repo_group_id
    assert isinstance(issues_first_time_closed(10, period='year'), df_type)

    # begin_date and end_date
    assert isinstance(issues_first_time_closed(10, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59'), df_type)

    assert isinstance(issues_first_time_closed(10, repo_id=25430, period='year', begin_date='2019-1-1 00:00:00',
                                             end_date='2019-12-31 23:59:59'), df_type)


def test_open_issues_count():
    # repo
    assert isinstance(open_issues_count(10, 25430), df_type)

    # repo_group
    assert isinstance(open_issues_count(10), df_type)

def test_closed_issues_count():
    # repo
    assert isinstance(closed_issues_count(10, 25430), df_type)

    # repo_group
    assert isinstance(closed_issues_count(10), df_type)

def test_issues_open_age():
    #repo group
    assert isinstance(issues_open_age(10), df_type)
    # repo
    assert isinstance(issues_open_age(10, 25430), df_type)

def test_issues_closed_resolution_duration():
    # repo group
    assert isinstance(issues_closed_resolution_duration(10), df_type)
    # repo
    assert isinstance(issues_closed_resolution_duration(10, 25430), df_type)

def test_average_issue_resolution_time():
    #repo
    assert isinstance(average_issue_resolution_time(10, 25430), df_type)

    # repo_group
    assert isinstance(average_issue_resolution_time(10), df_type)


def test_issues_maintainer_response_duration():
    assert isinstance(issues_maintainer_response_duration(10, 25430), df_type)
    assert isinstance(issues_maintainer_response_duration(10), df_type)
    assert isinstance(issues_maintainer_response_duration(10, 25430), df_type)

def test_issue_comments_mean():
    assert isinstance(issue_comments_mean(10), df_type)
    assert isinstance(issue_comments_mean(10, 25430), df_type)
    assert isinstance(issue_comments_mean(10, group_by='year'), df_type)
    assert isinstance(issue_comments_mean(10, 25430, group_by='year'), df_type)

def test_issue_comments_mean_std():
    assert isinstance(issue_comments_mean_std(10), df_type)
    assert isinstance(issue_comments_mean_std(10, 25430), df_type)
    assert isinstance(issue_comments_mean_std(10, group_by='year'), df_type)
    assert isinstance(issue_comments_mean_std(10, 25430, group_by='year'), df_type)
