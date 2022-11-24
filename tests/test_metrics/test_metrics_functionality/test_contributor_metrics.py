#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from augur.api.metrics.contributor import *

df_type = type(pd.DataFrame())

def test_contributors():
    # repo group
    assert isinstance(contributors(20), df_type)

    # repo id
    assert isinstance(contributors(
        10, repo_id=25430), df_type)

    # test begin_date and end_date
    assert isinstance(contributors(10, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59'), df_type)

    assert isinstance(contributors(10, repo_id=25430, begin_date='2019-6-1 00:00:01',
                                 end_date='2019-06-10 23:59:59'), df_type)

def test_contributors_new():
    assert isinstance(contributors_new(10, repo_id=25430, period='year'), df_type)

    # repo_group_id
    assert isinstance(contributors_new(10, period='year'), df_type)

    # begin_date and end_date
    assert isinstance(contributors_new(10, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59'), df_type)

    assert isinstance(contributors_new(10, repo_id=25430, period='year', begin_date='2019-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59'), df_type)
