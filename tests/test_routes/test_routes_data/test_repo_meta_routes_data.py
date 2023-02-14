#SPDX-License-Identifier: MIT
import requests
import pytest
from tests import server_port


def test_code_changes_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/code-changes')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/code-changes')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    # assert len(data) >= 1
    # assert data[0]['commit_count'] > 0

def test_code_changes_lines_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/code-changes-lines')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_code_changes_lines_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/code-changes-lines')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_sub_projects_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/sub-projects')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_project_count"] > 0

def test_sub_projects_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/sub-projects')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_project_count"] > 0

def test_cii_best_practices_badge_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/cii-best-practices-badge')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_languages_by_group_api_data():
    # TODO need data
    pass

def test_languages_by_repo_api_data():
    # TODO need data
    pass

# def test_license_declared_by_group_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-declared')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_declared_by_repo_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-declared')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_repo_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_group_api_data():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    assert response is not None
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

# def test_license_coverage_by_group_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-coverage')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_coverage_by_repo_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-coverage')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_count_by_group_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-count')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_count_by_repo_api_data():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-count')
    assert response is not None
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

