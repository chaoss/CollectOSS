import os
import pytest
import datetime

@pytest.fixture(scope="module")
def facade():
    import augur
    augur_app = augur.Application()
    return augur_app['facade']()

def test_downloaded_repos(facade):
    assert facade.downloaded_repos()["project_name"].iloc[0] == "Twitter"
    assert facade.downloaded_repos()["url"].iloc[0] == "github.com/twitter/twemoji"
    assert facade.downloaded_repos()["status"].iloc[0] == "Complete"
    assert facade.downloaded_repos()["base64_url"].iloc[0] == b"Z2l0aHViLmNvbS90d2l0dGVyL3R3ZW1vamk="

def test_lines_changed_by_author(facade):
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["author_email"].iloc[0] == "caniszczyk@gmail.com"
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["author_date"].iloc[0] == "2014-11-06"
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["affiliation"].iloc[0] == "(Unknown)"
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["additions"].iloc[0] == 7
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["deletions"].iloc[0] == 4
    assert facade.lines_changed_by_author("github.com/twitter/twemoji")["whitespace"].iloc[0] == 2

def test_lines_changed_by_week(facade):
    assert facade.lines_changed_by_week("github.com/twitter/twemoji")["date"].iloc[0] == datetime.date(2014, 11, 7)
    assert facade.lines_changed_by_week("github.com/twitter/twemoji")["additions"].iloc[0] == 1263564
    assert facade.lines_changed_by_week("github.com/twitter/twemoji")["deletions"].iloc[0] == 1834
    assert facade.lines_changed_by_week("github.com/twitter/twemoji")["whitespace"].iloc[0] == 27375

def test_lines_changed_by_month(facade):
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["author_email"].iloc[0] == "gudian@adobe.com"
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["affiliation"].iloc[0] == "Adobe"
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["month"].iloc[0] == 7
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["year"].iloc[0] == 2017
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["additions"].iloc[0] == 5361
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["deletions"].iloc[0] == 46
    assert facade.lines_changed_by_month("github.com/adobe/s3mock")["whitespace"].iloc[0] == 875

def test_commits_by_week(facade):
    assert facade.commits_by_week("github.com/adobe/s3mock")["author_email"].iloc[0] == "gudian@adobe.com"
    assert facade.commits_by_week("github.com/adobe/s3mock")["affiliation"].iloc[0] == "Adobe"
    assert facade.commits_by_week("github.com/adobe/s3mock")["week"].iloc[0] == 29
    assert facade.commits_by_week("github.com/adobe/s3mock")["year"].iloc[0] == 2017
    assert facade.commits_by_week("github.com/adobe/s3mock")["patches"].iloc[0] == 1
