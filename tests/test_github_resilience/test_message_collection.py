# SPDX-License-Identifier: MIT
"""Message collection on repos with issues and/or pull requests disabled."""
import logging
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.messages import (
    fast_retrieve_all_pr_and_issue_messages,
    select_comment_urls,
)
from collectoss.tasks.github.util.github_data_access import (
    GithubDataAccess,
    UrlNotFoundException,
)

COMMENT = {"id": 1, "body": "hello"}


def collect_messages():
    return fast_retrieve_all_pr_and_issue_messages(
        "https://github.com/owner/repo", Mock(), None, "test", None)


@pytest.mark.unit
@pytest.mark.parametrize("scenario", ["normal", "issues_disabled"])
def test_comments_are_collected(fake_github, scenario):
    """Failure means comments are being dropped. With issues disabled,
    /issues/comments still returns the pull request comments."""
    fake_github(scenario)
    assert collect_messages() == [COMMENT]


@pytest.mark.unit
def test_no_messages_when_issues_and_prs_disabled(fake_github):
    """When /issues/comments is unavailable (404), return no messages instead
    of raising UrlNotFoundException (#503)."""
    fake_github("issues_and_prs_disabled")
    assert collect_messages() == []


@pytest.mark.unit
def test_select_comment_urls_keeps_prs_when_issues_disabled():
    """When Issues are off, only PR comment URLs are fetched (shared numberspace)."""
    pr_urls = ["https://api.github.com/repos/o/r/issues/1/comments"]
    issue_urls = ["https://api.github.com/repos/o/r/issues/2/comments"]

    assert select_comment_urls(pr_urls, issue_urls, issues_enabled=True) == pr_urls + issue_urls
    assert select_comment_urls(pr_urls, issue_urls, issues_enabled=False) == pr_urls


@pytest.mark.unit
def test_check_issues_enabled_reraises_repo_not_found(fake_github):
    """Repo metadata 404 must not be treated as 'issues disabled' (#554 review)."""
    fake_github("repo_not_found")
    access = GithubDataAccess(Mock(), logging.getLogger("t"))

    with pytest.raises(UrlNotFoundException):
        access.check_issues_enabled("owner", "missing-repo")


@pytest.mark.unit
def test_check_issues_enabled_false_when_has_issues_false(fake_github):
    fake_github("issues_disabled")
    access = GithubDataAccess(Mock(), logging.getLogger("t"))
    assert access.check_issues_enabled("owner", "repo") is False
