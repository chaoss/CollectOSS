# SPDX-License-Identifier: MIT
"""PR collection must skip repos with PRs disabled or missing instead of crashing."""
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.pull_requests.tasks import retrieve_all_pr_data


@pytest.mark.unit
@pytest.mark.parametrize("scenario, expected_prs", [
    ("normal", [{"number": 1}]),
    ("issues_disabled", [{"number": 1}]),
    ("prs_disabled", []),
    ("issues_and_prs_disabled", []),
    ("repo_not_found", []),
])
def test_pr_collection(fake_github, scenario, expected_prs):
    """Failure means PR collection crashes, returns the wrong PRs, or fetches
    the PR list from a repo without pull requests."""
    gh = fake_github(scenario)
    prs = list(retrieve_all_pr_data("https://github.com/owner/repo", Mock(), None, None))
    assert prs == expected_prs

    fetched_list = ("GET", "/repos/owner/repo/pulls") in gh.requests
    assert fetched_list == bool(expected_prs), (
        "the PR list should only be fetched when pull requests are enabled")
