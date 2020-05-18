#SPDX-License-Identifier: MIT

import pytest
import pandas as pd

def test_pull_requests_merge_contributor_new(metrics):
    # repo id
    assert metrics.pull_requests_merge_contributor_new(10, repo_id=25430, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert metrics.pull_requests_merge_contributor_new(10, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert metrics.pull_requests_merge_contributor_new(10, period='year', begin_date='2019-1-1 00:00:00',
                                                        end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

def test_pull_request_acceptance_rate(metrics):
    assert metrics.pull_request_acceptance_rate(20).iloc[0]['rate'] > 0
    assert metrics.pull_request_acceptance_rate(10, 25430,begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59',group_by='year').iloc[0]['rate'] > 0

def test_pull_request_closed_no_merge(metrics):
    assert metrics.pull_requests_closed_no_merge(10).iloc[0]['pr_count'] > 0
    assert metrics.pull_requests_closed_no_merge(10, 25430, begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').iloc[0]['pr_count'] > 0

