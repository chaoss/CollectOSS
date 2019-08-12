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

def test_repos_in_repo_groups(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_get_repo_for_dosocs(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/dosocs/repos')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

#####################################
###           EVOLUTION           ###
#####################################

def test_code_changes_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/code-changes')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commit_count'] > 0

def test_code_changes_lines_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_code_changes_lines_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/code-changes-lines')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['added'] >= 0
    assert data[0]['removed'] >= 0

def test_issues_new_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_new_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-new')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_active_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-active')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_active_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-active')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_closed_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issues_closed_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21681/issues-closed')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issues'] > 0

def test_issue_duration_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-duration')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_duration_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21009/issue-duration')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_issue_participants_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-participants')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['participants'] > 0

def test_issue_participants_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issue-participants')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['participants'] > 0

def test_issue_throughput_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-throughput')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['throughput'] >= 0

def test_issue_throughput_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21682/issue-throughput')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['throughput'] >= 0

def test_issue_backlog_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issue-backlog')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['issue_backlog'] > 0

def test_issue_backlog_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21403/issue-backlog')
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
    assert data[0]["sub_project_count"] > 0

def test_sub_projects_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21477/sub-projects')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["sub_project_count"] > 0

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

def test_open_issues_count_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/open-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['open_count'] > 0

def test_open_issues_count_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/repos/21326/open-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['open_count'] > 0

def test_closed_issues_count_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/closed-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['closed_count'] > 0

def test_closed_issues_count_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/22/repos/21684/closed-issues-count')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['closed_count'] > 0

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

def test_issues_maintainer_response_duration_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/issues-maintainer-response-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["average_days_comment"] >= 0

def test_issues_maintainer_response_duration_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/issues-maintainer-response-duration/')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["average_days_comment"] >= 0
    assert data[0]["average_days_comment"] >= 0

def test_cii_best_practices_badge_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/cii-best-practices-badge')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_cii_best_practices_badge_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21252/cii-best-practices-badge')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_average_issue_resolution_time_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/average-issue-resolution-time')
    data = response.json()
    assert response.status_code == 200
    assert len(data) > 0

def test_average_issue_resolution_time_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21464/average-issue-resolution-time')
    data = response.json()
    assert response.status_code == 200
    assert len(data) > 0

def test_languages_by_group(augur_db_routes):
    # TODO need data
    pass

def test_languages_by_repo(augur_db_routes):
    # TODO need data
    pass

def test_license_declared_by_group(augur_db_routes):
    # TODO need more daa
    pass
    # response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/license-declared')
    # data = response.json()
    # assert response.status_code == 200
    # assert len(data) >= 1

def test_license_declared_by_repo(augur_db_routes):
    # TODO need more daa
    pass
    # response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21252/license-declared')
    # data = response.json()
    # assert response.status_code == 200
    # assert len(data) >= 1
    # assert data[0]["license"] == 'Apache-2.0'

def test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_commit_count_ranked_by_new_repo_in_repo_group_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_commit_count_ranked_by_repo_in_repo_group_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_commit_count_ranked_by_repo_in_repo_group_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-commit-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0


def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/repos/21000/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/20/annual-lines-of-code-count-ranked-by-repo-in-repo-group')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]["net"] > 0

def test_top_committers_by_repo(augur_db_routes):
    response = requests.get('http://0.0.0.0:5000/api/unstable/repo-groups/22/repos/21334/top-committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commits'] > 0

def test_top_committers_by_group(augur_db_routes):
    response = requests.get('http://0.0.0.0:5000/api/unstable/repo-groups/22/top-committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1
    assert data[0]['commits'] > 0

def test_committer_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/repos/21222/committers')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_committer_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/21/committers?period=year')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_aggregate_summary_by_repo(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/repos/21471/aggregate-summary')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1

def test_aggregate_summary_by_group(augur_db_routes):
    response = requests.get('http://localhost:5000/api/unstable/repo-groups/24/aggregate-summary')
    data = response.json()
    assert response.status_code == 200
    assert len(data) >= 1    
