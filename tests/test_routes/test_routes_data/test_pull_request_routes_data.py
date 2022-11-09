#SPDX-License-Identifier: MIT
import requests
import pytest
from tests import server_port


def test_pull_requests_merge_contributor_new_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_merge_contributor_new_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_closed_no_merge_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repos/25430/pull-requests-closed-no-merge')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["pr_count"] > 0

