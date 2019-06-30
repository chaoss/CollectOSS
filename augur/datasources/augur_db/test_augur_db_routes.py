import os
import subprocess
import time
from subprocess import Popen
import pytest
import requests

@pytest.fixture(scope="session")
def augur_db_routes():
    process = subprocess.Popen(['make', 'backend-restart'])
    time.sleep(5) #allow some time for the server to start
    return process



def test_downloaded_repos(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repos')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_repo_groups(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

#####################################
###           EVOLUTION           ###
#####################################

def test_code_changes_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21350/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_lines_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_code_changes_lines_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21350/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_issues_new_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_new_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21350/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] >= 1

def test_issues_closed_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_closed_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21350/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issue_backlog_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/issue-backlog')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issue_backlog'] > 0

def test_issue_backlog_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/23/repos/21350/issue-backlog')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issue_backlog'] > 0

def test_pull_requests_merge_contributor_new_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_pull_requests_merge_contributor_new_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21524/pull-requests-merge-contributor-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_opened_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-first-time-opened')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_opened_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/22054/issues-first-time-opened')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_closed_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-first-time-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_first_time_closed_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21524/issues-first-time-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_sub_projects_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/sub-projects')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_protject_count"] > 0

def test_sub_projects_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21477/sub-projects')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_protject_count"] > 0

def test_contributors_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0


def test_contributors_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/contributors')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["total"] > 0

def test_contributors_new_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0


def test_contributors_new_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21524/contributors-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["count"] > 0

def test_issues_open_age_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-open-age/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["open_date"] > 1

def test_issues_open_age_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-open-age/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["open_date"] > 1

def test_issues_closed_resolution_duration_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-closed-resolution-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["diffdate"] >= 0


def test_issues_closed_resolution_duration_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21682/issues-closed-resolution-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["diffdate"] >= 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-new-repo-in-repo-group/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] >= 0 