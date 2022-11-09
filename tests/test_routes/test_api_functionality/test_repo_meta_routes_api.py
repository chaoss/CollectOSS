#SPDX-License-Identifier: MIT
import requests
import pytest

from tests import server_port


def  test_code_changes_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/code-changes')
    data = response.json()
    assert response.status_code == 200

def  test_code_changes_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/code-changes')
    data = response.json()
    assert response.status_code == 200
    
def  test_code_changes_lines_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/code-changes-lines')
    data = response.json()
    assert response.status_code == 200

def  test_code_changes_lines_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/code-changes-lines')
    data = response.json()
    assert response.status_code == 200

def  test_sub_projects_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/sub-projects')
    data = response.json()
    assert response.status_code == 200

def  test_sub_projects_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/sub-projects')
    data = response.json()
    assert response.status_code == 200

def  test_cii_best_practices_badge_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/cii-best-practices-badge')
    data = response.json()
    assert response.status_code == 200

def  test_languages_by_group_api_is_functional():
    # TODO need data
    pass

def  test_languages_by_repo_api_is_functional():
    # TODO need data
    pass

# def  test_license_declared_by_group_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-declared')
#     data = response.json()
#     assert response.status_code == 200
#   

# def  test_license_declared_by_repo_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-declared')
#     data = response.json()
#     assert response.status_code == 200

def  test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_repo_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

def  test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_group_api_is_functional():
    response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200

# def  test_license_coverage_by_group_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-coverage')
#     data = response.json()
#     assert response.status_code == 200

# def  test_license_coverage_by_repo_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-coverage')
#     data = response.json()
#     assert response.status_code == 200

# def  test_license_count_by_group_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/license-count')
#     data = response.json()
#     assert response.status_code == 200

# def  test_license_count_by_repo_api_is_functional():
#     response = requests.get(f'http://localhost:{server_port}/api/unstable/repo-groups/10/repos/25430/license-count')
#     data = response.json()
#     assert response.status_code == 200

