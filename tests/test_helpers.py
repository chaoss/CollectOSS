import pytest
import os
import json
import pandas as pd
import tempfile
from queue import Queue
from workers.util import read_config
from workers.worker_base import Worker
from workers.worker_git_integration import WorkerGitInterfaceable
from augur.config import AugurConfig, default_config
from augur import ROOT_AUGUR_DIRECTORY

temp_dir = os.path.join(os.getcwd(), "util")
config_path = os.path.join(temp_dir, "test.config.json")
def test_dump_queues():
    sample_queue = Queue()
    list_sample = ["x@x.com", "y@y.com", "z@z.com"]
    for list_item in list_sample:
        sample_queue.put(list_item)
    queue_to_list = Worker.dump_queue(sample_queue)
    assert queue_to_list == ["x@x.com", "y@y.com", "z@z.com"]

def test_read_config_no_exception():
    test_config = default_config
    base_dir = os.path.dirname(os.path.dirname(__file__))
    print(base_dir)
    with open(config_path, "w") as f:
        json.dump(test_config, f)
    db_name = read_config('Database', 'user', 'AUGUR_DB_USER', 'augur', config_file_path=config_path)
    assert db_name == "augur"

def test_read_config_exception():
    with pytest.raises(AttributeError):
        db_name = read_config('Server', 'username')

def test_config_get_section_no_exception():
    test_config = default_config
    test_config['Database']['user'] = "test_user"
    config_object = AugurConfig(temp_dir, test_config)
    assert type(config_object.get_section("Database")) == dict

def test_config_get_section_exception():
    test_config = default_config
    test_config['Database']['user'] = "test_user"
    config_object = AugurConfig(temp_dir, test_config)
    assert config_object.get_section("absent_section") == None

def test_discover_config_file_env_exception():
    os.environ['AUGUR_CONFIG_FILE'] = os.path.join(temp_dir, "augur.config.json")
    test_config = default_config
    with pytest.raises(FileNotFoundError):
        config_object = AugurConfig(temp_dir, test_config)
        assert config_object.discover_config_file()

def test_discover_config_file_env_no_exception():
    test_config = default_config
    with open(os.path.join(temp_dir, "augur.config.json"), "w") as f:
        pass
    config_object = AugurConfig(temp_dir, test_config)
    assert config_object.discover_config_file() == os.path.join(temp_dir, "augur.config.json")




