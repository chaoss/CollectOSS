import os
import pytest

@pytest.fixture(scope="module")
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
def test_closed_issues(ghtorrent):
    assert ghtorrent.closed_issues('cashmusic', 'platform').isin(["2012-11-09T00:00:00.000Z"]).any

def test_code_commits(ghtorrent):
    assert ghtorrent.code_commits('facebook', 'folly').isin(["2013-01-07"]).any

def test_code_review_iteration(ghtorrent):
    assert ghtorrent.code_review_iteration('apache', 'spark').isin(["2015-05-22T00:00:00.000Z"]).any

def test_contribution_acceptance(ghtorrent):
    assert ghtorrent.contribution_acceptance('rails', 'rails').isin(["2012-05-16T00:00:00.000Z"]).any

def test_contributing_github_organizations(ghtorrent):
    assert ghtorrent.contributing_github_organizations('rails', 'rails').isin(["4066"]).any

def test_first_response_to_issue_duration(ghtorrent):
    assert ghtorrent.first_response_to_issue_duration('AudioKit', 'AudioKit').isin(["13000839"]).any

def test_forks(ghtorrent):
    assert ghtorrent.forks('facebook', 'hiphop-php').isin(["2012-01-08"]).any

def test_maintainer_response_to_merge_request_duration(ghtorrent):
    assert ghtorrent.maintainer_response_to_merge_request_duration('rails', 'rails').isin(["2011-05-10T00:00:00.000Z"]).any
 
def test_new_contributing_github_organizations(ghtorrent):
    assert ghtorrent.new_contributing_github_organizations('rails', 'rails').isin(["4066"]).any

def test_open_issues(ghtorrent):
    assert ghtorrent.open_issues('mongodb', 'mongo').isin(["2013-01-05"]).any

def test_pull_request_comments(ghtorrent):
    assert ghtorrent.pull_request_comments('rails', 'rails').isin(["2011-11-15T00:00:00.000Z"]).any 

def test_pull_requests_open(ghtorrent):
    assert ghtorrent.pull_requests_open('rails', 'rails').isin(["2013-01-09T00:00:00.000Z"]).any

# *** RISK *** #

# *** VALUE *** #

# *** ACTIVITY *** #

def test_watchers(ghtorrent):
    assert ghtorrent.watchers('rails', 'rails').isin(["2017-08-23T00:00:00.000Z"]).any

def test_issue_comments(ghtorrent):
    assert ghtorrent.issue_comments('rails', 'rails').isin(["2009-04-05T00:00:00.000Z"]).any

# *** EXPERIMENTAL *** #

def test_commits100(ghtorrent):
    assert ghtorrent.commits100('rails', 'rails').isin(["2017-08-13T00:00:00.000Z"]).any

def test_commit_comments(ghtorrent):
    assert ghtorrent.commit_comments('rails', 'rails').isin(["2008-07-10T00:00:00.000Z"]).any

def test_committer_locations(ghtorrent):
    assert ghtorrent.committer_locations('mavam', 'stat-cookbook').isin(["Berkeley, CA"]).any

def test_total_committers(ghtorrent):
    assert ghtorrent.total_committers('rails', 'rails').isin(["2004-11-24T00:00:00.000Z"]).any

def test_issue_activity(ghtorrent):
    assert ghtorrent.issue_activity('bitcoin', 'bitcoin').isin(["2010-12-20T00:00:00.000Z"]).any

def test_pull_acceptance_rate(ghtorrent):
    assert ghtorrent.pull_request_acceptance_rate('akka', 'akka').isin([0.5]).any

# def test_community_age(ghtorrent):
#     assert ghtorrent.community_age('TEST', 'TEST').isin(["DATE"]).any

def test_community_engagement(ghtorrent):
    assert ghtorrent.community_engagement('rails', 'rails').isin(["2010-09-11T00:00:00.000Z"]).any

def test_contributions(ghtorrent):
    assert ghtorrent.contributions('ariya', 'phantomjs').isin(["ariya"]).any

def test_contributors(ghtorrent):
    assert ghtorrent.contributors('TTimo', 'doom3.gpl').isin(["sergiocampama"]).any 

def test_project_age(ghtorrent):
    assert ghtorrent.project_age('rails', 'rails').isin(["2008-04-11T00:00:00.000Z"]).any

def test_fakes(ghtorrent):
    assert ghtorrent.fakes('rails', 'rails').isin(["2008-09-24T00:00:00.000Z"]).any







