# Sample Test passing with nose and pytest
import pandas as pd
import pytest
from github_worker.helpers import Helpers


def test_check_duplicates():
    gh_worker = Helpers()
    obj = {"website":["walmart.com"]}
    new_data = [obj]
    table_values = pd.read_csv("../../../augur/data/companies.csv")
    assert gh_worker.check_duplicates(new_data, table_values, "website") == [obj]
