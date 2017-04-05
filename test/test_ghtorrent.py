import os
import pytest
import pandas

@pytest.fixture
def ghtorrent():
    import ghdata
    dbstr = os.getenv("DB_TEST_URL")
    assert dbstr is not None and len(dbstr) > 8
    return ghdata.GHTorrent(dbstr)

def test_repoid(ghtorrent):
    assert ghtorrent.repoid('rails', 'rails') == 78852

def test_userid(ghtorrent):
    assert ghtorrent.userid('howderek') == 417486

"""
Pandas testing format

assert ghtorrent.<function>(ghtorrent.repoid('owner', 'repo')).isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe
"""
def test_stargazers(ghtorrent):
    assert ghtorrent.stargazers(ghtorrent.repoid('akka', 'akka')).isin(["2011-09-14"]).any

def test_commits(ghtorrent):
    assert ghtorrent.commits(ghtorrent.repoid('facebook', 'folly')).isin(["2013-01-07"]).any

def test_forks(ghtorrent):
    assert ghtorrent.forks(ghtorrent.repoid('facebook', 'hiphop-php')).isin(["2012-01-08"]).any

def test_issues(ghtorrent):
    assert ghtorrent.issues(ghtorrent.repoid('mongodb', 'mongo')).isin(["2013-01-05"]).any

def test_issues_with_close(ghtorrent):
    assert ghtorrent.issues_with_close(ghtorrent.repoid('TrinityCore', 'TrinityCore')).isin(["2012-01-08"]).any

def test_contributors(ghtorrent):
    assert ghtorrent.contributors(ghtorrent.repoid('TTimo', 'doom3.gpl')).isin(["sergiocampama"]).any

def test_contributions(ghtorrent):
    assert ghtorrent.contributions(ghtorrent.repoid('ariya', 'phantomjs')).isin(["ariya"]).any

def test_committer_locations(ghtorrent):
    assert ghtorrent.committer_locations(ghtorrent.repoid('mavam', 'stat-cookbook')).isin(["Berkeley, CA"]).any

def test_issue_response_time(ghtorrent):
    assert ghtorrent.issue_response_time(ghtorrent.repoid('hadley', 'devtools')).isin(["2013-09-16 17:00:54"]).any

def test_pull_acceptance_rate(ghtorrent):
    assert ghtorrent.pull_acceptance_rate(ghtorrent.repoid('akka', 'akka')).isin([0.5]).any
