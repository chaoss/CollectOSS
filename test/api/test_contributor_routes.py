import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_contributors_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0


def test_contributors_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0

def test_contributors_new_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0


def test_contributors_new_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21070/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["new_contributors"] > 0

