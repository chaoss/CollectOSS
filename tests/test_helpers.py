import pytest
import pandas as pd
from queue import Queue
from workers.util import read_config
from workers.worker_base import Worker

def test_dump_queues():
    sample_queue = Queue()
    list_sample = ["x@x.com", "y@y.com", "z@z.com"]
    for list_item in list_sample:
        sample_queue.put(list_item)
    queue_to_list = Worker.dump_queue(sample_queue)
    assert queue_to_list == ["x@x.com", "y@y.com", "z@z.com"]

def test_read_config_no_exception():
    db_name = read_config('Database', 'user', 'AUGUR_DB_USER', 'augur', config_file_path="augur.config.json")
    assert db_name == "augur"

def test_read_config_exception():
    with pytest.raises(AttributeError):
        db_name = read_config('Server', 'username')
