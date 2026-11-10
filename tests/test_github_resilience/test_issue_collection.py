# SPDX-License-Identifier: MIT
"""Issue collection on repos with issues disabled."""
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.issues import collect_issues, retrieve_all_issue_data


def collect():
    return list(retrieve_all_issue_data("https://github.com/owner/repo", Mock(), None))


@pytest.mark.unit
@pytest.mark.parametrize("scenario, expected", [
    ("normal", [{"number": 2}]),
    # /issues still lists pull requests.
    ("issues_disabled", [{"number": 1, "pull_request": {}}]),
    ("issues_and_prs_disabled", []),
])
def test_issue_collection(fake_github, scenario, expected):
    """Failure means issue collection crashes or returns the wrong items on a
    repo with issues disabled."""
    fake_github(scenario)
    assert collect() == expected


@pytest.mark.unit
def test_celery_tasks_cannot_be_called_directly():
    """Failure means a Celery task ran without a database, so a test calling
    one could pass without testing anything."""
    with pytest.raises(RuntimeError, match="Celery task"):
        collect_issues("https://github.com/owner/repo", True)
