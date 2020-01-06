#SPDX-License-Identifier: MIT

import pytest
import pandas as pd

@pytest.fixture(scope="module")
def metrics():
    import augur
    augur_app = augur.Application()
    return augur_app.metrics

def test_code_changes(metrics):
    #repo_id
    assert metrics.code_changes(23, 21350, period='year').isin([pd.Timestamp('2009-01-01T00:00:00+00:00'), 2]).any().any()

    # repo_group_id
    assert metrics.code_changes(23, period='year').isin([pd.Timestamp('2009-01-01T00:00:00+00:00'), 21350, 2]).any().any()

    #begin_date & end_date
    assert metrics.code_changes(23, 21350, period='month', begin_date='2009',
                                 end_date='2011-05').isin([pd.Timestamp('2009-02-01T00:00:00+00:00'), 2]).any().any()
    assert metrics.code_changes(23, period='month', begin_date='2009',
                                 end_date='2011-05').isin([pd.Timestamp('2011-02-01T00:00:00+00:00'), 21420, 4]).any().any()

def test_code_changes_lines(metrics):
    #repo_id
    assert metrics.code_changes_lines(22, 21331, period='year').isin([pd.Timestamp('2016-01-01T00:00:00+00:00'), 27190, 3163]).any().any()

    #repo_group_id
    assert metrics.code_changes_lines(23, period='year').isin([pd.Timestamp('2016-01-01T00:00:00+00:00'), 21420, 31, 3]).any().any()

    #begin_date & end_date
    assert metrics.code_changes_lines(22, 21331, period='month', begin_date='2016',
                                       end_date='2016-05').isin([pd.Timestamp('2016-02-01T00:00:00+00:00'), 196, 108]).any().any()
    assert metrics.code_changes_lines(22, period='month', begin_date='2016-05',
                                       end_date='2016-08-15').isin([pd.Timestamp('2016-06-01T00:00:00+00:00'), 21331, 70, 20]).any().any()

def test_sub_projects(metrics):

    # repo group
    assert metrics.sub_projects(20).iloc[0]['sub_project_count'] > 0

    # repo id
    assert metrics.sub_projects(
        20, repo_id=21000).iloc[0]['sub_project_count'] > 0

def test_lines_changed_by_author(metrics):
    assert metrics.lines_changed_by_author(20).iloc[0].additions > 0
    assert metrics.lines_changed_by_author(20,21000).iloc[0].additions > 0

def test_cii_best_practices_badge(metrics):
    # repo
    assert int(metrics.cii_best_practices_badge(21, 21000).iloc[0]['tiered_percentage']) >= 85

def test_languages(metrics):
    # TODO
    pass

def test_annual_lines_of_code_count_ranked_by_repo_in_repo_group(metrics):
    pass
    # these tests break in 2020
    # assert metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group(20).iloc[0].net > 0
    # assert metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group(20, timeframe = 'year').iloc[0].net > 0
    # assert metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group(20, 21000).iloc[0].net > 0
    # assert metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group(20, 21000,timeframe = 'year').iloc[0].net > 0

def test_annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(metrics):
    pass
    # assert metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(20).iloc[0].net > 0
    # assert metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group(20, 21000).iloc[0].net > 0

def test_aggregate_summary(metrics):
    assert metrics.aggregate_summary(24).iloc[0]['commit_count'] > 0
    assert metrics.aggregate_summary(24,21471,begin_date='2018-1-1 00:00:00',
                                     end_date='2019-12-31 23:59:59').iloc[0]['commit_count'] > 0

# def test_license_declared(metrics):
#     assert metrics.license_declared(21).iloc[0]['name']
#     assert metrics.license_declared(21, 21116).iloc[0]['name']

# def test_license_count(metrics):
#     assert metrics.license_count(21).iloc[0]['number_of_license'] >= 1
#     assert metrics.license_count(21, 21116).iloc[0]['number_of_license'] >= 1

# def test_license_coverage(metrics):
#     assert metrics.license_coverage(21).iloc[0]['total_files'] >= 1
#     assert metrics.license_coverage(21, 21116).iloc[0]['total_files'] >= 1


