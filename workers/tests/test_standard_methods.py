# Sample Test passing with nose and pytest
import pandas as pd
import pytest
from workers.standard_methods import check_duplicates


def test_check_duplicates():
    obj = {"website":["walmart.com"]}
    new_data = [obj]
    table_values = pd.read_csv("../../augur/data/companies.csv")
    assert check_duplicates(new_data, table_values, "website") == [obj]
