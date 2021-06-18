#SPDX-License-Identifier: MIT
import requests
import pytest

def test_pull_requests_merge_contributor_new_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_merge_contributor_new_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/10/repos/25430/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_closed_no_merge(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repos/25430/pull-requests-closed-no-merge')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["pr_count"] > 0

