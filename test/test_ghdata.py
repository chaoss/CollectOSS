import os
import pytest
import pandas

@pytest.fixture
def gh():
    import ghdata
    return ghdata.GHData(os.getenv("DB_TEST_URL"))

def test_repoid(gh):
    assert gh.repoid('rails', 'rails') == 78852

def test_userid(gh):
    assert gh.userid('howderek') == 417486

"""
Pandas testing format

assert gh.<function>('<repoid>, <userid>').isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""
def test_stargazers(gh):
    assert gh.stargazers('1').isin(["2011-09-14"]).any

def test_commits(gh):
    assert gh.commits('8').isin(["2013-01-07"]).any

def test_forks(gh):
    assert gh.forks('5').isin(["2012-01-08"]).any

def test_issues(gh):
    assert gh.issues('9').isin(["2013-01-05"]).any

def test_issues_with_close(gh):
    assert gh.issues_with_close('12').isin(["2012-01-08"]).any

def test_contributors(gh):
    assert gh.contributors('10').isin(["sergiocampama"]).any

def test_contributions(gh):
    assert gh.contributions(11, '15').isin(["ariya"]).any

def test_committer_locations(gh):
    assert gh.committer_locations('4').isin(["Berkeley, CA"]).any

def test_issue_response_time(gh):
    assert gh.issue_response_time('2').isin(["2013-09-16 17:00:54"]).any

def test_linking_websites(gh):
    assert gh.linking_websites('6').isin(["sohu.com"]).any
