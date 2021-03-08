#SPDX-License-Identifier: MIT
import pytest
from time import sleep

from workers.repo_info_worker.repo_info_worker import RepoInfoWorker

@pytest.fixture
def test_task():
    return {
        "given": {
            "github_url": "https://github.com/chaoss/augur.git"
        },
        "models": ["repo_info"],
        "job_type": "MAINTAIN",
        "display_name": "repo_info model for url: https://github.com/chaoss/augur.git",
        "focused_task": 1
    }

@pytest.fixture
def repo_info_worker():
    config = {
        "offline_mode": True,
        "quiet": True
    }

    repo_info_worker = RepoInfoWorker(config=config)
    return repo_info_worker

def test_repo_info_worker(repo_info_worker, test_task):
    assert repo_info_worker is not None
