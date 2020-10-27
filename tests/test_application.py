#SPDX-License-Identifier: MIT
import pytest
import augur.application
import sqlalchemy as s
import json

from augur.application import Application

def test_init_augur_regular():
    augur_app = Application(disable_logs=True)
    assert augur_app is not None

def test_connect_to_database(monkeypatch):
    def mock_fail_connection(self):
        raise(s.exc.OperationalError("fake", "error", "message"))

    monkeypatch.setattr(s.engine.Engine, "connect", mock_fail_connection)
    monkeypatch.setenv("AUGUR_LOG_QUIET", "1")

    with pytest.raises(s.exc.OperationalError):
        augur_app = Application(disable_logs=True)
