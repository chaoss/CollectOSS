import pytest
from time import sleep
#from workers.discourse_analysis_worker.discourse_analysis_worker import DiscourseAnalysisWorker
from augur import ROOT_AUGUR_DIRECTORY
import os
from workers.util import read_config
from augur.config import AugurConfig

@pytest.fixture
def test_task():
    return {
        "given": {
            "github_url": "https://github.com/chaoss/augur.git"
        },
        "models": ["discourse_analysis"],
        "job_type": "MAINTAIN",
        "display_name": "discourse analysis model for url: https://github.com/chaoss/augur.git",
        "focused_task": 1
    }
'''
@pytest.fixture
def discourse_analysis_worker():
    config = {
        "offline_mode": True,
        "quiet": True
    }

    discourse_analysis_worker = DiscourseAnalysisWorker(config=config)
    return discourse_analysis_worker
'''
@pytest.fixture
def worker_files():
    return set(os.listdir(os.path.join(ROOT_AUGUR_DIRECTORY,"workers","discourse_analysis_worker")))    
'''
def test_discourse_analysis_worker(discourse_analysis_worker, test_task):
    assert discourse_analysis_worker is not None
'''
def test_map_exists(worker_files):
    assert len(worker_files & set(["word_to_emotion_map","trained_crf_model","tfidf_transformer"]))==3

def test_configuration(worker_files):
    augur_config = AugurConfig(ROOT_AUGUR_DIRECTORY)
    assert (['port','switch','workers'] == list(augur_config.get_section("Workers")["discourse_analysis_worker"].keys()))
