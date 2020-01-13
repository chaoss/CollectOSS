import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_annual_commit_count_ranked_by_new_repo_in_repo_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-new-repo-in-repo-group/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] >= 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_commit_count_ranked_by_repo_in_repo_group_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_commit_count_ranked_by_repo_in_repo_group_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_top_committers_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/repos/21334/top-committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commits'] > 0

def test_top_committers_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/top-committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commits'] > 0

def test_committer_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21222/committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_committer_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/committers?period=year')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
