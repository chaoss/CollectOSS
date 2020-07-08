import pytest
import os
import pandas as pd
from queue import Queue
from workers.util import read_config
from workers.worker_base import Worker
from augur.config import AugurConfig, default_config
from augur import ROOT_AUGUR_DIRECTORY

def test_dump_queues():
    sample_queue = Queue()
    list_sample = ["x@x.com", "y@y.com", "z@z.com"]
    for list_item in list_sample:
        sample_queue.put(list_item)
    queue_to_list = Worker.dump_queue(sample_queue)
    assert queue_to_list == ["x@x.com", "y@y.com", "z@z.com"]

def test_read_config_no_exception():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    print(base_dir)
    db_name = read_config('Database', 'user', 'AUGUR_DB_USER', 'augur', config_file_path=base_dir+"/augur.config.json")
    assert db_name == "augur"

def test_read_config_exception():
    with pytest.raises(AttributeError):
        db_name = read_config('Server', 'username')

def test_config_get_section_no_exception():
    test_config = default_config
    test_config['Database']['user'] = "test_user"
    config_object = AugurConfig(ROOT_AUGUR_DIRECTORY, test_config)
    assert type(config_object.get_section("Database")) == dict

def test_config_get_section_exception():
    test_config = default_config
    test_config['Database']['user'] = "test_user"
    config_object = AugurConfig(ROOT_AUGUR_DIRECTORY, test_config)
    with pytest.raises(KeyError):
        config_object.get_section("absent_section")





