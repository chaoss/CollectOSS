#SPDX-License-Identifier: MIT

import pytest

def test_annual_commit_count_ranked_by_repo_in_repo_group(metrics):
    assert metrics.annual_commit_count_ranked_by_repo_in_repo_group(10).iloc[0].net > 0
    assert metrics.annual_commit_count_ranked_by_repo_in_repo_group(10, 25430).iloc[0].net > 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group(metrics):
    assert metrics.annual_commit_count_ranked_by_new_repo_in_repo_group(10).iloc[0].net > 0
    assert metrics.annual_commit_count_ranked_by_new_repo_in_repo_group(10, 25430).iloc[0].net > 0

def test_top_committers(metrics):
    assert metrics.top_committers(10, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(10, year=2017, threshold=0.7).iloc[0]['commits'] > 0
    assert metrics.top_committers(10, 25430, year=2017).iloc[0]['commits'] > 0
    assert metrics.top_committers(10, 25430, year=2017, threshold=0.7).iloc[0]['commits'] > 0
    assert metrics.top_committers(10).iloc[0]['commits'] > 0
    assert metrics.top_committers(10, 25430).iloc[0]['commits'] > 0

def test_committer(metrics):
    assert metrics.committers(10, period='year').iloc[0]['count'] > 0
    assert metrics.committers(10, 25430,period='year').iloc[0]['count'] > 0
