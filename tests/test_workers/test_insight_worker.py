import pytest
from time import sleep
import logging
import sys
from workers.insight_worker.insight_worker import InsightWorker

from unittest.mock import patch
@pytest.fixture
def test_task():
    return {
        "given": {
            "git_url": "https://github.com/chaoss/augur.git"
        },
        "models": ["insights"],
        "job_type": "MAINTAIN",
        "display_name": "insights model model for url: https://github.com/chaoss/augur.git",
        "focused_task": 1
    }
@pytest.fixture
def test_config():

    return {
        
        "anomaly_days": 30,
        "contamination": 0.1,
        "metrics": [
            "code-changes",
            "code-changes-lines",
            "contributors-new",
            "issues-new",
            "reviews"
        ],
        "training_days": 365
        
    }

@pytest.fixture
def insight_worker(test_config):
    
    insight_worker = InsightWorker(config=test_config)
    return insight_worker

def test_insight_worker(insight_worker,test_task):

    assert insight_worker is not None

    
@patch('workers.insight_worker.insight_worker.InsightWorker.register_task_completion')
def test_insight_model(mock_function, test_task,test_config):

    assert InsightWorker(config=test_config).insights_model(test_task,10) is None