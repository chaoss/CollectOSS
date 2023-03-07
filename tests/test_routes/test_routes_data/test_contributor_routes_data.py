#SPDX-License-Identifier: MIT
import requests
import pytest

from tests import server_port

def test_contributors_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/contributors')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0


def test_contributors_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/contributors')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0

def test_contributors_new_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/contributors-new')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0


def test_contributors_new_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/contributors-new')
    assert response is not None
    print(response)
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0

