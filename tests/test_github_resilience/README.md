# GitHub resilience tests

Tests for collectors running against unusual repositories (issues disabled, PRs
disabled, repo deleted) using a fake GitHub API. They need no token, network,
database or Redis, and run in CI with the rest of `pytest`.

```bash
uv run pytest tests/test_github_resilience
```

## Testing a fix for a "collector crashes on repo X" bug

1. Pick a scenario in `SCENARIOS` (`conftest.py`), or add one. Copy the status
   codes from the real GitHub API (`curl -i` the failing URL from the bug
   report) and note the repository and date beside it. Do not guess them.
2. Call the collector's helper function against the scenario and assert what it
   returns. Celery tasks (`@celery.task`) need a database and raise if called;
   test the plain function the task calls, such as `retrieve_all_pr_data`.
3. Confirm the test fails without your fix and passes with it.
4. Check the neighboring scenarios still pass. A repo with only issues
   disabled still has pull request comments on `/issues/comments`, so a fix
   for one scenario must not skip data in another.
5. Give the test a one-line docstring saying what a failure means.

Example: `test_message_collection.py` has a test for a known crash, marked
`xfail`. The fix makes it pass, and the marker is then removed:

```python
import pytest
from unittest.mock import Mock

from collectoss.tasks.github.messages import fast_retrieve_all_pr_and_issue_messages


@pytest.mark.unit
def test_no_messages_when_issues_and_prs_disabled(fake_github):
    fake_github("issues_and_prs_disabled")

    messages = fast_retrieve_all_pr_and_issue_messages(
        "https://github.com/owner/repo", Mock(), None, "test", None)

    assert messages == []
```

## What the fixture gives you

- `gh = fake_github("scenario")` starts the fake.
- `gh.respond(path_regex, status, body)` adds a one-off response that takes
  priority over the scenario.
- `gh.requests` lists every `(method, path)` the code asked for.
- A test fails if the code requests a path with no rule, even when the code
  catches the error.

Not modeled yet: response headers (pagination, rate limits, redirects) and
query strings.
