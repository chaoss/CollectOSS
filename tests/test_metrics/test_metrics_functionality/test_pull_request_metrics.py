#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from augur.api.metrics.pull_request import *

df_type = type(pd.DataFrame())

def test_pull_requests_merge_contributor_new():
    # repo id
    assert isinstance(pull_requests_merge_contributor_new(10, repo_id=25430, period='year'), df_type)

    # repo_group_id
    assert isinstance(pull_requests_merge_contributor_new(10, period='year'), df_type)

    # begin_date and end_date
    assert isinstance(pull_requests_merge_contributor_new(10, period='year', begin_date='2019-1-1 00:00:00',
                                                        end_date='2019-12-31 23:59:59'), df_type)

def test_pull_request_acceptance_rate():
    assert isinstance(pull_request_acceptance_rate(20), df_type)
    assert isinstance(pull_request_acceptance_rate(10, 25430,begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59',group_by='year'), df_type)

def test_pull_request_closed_no_merge():
    assert isinstance(pull_requests_closed_no_merge(10), df_type)
    assert isinstance(pull_requests_closed_no_merge(10, 25430, begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59'), df_type)

