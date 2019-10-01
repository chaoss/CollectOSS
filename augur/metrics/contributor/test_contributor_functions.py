import os
import pytest
import pandas as pd

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

def test_contributors(metrics):
    # repo group
    assert metrics.contributors(20).iloc[0]['total'] > 0

    # repo id
    assert metrics.contributors(
        24, repo_id=21000).iloc[0]['total'] > 0

    # test begin_date and end_date
    assert metrics.contributors(20, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] > 0

    assert metrics.contributors(20, repo_id=21000, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59').iloc[0]['total'] > 0


def test_contributors_new(metrics):
    assert metrics.contributors_new(21, repo_id=21222, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # repo_group_id
    assert metrics.contributors_new(24, period='year').isin(
        [pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    # begin_date and end_date
    assert metrics.contributors_new(24, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

    assert metrics.contributors_new(21, repo_id=21222, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').isin([pd.Timestamp('2019-01-01 00:00:00', tz='UTC')]).any().any()

def test_top_committers(metrics):
    assert metrics.top_committers(20).iloc[0]['commits'] > 0
    assert metrics.top_committers(20, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(20, year=2017, threshold=0.7).iloc[0]['commits'] > 0
    assert metrics.top_committers(20, 21000).iloc[0]['commits'] > 0
    assert metrics.top_committers(20, 21000, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(20, 21000, year=2017, threshold=0.7).iloc[0]['commits'] > 0

def test_committer(metrics):
    assert metrics.committers(21,period='year').iloc[0]['count'] > 100
    assert metrics.committers(20,21000,period='year').iloc[0]['count'] > 100

