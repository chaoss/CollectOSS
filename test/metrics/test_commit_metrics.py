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

