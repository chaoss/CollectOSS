import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_common(endpoint="http://localhost:5000/api/unstable/repos"):
    response = requests.get(endpoint)
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_downloaded_repos(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/repos')

def test_repo_groups(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/repo-groups')

def test_repos_in_repo_groups(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/repo-groups')

def test_get_repo_for_dosocs(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/dosocs/repos')

def test_aggregate_summary_by_repo(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/repo-groups/10/repos/25430/aggregate-summary')

def test_aggregate_summary_by_group(metrics):
    return test_common(endpoint='http://localhost:5000/api/unstable/repo-groups/10/aggregate-summary')

