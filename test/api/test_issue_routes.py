import requests
import pytest

@pytest.fixture(scope="session")
def metrics():
    pass

def test_issues_new_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_new_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_active_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-active')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_active_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-active')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_closed_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_closed_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21681/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issue_duration_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-duration')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_duration_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21030/issue-duration')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_participants_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-participants')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['participants'] > 0

def test_issue_participants_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issue-participants')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['participants'] > 0

def test_issue_throughput_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-throughput')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['throughput'] >= 0

def test_issue_throughput_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21682/issue-throughput')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['throughput'] >= 0

def test_issue_backlog_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-backlog')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issue_backlog'] > 0

def test_issue_backlog_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21403/issue-backlog')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issue_backlog'] > 0

def test_issues_first_time_opened_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-first-time-opened')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_opened_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21222/issues-first-time-opened')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_closed_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-first-time-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_closed_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/22997/issues-first-time-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_open_issues_count_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/open-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['open_count'] > 0

def test_open_issues_count_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/repos/21326/open-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['open_count'] > 0

def test_closed_issues_count_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/closed-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['closed_count'] > 0

def test_closed_issues_count_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/repos/21684/closed-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['closed_count'] > 0

def test_issues_open_age_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-open-age/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["open_date"] > 1

def test_issues_open_age_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-open-age/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["open_date"] > 1

def test_issues_closed_resolution_duration_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-closed-resolution-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["diffdate"] >= 0


def test_issues_closed_resolution_duration_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21041/issues-closed-resolution-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["diffdate"] >= 0

def test_issues_maintainer_response_duration_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-maintainer-response-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["average_days_comment"] >= 0

def test_issues_maintainer_response_duration_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-maintainer-response-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["average_days_comment"] >= 0
    assert data[0]["average_days_comment"] >= 0

def test_average_issue_resolution_time_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/average-issue-resolution-time')
    data = response.json()
    assert response.status_code == 200
    assert len(data) > 0

def test_average_issue_resolution_time_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/average-issue-resolution-time')
    data = response.json()
    assert response.status_code == 200
    assert len(data) > 0

def test_issue_comments_mean_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/issue-comments-mean')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_comments_mean_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21104/issue-comments-mean')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_comments_mean_std_by_group(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/issue-comments-mean-std')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_comments_mean_std_by_repo(metrics):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21104/issue-comments-mean-std')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
