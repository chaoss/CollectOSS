import os
from pathlib import Path
from time import sleep
from unittest.mock import patch

import pytest
import requests
import sqlalchemy as s

from workers.pull_request_analysis_worker.pull_request_analysis_worker import PullRequestAnalysisWorker
from workers.worker_base import Worker


@pytest.fixture
def training_files():
    data_path = Path(os.path.dirname(os.getcwd())).parents[0]
    path = os.path.join(data_path, 'workers', 'pull_request_analysis_worker')
    return os.listdir(path)

def test_training_files(training_files):
    assert 'trained_pr_model.pkl' in training_files

@pytest.fixture
def test_task():
    return {
        "given": {
            "git_url": "https://github.com/chaoss/augur.git"
        },
        "models": ["pull_request_analysis"],
        "job_type": "MAINTAIN",
        "display_name": "pull request analysis model for url: https://github.com/chaoss/augur.git",
        "focused_task": 1
    }

@pytest.fixture
def test_config():
    config = {
        "offline_mode": True,
        "quiet": True
    }
    return config

@pytest.fixture
def pull_request_analysis_worker(test_config):
    pr_analysis_worker = PullRequestAnalysisWorker(config=test_config)
    return pr_analysis_worker

def test_pull_request_analysis_worker(pull_request_analysis_worker, test_task):
    assert pull_request_analysis_worker is not None
