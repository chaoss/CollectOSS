#SPDX-License-Identifier: MIT
import requests
import pytest
from tests import server_port


def  test_contributors_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/contributors')
    data = response.json()
    assert response.status_code == 200

def  test_contributors_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/contributors')
    data = response.json()
    assert response.status_code == 200

def  test_contributors_new_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/contributors-new')
    data = response.json()
    assert response.status_code == 200


def  test_contributors_new_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/contributors-new')
    data = response.json()
    assert response.status_code == 200
