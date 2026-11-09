# SPDX-License-Identifier: MIT
"""Message collection on repos with issues and/or pull requests disabled."""
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.messages import fast_retrieve_all_pr_and_issue_messages
from collectoss.tasks.github.util.github_data_access import UrlNotFoundException

COMMENT = {"id": 1, "body": "hello"}


def collect_messages():
    return fast_retrieve_all_pr_and_issue_messages(
        "https://github.com/owner/repo", Mock(), None, "test", None)


@pytest.mark.unit
@pytest.mark.parametrize("scenario", ["normal", "issues_disabled"])
def test_comments_are_collected(fake_github, scenario):
    # /issues/comments also holds PR comments, so it works with issues disabled.
    fake_github(scenario)
    assert collect_messages() == [COMMENT]


# Known crash (#503). Remove the xfail marker once it is fixed.
@pytest.mark.unit
@pytest.mark.xfail(strict=True, raises=UrlNotFoundException, reason="#503")
def test_no_messages_when_issues_and_prs_disabled(fake_github):
    fake_github("issues_and_prs_disabled")
    assert collect_messages() == []
