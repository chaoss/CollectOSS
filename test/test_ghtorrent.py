import os
import pytest

@pytest.fixture
def ghtorrent():
    import augur
    augurApp = augur.Application()
    return augurApp.ghtorrent()

def test_repoid(ghtorrent):
    assert ghtorrent.repoid('rails', 'rails') >= 1000

def test_userid(ghtorrent):
    assert ghtorrent.userid('howderek') >= 1000

"""
Pandas testing format

assert ghtorrent.<function>('owner', 'repo').isin(['<data that should be in dataframe>']).any

The tests check if a value is anywhere in the dataframe

"""

# *** DIVERSITY AND INCLUSION *** #


# *** GROWTH, MATURITY, AND DECLINE *** #
def test_issues(ghtorrent):
    assert ghtorrent.issues('mongodb', 'mongo').isin(["2013-01-05"]).any

# issues closed

def test_issue_response_time(ghtorrent):
    assert ghtorrent.issue_response_time('hadley', 'devtools').isin([1]).any

def test_issues_with_close(ghtorrent):
    assert ghtorrent.issues_with_close('TrinityCore', 'TrinityCore').isin(["2012-01-08"]).any

def test_commits(ghtorrent):
    assert ghtorrent.commits('facebook', 'folly').isin(["2013-01-07"]).any

# time to first maintainer response

def test_forks(ghtorrent):
    assert ghtorrent.forks('facebook', 'hiphop-php').isin(["2012-01-08"]).any

# pulls

# pull request comments

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #
# watchers

#issue comments

# *** EXPERIMENTAL *** #

# commits100

# commit_comments

def test_committer_locations(ghtorrent):
    assert ghtorrent.committer_locations('mavam', 'stat-cookbook').isin(["Berkeley, CA"]).any

def test_issue_activity(ghtorrent):
    assert ghtorrent.issue_activity('bitcoin', 'bitcoin').isin(["2010-12-20T00:00:00.000Z"]).any

def test_pull_acceptance_rate(ghtorrent):
    assert ghtorrent.pull_acceptance_rate('akka', 'akka').isin([0.5]).any# commits100

def test_contributions(ghtorrent):
    assert ghtorrent.contributions('ariya', 'phantomjs').isin(["ariya"]).any

# community age

# community engagement

# fakes

def test_contributors(ghtorrent):
    assert ghtorrent.contributors('TTimo', 'doom3.gpl').isin(["sergiocampama"]).any 







