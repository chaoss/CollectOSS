import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_downloaded_repos(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repos')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_repo_groups(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_repos_in_repo_groups(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_get_repo_for_dosocs(metrics):
    response = requests.get('http://localhost:5000/api/unstable/dosocs/repos')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_aggregate_summary_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21471/aggregate-summary')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_aggregate_summary_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/aggregate-summary')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

