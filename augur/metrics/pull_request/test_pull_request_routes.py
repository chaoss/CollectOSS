import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_pull_requests_merge_contributor_new_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_merge_contributor_new_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21339/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

