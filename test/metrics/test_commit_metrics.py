#SPDX-License-Identifier: MIT

import pytest

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

def test_annual_commit_count_ranked_by_repo_in_repo_group(metrics):
    assert metrics.annual_commit_count_ranked_by_repo_in_repo_group(20).iloc[0].net > 0
    assert metrics.annual_commit_count_ranked_by_repo_in_repo_group(20, 21000).iloc[0].net > 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group(metrics):
    assert metrics.annual_commit_count_ranked_by_new_repo_in_repo_group(20).iloc[0].net > 0
    assert metrics.annual_commit_count_ranked_by_new_repo_in_repo_group(20, 21000).iloc[0].net > 0

def test_top_committers(metrics):
    assert metrics.top_committers(24, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(24, year=2017, threshold=0.7).iloc[0]['commits'] > 0
    assert metrics.top_committers(24, 21000, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(24, 21000, year=2017, threshold=0.7).iloc[0]['commits'] > 0
    assert metrics.top_committers(24).iloc[0]['commits'] > 0
    assert metrics.top_committers(24, 21000).iloc[0]['commits'] > 0

def test_committer(metrics):
    assert metrics.committers(21,period='year').iloc[0]['count'] > 0
    assert metrics.committers(20,21000,period='year').iloc[0]['count'] > 0
