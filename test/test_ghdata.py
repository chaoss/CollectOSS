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

assert gh.<function>(gh.repoid('owner', 'repo')).isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""
def test_stargazers(gh):
    assert gh.stargazers(gh.repoid('akka', 'akka')).isin(["2011-09-14"]).any

def test_commits(gh):
    assert gh.commits(gh.repoid('facebook', 'folly')).isin(["2013-01-07"]).any

def test_forks(gh):
    assert gh.forks(gh.repoid('facebook', 'hiphop-php')).isin(["2012-01-08"]).any

def test_issues(gh):
    assert gh.issues(gh.repoid('mongodb', 'mongo')).isin(["2013-01-05"]).any

def test_issues_with_close(gh):
    assert gh.issues_with_close(gh.repoid('TrinityCore', 'TrinityCore')).isin(["2012-01-08"]).any

def test_contributors(gh):
    assert gh.contributors(gh.repoid('TTimo', 'doom3.gpl')).isin(["sergiocampama"]).any

def test_contributions(gh):
    assert gh.contributions(gh.repoid('ariya', 'phantomjs')).isin(["ariya"]).any

def test_committer_locations(gh):
    assert gh.committer_locations(gh.repoid('mavam', 'stat-cookbook')).isin(["Berkeley, CA"]).any

def test_issue_response_time(gh):
    assert gh.issue_response_time(gh.repoid('hadley', 'devtools')).isin(["2013-09-16 17:00:54"]).any

def test_linking_websites(gh):
    assert gh.linking_websites(gh.repoid('yihui', 'knitr')).isin(["sohu.com"]).any

def test_pull_acceptance_rate(gh):
    assert gh.pull_acceptance_rate(gh.repoid('akka', 'akka')).isin([0.5]).any
