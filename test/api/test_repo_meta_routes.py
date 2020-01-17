import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_code_changes_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_lines_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_code_changes_lines_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_sub_projects_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/sub-projects')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_project_count"] > 0

def test_sub_projects_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21477/sub-projects')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_project_count"] > 0

def test_cii_best_practices_badge_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21000/cii-best-practices-badge')
    print(response)
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_languages_by_group(metrics):
    # TODO need data
    pass

def test_languages_by_repo(metrics):
    # TODO need data
    pass

# def test_license_declared_by_group(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/license-declared')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_declared_by_repo(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21116/license-declared')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

# def test_license_coverage_by_group(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/license-coverage')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_coverage_by_repo(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21116/license-coverage')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_count_by_group(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/license-count')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

# def test_license_count_by_repo(metrics):
#     response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21116/license-count')
#     data = response.json()
#     assert response.status_code == 200
#     assert len(data) >= 1

