import pytest
import requests
from time import sleep

from workers.gitlab_issues_worker.gitlab_issues_worker import GitLabIssuesWorker
from workers.worker_base import Worker
@pytest.fixture
def test_task():
    return {
        "given": {
            "git_url": "https://gitlab.com/NickBusey/HomelabOS"
        },
        "models": ["issues"],
        "job_type": "MAINTAIN",
        "display_name": "issues model for url: https://gitlab.com/NickBusey/HomelabOS",
        "focused_task": 1
    }

@pytest.fixture
def gitlab_issues_worker():
    config = {
        "offline_mode": True,
        "quiet": True
    }

    gitlab_issues_worker = GitLabIssuesWorker(config=config)
    return gitlab_issues_worker

# def test_gitlab_issues_worker(gitlab_issues_worker, test_task):
#     gitlab_issues_worker._queue.put(test_task)
#     gitlab_issues_worker.collect()

#     print('collection done')
#     issues = requests.get('https://gitlab.com/api/v4/projects/6853087/issues', headers=gitlab_issues_worker.headers)
#     issues_list = issues.json()
#     id_list = [issue['_id'] for issue in issues_list]

#     table_ids_list = gitlab_issues_worker.get_table_values([gh_issue_id], [issues])

#     assert id_list == table_ids_list.index.tolist()

    
    