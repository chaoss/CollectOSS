# SPDX-License-Identifier: MIT
"""
Fake GitHub API for testing collectors against unusual repositories (issues or
PRs disabled, repo deleted) with no token, network, database or Redis.

    def test_something(fake_github):
        gh = fake_github("issues_and_prs_disabled")
        ...call a collector function and assert on the result...

See README.md for how to add a scenario.
"""
import os
import re
import sys
import types

import httpx
import pytest
from tenacity import wait_none
from unittest.mock import Mock

# issues.py reads this flag from the database at import time unless it is set.
os.environ.setdefault("COLLECTOSS_DEV", "1")

from collectoss.tasks.github.util import github_data_access as gda_module


def _task(*args, **kwargs):
    """Stand-in for @celery.task: tasks need a database, so calling one raises."""
    def decorate(func):
        def needs_database(*a, **kw):
            raise RuntimeError(
                f"{func.__name__} is a Celery task and needs a database. "
                "Test the helper function it calls instead."
            )
        return needs_database

    if len(args) == 1 and callable(args[0]) and not kwargs:  # bare @celery.task
        return decorate(args[0])
    return decorate


# The real celery_app module reads Redis settings from the database at import time.
_celery_stub = types.ModuleType("collectoss.tasks.init.celery_app")
_celery_stub.celery_app = Mock(task=_task)
for _name in ("CoreRepoCollectionTask", "SecondaryRepoCollectionTask",
              "FacadeRepoCollectionTask", "MLRepoCollectionTask"):
    setattr(_celery_stub, _name, type(_name, (), {}))
sys.modules.setdefault("collectoss.tasks.init.celery_app", _celery_stub)


REPO = r"^/repos/[^/]+/[^/]+$"
ISSUES = r"/issues$"
ISSUE_COMMENTS = r"/issues/\d+/comments$"  # one issue or PR
ALL_COMMENTS = r"/issues/comments$"        # whole repo, issues and PRs
PULLS = r"/pulls$"

NOT_FOUND = {"message": "Not Found"}
ISSUES_GONE = {"message": "Issues are disabled for this repo"}
COMMENT = {"id": 1, "body": "hello"}
PULL = {"number": 1}

# scenario -> [(path regex, status, JSON body)]; the first matching rule wins.
# "Observed" = checked against the real GitHub API on that repository and date.
SCENARIOS = {
    "normal": [
        (REPO, 200, {"has_issues": True, "has_pull_requests": True}),
        (ISSUE_COMMENTS, 200, [COMMENT]),
        (ALL_COMMENTS, 200, [COMMENT]),
        (ISSUES, 200, [{"number": 2}]),
        (PULLS, 200, [PULL]),
    ],
    # Observed 2026-11-09 on openshift/release.
    "issues_disabled": [
        (REPO, 200, {"has_issues": False, "has_pull_requests": True}),
        (ISSUE_COMMENTS, 410, ISSUES_GONE),
        (ALL_COMMENTS, 200, [COMMENT]),
        (ISSUES, 200, [{"number": 1, "pull_request": {}}]),
        (PULLS, 200, [PULL]),
    ],
    # Observed 2026-11-09 on kubernetes/apiextensions-apiserver.
    "issues_and_prs_disabled": [
        (REPO, 200, {"has_issues": False, "has_pull_requests": False}),
        (ISSUE_COMMENTS, 410, ISSUES_GONE),
        (ALL_COMMENTS, 404, NOT_FOUND),
        (ISSUES, 200, []),
        (PULLS, 404, NOT_FOUND),
    ],
    # Assumed: no public repository with only PRs disabled was found to check.
    "prs_disabled": [
        (REPO, 200, {"has_issues": True, "has_pull_requests": False}),
        (ISSUE_COMMENTS, 200, [COMMENT]),
        (ALL_COMMENTS, 200, [COMMENT]),
        (ISSUES, 200, [{"number": 2}]),
        (PULLS, 404, NOT_FOUND),
    ],
    # Observed 2026-11-09 on a repository name that does not exist.
    "repo_not_found": [
        (r"^/repos/", 404, NOT_FOUND),
    ],
}


class FakeGitHub:
    """Answers GitHub API requests from a list of rules and records them."""

    def __init__(self, rules):
        self.rules = list(rules)
        self.requests = []   # (method, path) of every request
        self.unmatched = []  # requests no rule could answer

    def respond(self, path_regex, status, body):
        """Add a rule that takes priority over the scenario's rules."""
        self.rules.insert(0, (path_regex, status, body))

    def handle(self, request: httpx.Request) -> httpx.Response:
        """Return the first matching rule's response, or 501 if none match."""
        path = request.url.path
        self.requests.append((request.method, path))
        for regex, status, body in self.rules:
            if re.search(regex, path):
                return httpx.Response(status, json=body)
        self.unmatched.append(f"{request.method} {path}")
        return httpx.Response(501, json={"message": "FakeGitHub has no rule for this path"})


@pytest.fixture
def fake_github(monkeypatch):
    """Route all GitHub HTTP calls to a FakeGitHub scenario."""
    real_client = httpx.Client
    started = []

    def start(scenario):
        gh = FakeGitHub(SCENARIOS[scenario])
        started.append(gh)
        monkeypatch.setattr(
            gda_module.httpx, "Client",
            lambda *a, **kw: real_client(transport=httpx.MockTransport(gh.handle)),
        )
        key_client = Mock(request=Mock(return_value="fake-token"))
        monkeypatch.setattr(gda_module, "KeyClient", Mock(return_value=key_client))
        # Keep the real retry logic but skip the 5s waits.
        retrying = gda_module.GithubDataAccess._GithubDataAccess__make_request_with_retries.retry
        monkeypatch.setattr(retrying, "wait", wait_none())
        return gh

    yield start

    # Fail even if the code under test caught the error.
    for gh in started:
        assert not gh.unmatched, (
            f"No rule for: {sorted(set(gh.unmatched))}. "
            "Add one to the scenario or use gh.respond()."
        )
