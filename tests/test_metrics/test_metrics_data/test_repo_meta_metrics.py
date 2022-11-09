#SPDX-License-Identifier: MIT

import pytest
import pandas as pd

from augur.api.metrics.repo_meta import *
from augur.api.metrics.contributor import lines_changed_by_author


def test_code_changes():
    #repo_id
    assert code_changes(10, 25430, period='year').isin([pd.Timestamp('2019-01-01T00:00:00+00:00'), 2]).any().any()

    # repo_group_id
    assert code_changes(10, period='year').isin([pd.Timestamp('2019-01-01T00:00:00+00:00'), 21350, 2]).any().any()

    #begin_date & end_date
    assert code_changes(10, 25430, begin_date='2019',
                                      end_date='2019-05').isin([pd.Timestamp('2019-03-01'), 2]).any().any()
    assert code_changes(10, begin_date='2019',
                                 end_date='2019-05').isin([pd.Timestamp('2019-03-06'), 21410, 4]).any().any()

def test_code_changes_lines():
    #repo_id
    assert code_changes_lines(10, 25430, period='year').isin([pd.Timestamp('2019-01-01T00:00:00+00:00'), 27190, 3163]).any().any()

    #repo_group_id
    assert code_changes_lines(10, period='year').isin([pd.Timestamp('2019-01-01T00:00:00+00:00'), 21410, 31, 3]).any().any()

    #begin_date & end_date
    assert code_changes_lines(10, 25430, period='month', begin_date='2019',
                                       end_date='2019-05').isin([pd.Timestamp('2019-02-01T00:00:00+00:00'), 196, 108]).any().any()
    assert code_changes_lines(10, period='month', begin_date='2019-05',
                                       end_date='2019-08-15').isin([pd.Timestamp('2019-06-01T00:00:00+00:00'), 25430, 70, 20]).any().any()

def test_sub_projects():

    # repo group
    assert sub_projects(10).iloc[0]['sub_project_count'] > 0

    # repo id
    assert sub_projects(
        10, repo_id=25430).iloc[0]['sub_project_count'] > 0

def test_lines_changed_by_author():
    assert lines_changed_by_author(10).iloc[0].additions > 0
    assert lines_changed_by_author(10, 25430).iloc[0].additions > 0

def test_cii_best_practices_badge():
    # repo
    assert int(cii_best_practices_badge(10, 25430).iloc[0]['tiered_percentage']) >= 85

def test_languages():
    # TODO
    pass

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group():
    pass
    # these tests break in 2020
    # assert annual_lines_of_code_count_ranked_by_repo_in_repo_group(20).iloc[0].net > 0
    # assert annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, timeframe = 'year').iloc[0].net > 0
    # assert annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, 25430).iloc[0].net > 0
    # assert annual_lines_of_code_count_ranked_by_repo_in_repo_group(10, 25430,timeframe = 'year').iloc[0].net > 0

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group():
    pass
    # assert annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(20).iloc[0].net > 0
    # assert annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(10, 25430).iloc[0].net > 0

def test_aggregate_summary():
    assert aggregate_summary(10).iloc[0]['commit_count'] > 0
    assert aggregate_summary(10, 25430,begin_date='2018-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').iloc[0]['commit_count'] > 0

# def test_license_declared():
#     assert license_declared(21).iloc[0]['name']
#     assert license_declared(10, 21116).iloc[0]['name']

# def test_license_count():
#     assert license_count(21).iloc[0]['number_of_license'] >= 1
#     assert license_count(10, 21116).iloc[0]['number_of_license'] >= 1

# def test_license_coverage():
#     assert license_coverage(21).iloc[0]['total_files'] >= 1
#     assert license_coverage(10, 21116).iloc[0]['total_files'] >= 1


