import pytest
from time import sleep
#from workers.clustering_worker.clustering_worker import ClusteringWorker
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
        "models": ["clustering"],
        "job_type": "MAINTAIN",
        "display_name": "clustering model for url: https://github.com/chaoss/augur.git",
        "focused_task": 1
    }

'''
@pytest.fixture
def clustering_worker():
    config = {
        "offline_mode": True,
        "quiet": True
    }

    clustering_worker = ClusteringWorker(config=config)
    return clustering_worker
'''
@pytest.fixture
def worker_files():
    return set(os.listdir(os.path.join(ROOT_AUGUR_DIRECTORY,"workers","clustering_worker")))    

'''
def test_clustering_worker(clustering_worker, test_task):
    assert clustering_worker is not None

'''

def test_configuration(worker_files):
    augur_config = AugurConfig(ROOT_AUGUR_DIRECTORY)
    assert (['port','switch','workers','max_df','max_features','min_df','num_clusters'] == list(augur_config.get_section("Workers")["clustering_worker"].keys()))
