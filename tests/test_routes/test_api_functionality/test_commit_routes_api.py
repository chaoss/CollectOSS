#SPDX-License-Identifier: MIT
import requests
import pytest
from tests import server_port


def  test_annual_commit_count_ranked_by_new_repo_in_repo_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-commit-count-ranked-by-new-repo-in-repo-group/')
    data = response.json()
    assert response.status_code == 200

def  test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_commit_count_ranked_by_repo_in_repo_group_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_commit_count_ranked_by_repo_in_repo_group_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_top_committers_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/top-committers')
    data = response.json()
    assert response.status_code == 200

def  test_top_committers_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/top-committers')
    data = response.json()
    assert response.status_code == 200

def  test_committer_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/committers')
    data = response.json()
    assert response.status_code == 200

def  test_committer_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/committers?period=year')
    data = response.json()
    assert response.status_code == 200
