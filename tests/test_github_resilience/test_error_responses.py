# SPDX-License-Identifier: MIT
"""How the GitHub REST client reports unusual responses to collectors."""
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.util.github_data_access import (
    GithubDataAccess, ResourceGoneException, UrlNotFoundException,
)


def client():
    return GithubDataAccess(None, Mock())


@pytest.mark.unit
def test_404_raises_url_not_found(fake_github):
    fake_github("repo_not_found")
    with pytest.raises(UrlNotFoundException):
        client().get_resource("https://api.github.com/repos/owner/repo")


@pytest.mark.unit
def test_410_raises_resource_gone_with_github_message(fake_github):
    fake_github("issues_disabled")
    with pytest.raises(ResourceGoneException, match="Issues are disabled"):
        client().get_resource("https://api.github.com/repos/owner/repo/issues/1/comments")


@pytest.mark.unit
@pytest.mark.parametrize("scenario, expected", [
    ("normal", True),
    ("prs_disabled", False),
    ("issues_and_prs_disabled", False),
    # Current behavior, not a requirement.
    ("repo_not_found", False),
])
def test_check_prs_enabled(fake_github, scenario, expected):
    fake_github(scenario)
    assert client().check_prs_enabled("owner", "repo") is expected


@pytest.mark.unit
def test_respond_overrides_the_scenario(fake_github):
    gh = fake_github("normal")
    gh.respond(r"/pulls$", 404, {"message": "Not Found"})
    assert client().check_prs_enabled("owner", "repo") is False


@pytest.mark.unit
def test_unknown_path_fails_the_test_even_if_the_error_is_caught(fake_github):
    gh = fake_github("normal")
    try:
        client().get_resource("https://api.github.com/repos/owner/repo/releases")
    except Exception:
        pass  # as a collector with a broad except would
    assert set(gh.unmatched) == {"GET /repos/owner/repo/releases"}
    gh.unmatched.clear()  # asserted above; skip the teardown check
