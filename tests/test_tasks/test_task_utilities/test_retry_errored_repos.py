# SPDX-License-Identifier: MIT
"""Unit tests for per-hook error retry scheduling (#502)."""
import os
import sys
import types
from unittest.mock import Mock

import pytest

# collection_util imports celery_app, which needs Redis/DB at import time.
os.environ.setdefault("COLLECTOSS_DEV", "1")
_celery_stub = types.ModuleType("collectoss.tasks.init.celery_app")
_celery_stub.celery_app = Mock()
sys.modules.setdefault("collectoss.tasks.init.celery_app", _celery_stub)

from collectoss.tasks.util.collection_state import CollectionState
from collectoss.tasks.util.collection_util import (
    build_error_retry_sql_for_hook,
    hooks_ready_for_error_retry,
)


@pytest.mark.unit
def test_hooks_ready_when_no_new_backlog():
    """Only hooks with zero new repos should retry Errors."""
    assert hooks_ready_for_error_retry(
        {"core": 5, "secondary": 0, "facade": 0, "ml": 2}
    ) == ["secondary", "facade"]


@pytest.mark.unit
def test_hooks_ready_all_idle():
    assert hooks_ready_for_error_retry({"core": 0, "secondary": 0}) == ["core", "secondary"]


@pytest.mark.unit
def test_hooks_ready_none_when_all_busy():
    """Old global behavior blocked everyone; per-hook still blocks each busy hook."""
    assert hooks_ready_for_error_retry({"core": 1, "secondary": 3}) == []


@pytest.mark.unit
def test_build_error_retry_sql_core_resets_pending_and_success():
    sql = build_error_retry_sql_for_hook("core")
    pending = CollectionState.PENDING.value
    success = CollectionState.SUCCESS.value
    error = CollectionState.ERROR.value

    assert f"SET core_status = '{pending}'" in sql
    assert f"core_status = '{error}' and core_data_last_collected is NULL" in sql
    assert f"SET core_status = '{success}'" in sql
    assert f"core_status = '{error}' and core_data_last_collected is not NULL" in sql
    # Must not touch other hooks
    assert "secondary_status" not in sql
    assert "facade_status" not in sql


@pytest.mark.unit
def test_build_error_retry_sql_unknown_hook():
    with pytest.raises(ValueError):
        build_error_retry_sql_for_hook("not-a-hook")
