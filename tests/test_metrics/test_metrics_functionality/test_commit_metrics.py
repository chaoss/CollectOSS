#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from augur.api.metrics.commit import *

df_type = type(pd.DataFrame())

def test_annual_commit_count_ranked_by_repo_in_repo_group():
    assert isinstance(annual_commit_count_ranked_by_repo_in_repo_group(10), df_type)
    assert isinstance(annual_commit_count_ranked_by_repo_in_repo_group(10, 25430), df_type)

def test_annual_commit_count_ranked_by_new_repo_in_repo_group():
    assert isinstance(annual_commit_count_ranked_by_new_repo_in_repo_group(10), df_type)
    assert isinstance(annual_commit_count_ranked_by_new_repo_in_repo_group(10, 25430), df_type)

def test_top_committers():

    assert isinstance(top_committers(10, year=2017), df_type)
    assert isinstance(top_committers(10, year=2017, threshold=0.7), df_type)
    assert isinstance(top_committers(10, 25430, year=2017), df_type)
    assert isinstance(top_committers(10, 25430, year=2017, threshold=0.7), df_type)
    assert isinstance(top_committers(10), df_type)
    assert isinstance(top_committers(10, 25430), df_type)


def test_committer():
    assert isinstance(committers(10, period='year'), df_type)
    assert isinstance(committers(10, 25430,period='year'), df_type)

