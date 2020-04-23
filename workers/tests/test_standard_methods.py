# Sample Test passing with nose and pytest
import pandas as pd
import pytest
from workers.standard_methods import check_duplicates, dump_queue, read_config
from queue import Queue


def test_check_duplicates():
    obj = {"website":["walmart.com"]}
    new_data = [obj]
    table_values = pd.read_csv("augur/data/companies.csv")
    assert check_duplicates(new_data, table_values, "website") == [obj]

def test_dump_queues():
    sample_queue = Queue()
    list_sample = ["x@x.com", "y@y.com", "z@z.com"]
    for list_item in list_sample:
        sample_queue.put(list_item)
    queue_to_list = dump_queue(sample_queue)
    assert queue_to_list == ["x@x.com", "y@y.com", "z@z.com"]

def test_read_config_no_exception():
    db_name = read_config('Database', 'user', 'AUGUR_DB_USER', 'augur',config_file_path="augur.config.json")
    assert db_name == "augur"

def test_read_config_exception():
    with pytest.raises(AttributeError):
        db_name = read_config('Server', 'username')
