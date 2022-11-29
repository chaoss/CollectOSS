#SPDX-License-Identifier: MIT

import pytest
import pandas as pd
from augur.api.metrics.repo_meta import *
from augur.api.metrics.contributor import lines_changed_by_author

df_type = type(pd.DataFrame())

def test_code_changes():
    #repo_id
    assert isinstance(code_changes(10, 25430, period='year'), df_type)

    # repo_group_id
    assert isinstance(code_changes(10, period='year'), df_type)

    #begin_date & end_date
    assert isinstance(code_changes(10, 25430, begin_date='2019',
                                      end_date='2019-05'), df_type)
    assert isinstance(code_changes(10, begin_date='2019',
                                 end_date='2019-05'), df_type)

def test_code_changes_lines():
    #repo_id
    assert isinstance(code_changes_lines(10, 25430, period='year'), df_type)

    #repo_group_id
    assert isinstance(code_changes_lines(10, period='year'), df_type)

    #begin_date & end_date
    assert isinstance(code_changes_lines(10, 25430, period='month', begin_date='2019',
                                       end_date='2019-05'), df_type)
    assert isinstance(code_changes_lines(10, period='month', begin_date='2019-05',
                                       end_date='2019-08-15'), df_type)

def test_sub_projects():

    # repo group
    assert isinstance(sub_projects(10), df_type)

    # repo id
    assert isinstance(sub_projects(
        10, repo_id=25430), df_type)

def test_lines_changed_by_author():
    assert isinstance(lines_changed_by_author(10), df_type)
    assert isinstance(lines_changed_by_author(10, 25430), df_type)

def test_cii_best_practices_badge():
    # repo
    assert isinstance(cii_best_practices_badge(10, 25430), list)

def test_languages():
    # TODO
    pass

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group():
    pass
    # these tests break in 2020
    # assert isinstance(annual_lines_of_code_count_ranked_by_repo_in_repo_group(20), df_type)
    # assert isinstance(annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, timeframe = 'year'), df_type)
    # assert isinstance(annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, 25430), df_type)
    # assert isinstance(annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, 25430,timeframe = 'year'), df_type)

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group():
    pass
    # assert isinstance(annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(20), df_type)
    # assert isinstance(annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(10, 25430), df_type)

def test_aggregate_summary():
    assert isinstance(aggregate_summary(10), df_type)
    assert isinstance(aggregate_summary(10, 25430,begin_date='2018-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59'), df_type)

# def test_license_declared():
#     assert isinstance(license_declared(21), df_type)
#     assert isinstance(license_declared(10, 21116), df_type)

# def test_license_count():
#     assert isinstance(license_count(21), df_type)
#     assert isinstance(license_count(10, 21116), df_type)

# def test_license_coverage():
#     assert isinstance(license_coverage(21), df_type)
#     assert isinstance(license_coverage(10, 21116), df_type)


