import os
from pathlib import Path
from time import sleep
from unittest.mock import patch

import pytest
import requests
import sqlalchemy as s

from workers.message_insights_worker.message_insights_worker import \
    MessageInsightsWorker
from workers.worker_base import Worker


@pytest.fixture
def training_files():
    data_path = Path(os.path.dirname(os.getcwd())).parents[0]
    path = os.path.join(data_path, 'workers', 'message_insights_worker', 'train_data')
    return os.listdir(path)

def test_training_files(training_files):
    assert training_files == ['EmoticonLookupTable.txt', 'doc2vec.model', 'custom_dataset.xlsx']

@pytest.fixture
def test_task():
    return {
        "given": {
            "git_url": "https://github.com/chaoss/augur.git"
        },
        "models": ["message_analysis"],
        "job_type": "MAINTAIN",
        "display_name": "message analysis model for url: https://github.com/chaoss/augur.git",
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
def message_insights_worker(test_config):
    message_insights_worker = MessageInsightsWorker(config=test_config)
    return message_insights_worker

def test_message_insights_worker(message_insights_worker, test_task):
    assert message_insights_worker is not None
