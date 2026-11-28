# SPDX-License-Identifier: MIT
"""Unit tests for backend server start/stop behavior with --disable-collection."""

import importlib
import logging
import signal
import sys
import types
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner


def _make_stub_module(name, **attrs):
    mod = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(mod, key, value)
    return mod


def _make_process(cmdline, environ=None, name="celery", pid=12345):
    proc = MagicMock()
    proc.pid = pid
    proc.name.return_value = name
    proc.info = {
        "cmdline": cmdline,
        "name": name,
        "environ": environ or {},
    }
    return proc


@pytest.fixture(name="backend_module")
def _backend_module(monkeypatch):
    """Import collectoss.application.cli.backend with isolated import-time stubs."""
    monkeypatch.setenv("COLLECTOSS_DEV", "0")
    monkeypatch.setenv("COLLECTOSS_DB", "postgresql+psycopg2://test:test@localhost:5435/scratch")
    monkeypatch.delenv("COLLECTOSS_DISABLE_COLLECTION", raising=False)

    mock_engine = MagicMock()
    mock_session = MagicMock()

    stubs = {
        "keyman": _make_stub_module("keyman"),
        "keyman.KeyClient": _make_stub_module(
            "keyman.KeyClient",
            KeyClient=MagicMock(),
            KeyPublisher=MagicMock(),
        ),
        "collectoss.tasks.start_tasks": _make_stub_module(
            "collectoss.tasks.start_tasks",
            collection_monitor=MagicMock(),
            create_collection_status_records=MagicMock(),
        ),
        "collectoss.tasks.git.facade_tasks": _make_stub_module(
            "collectoss.tasks.git.facade_tasks",
            clone_repos=MagicMock(),
        ),
        "collectoss.tasks.github.contributors": _make_stub_module(
            "collectoss.tasks.github.contributors",
            process_contributors=MagicMock(),
        ),
        "collectoss.tasks.github.util.github_api_key_handler": _make_stub_module(
            "collectoss.tasks.github.util.github_api_key_handler",
            GithubApiKeyHandler=MagicMock(),
        ),
        "collectoss.tasks.gitlab.gitlab_api_key_handler": _make_stub_module(
            "collectoss.tasks.gitlab.gitlab_api_key_handler",
            GitlabApiKeyHandler=MagicMock(),
        ),
        "collectoss.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker": _make_stub_module(
            "collectoss.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker",
            contributor_breadth_model=MagicMock(),
        ),
        "collectoss.tasks.init.celery_app": _make_stub_module(
            "collectoss.tasks.init.celery_app",
            celery_app=MagicMock(),
        ),
    }

    if "resource" not in sys.modules:
        stubs["resource"] = _make_stub_module(
            "resource",
            RLIMIT_NOFILE=0,
            getrlimit=lambda _: (1024, 4096),
            setrlimit=lambda *_: None,
        )
    if "requests" not in sys.modules:
        stubs["requests"] = _make_stub_module(
            "requests",
            exceptions=types.SimpleNamespace(ConnectionError=ConnectionError),
            get=MagicMock(return_value=types.SimpleNamespace(ok=True, json=lambda: {"route": "/api"})),
        )

    for mod_name, mod_obj in stubs.items():
        monkeypatch.setitem(sys.modules, mod_name, mod_obj)

    import collectoss.tasks.init as tasks_init
    monkeypatch.setattr(tasks_init, "get_redis_conn_values", lambda: (0, "redis://127.0.0.1:6379/"))
    monkeypatch.setattr(tasks_init, "get_rabbitmq_conn_string", lambda: "amqp://guest:guest@localhost:5672//")

    from collectoss.application.db.engine import DatabaseEngine
    monkeypatch.setattr(DatabaseEngine, "__init__", lambda self, *a, **kw: None)
    monkeypatch.setattr(DatabaseEngine, "engine", property(lambda self: mock_engine))
    monkeypatch.setattr(DatabaseEngine, "__enter__", lambda self: mock_engine)
    monkeypatch.setattr(DatabaseEngine, "__exit__", lambda self, *a: None)

    from collectoss.application.db.session import DatabaseSession
    monkeypatch.setattr(
        DatabaseSession,
        "__init__",
        lambda self, *a, **kw: setattr(self, "logger", logging.getLogger("test_backend")),
    )
    monkeypatch.setattr(DatabaseSession, "__del__", lambda self: None)
    monkeypatch.setattr(DatabaseSession, "__enter__", lambda self: mock_session)
    monkeypatch.setattr(DatabaseSession, "__exit__", lambda self, *a: None)

    from collectoss.application.logs import SystemLogger
    monkeypatch.setattr(SystemLogger, "__init__", lambda self, *a, **kw: None)
    monkeypatch.setattr(SystemLogger, "get_logger", lambda self: logging.getLogger("test_backend"))

    import collectoss.application.cli as cli_pkg
    monkeypatch.setattr(cli_pkg, "check_connectivity", lambda *a, **kw: True)

    sys.modules.pop("collectoss.application.cli.backend", None)
    module = importlib.import_module("collectoss.application.cli.backend")
    yield module
    sys.modules.pop("collectoss.application.cli.backend", None)


@pytest.mark.unit
class TestDisableCollection:
    """Tests for --disable-collection startup and shutdown behavior."""

    def test_start_disable_collection_skips_cleanup_beat_and_keypublisher(self, backend_module, tmp_path):
        """Starting with --disable-collection should not purge queues, flush Redis, start beat, or connect KeyPublisher."""
        pidfile = tmp_path / "collectoss.pid"
        runner = CliRunner()

        fake_server = MagicMock()
        fake_server.poll.return_value = None
        fake_server.wait.return_value = 0

        config_values = {
            "host": "127.0.0.1",
            "port": "5000",
            "core_worker_count": 1,
            "secondary_worker_count": 1,
            "facade_worker_count": 1,
            "logs_directory": str(tmp_path),
            "log_level": "INFO",
        }

        with patch.object(backend_module, "get_value", side_effect=lambda _s, k: config_values[k]), \
             patch.object(backend_module, "cleanup_collection_status_and_rabbit") as mock_cleanup, \
             patch.object(backend_module, "KeyPublisher") as mock_keypub, \
             patch.object(backend_module, "start_celery_worker_processes", return_value=[]) as mock_workers, \
             patch.object(backend_module.subprocess, "Popen", return_value=fake_server) as mock_popen, \
             patch.object(backend_module.signal, "signal"), \
             patch.object(backend_module.requests, "get", return_value=types.SimpleNamespace(ok=True, json=lambda: {"route": "/api"})):
            result = runner.invoke(
                backend_module.cli,
                ["start", "--disable-collection", "--pidfile", str(pidfile)],
            )

        assert result.exit_code == 0, result.output
        mock_cleanup.assert_not_called()
        mock_keypub.assert_not_called()
        mock_workers.assert_called_once_with((1, 1, 1), True)
        # Only Gunicorn should be started via Popen here (no celery beat process).
        assert mock_popen.call_count == 1
        assert "gunicorn" in mock_popen.call_args[0][0][0]

    def test_stop_skips_cleanup_when_only_frontend_worker_or_disable_collection_is_running(self, backend_module):
        """Stopping when --disable-collection was used should not purge Celery/Redis."""
        frontend_proc = _make_process(
            ["celery", "-A", "collectoss.tasks.init.celery_app.celery_app", "worker", "-Q", "frontend", "-n", "frontend:1@h"],
            environ={"COLLECTOSS_DISABLE_COLLECTION": "1"},
        )

        with patch.object(backend_module, "get_backend_processes", return_value=[frontend_proc]), \
             patch.object(backend_module, "_broadcast_signal_to_processes") as mock_broadcast, \
             patch.object(backend_module, "cleanup_collection_status_and_rabbit") as mock_cleanup:
            backend_module.stop_processes(signal.SIGTERM, backend_module.logger, MagicMock())

        mock_broadcast.assert_called_once()
        mock_cleanup.assert_not_called()

    def test_stop_skips_cleanup_for_frontend_celery_even_without_env_flag(self, backend_module):
        """A frontend-only celery worker without collection workers should not trigger collection cleanup."""
        frontend_proc = _make_process(
            ["celery", "-A", "collectoss.tasks.init.celery_app.celery_app", "worker", "-Q", "frontend", "-n", "frontend:1@h"],
        )

        with patch.object(backend_module, "get_backend_processes", return_value=[frontend_proc]), \
             patch.object(backend_module, "_broadcast_signal_to_processes"), \
             patch.object(backend_module, "cleanup_collection_status_and_rabbit") as mock_cleanup:
            backend_module.stop_processes(signal.SIGTERM, backend_module.logger, MagicMock())

        mock_cleanup.assert_not_called()

    def test_stop_runs_cleanup_when_collection_workers_are_running(self, backend_module):
        """Stopping an instance with active collection workers should still clean up queues and status."""
        core_proc = _make_process(
            ["celery", "-A", "collectoss.tasks.init.celery_app.celery_app", "worker", "-n", "core:1@h"],
        )
        engine = MagicMock()

        with patch.object(backend_module, "get_backend_processes", return_value=[core_proc]), \
             patch.object(backend_module, "_broadcast_signal_to_processes") as mock_broadcast, \
             patch.object(backend_module, "cleanup_collection_status_and_rabbit") as mock_cleanup:
            backend_module.stop_processes(signal.SIGTERM, backend_module.logger, engine)

        mock_broadcast.assert_called_once()
        mock_cleanup.assert_called_once_with(backend_module.logger, engine)

    def test_start_with_collection_enabled_runs_cleanup_beat_and_keypublisher(self, backend_module, tmp_path):
        """Starting without --disable-collection should run startup cleanup, beat, and KeyPublisher."""
        pidfile = tmp_path / "collectoss_enabled.pid"
        runner = CliRunner()

        fake_server = MagicMock()
        fake_server.poll.return_value = None
        fake_server.wait.return_value = 0

        config_values = {
            "host": "127.0.0.1",
            "port": "5000",
            "core_worker_count": 1,
            "secondary_worker_count": 1,
            "facade_worker_count": 1,
            "logs_directory": str(tmp_path),
            "log_level": "INFO",
        }

        with patch.object(backend_module, "get_value", side_effect=lambda _s, k: config_values[k]), \
             patch.object(backend_module, "cleanup_collection_status_and_rabbit") as mock_cleanup, \
             patch.object(backend_module, "KeyPublisher") as mock_keypub, \
             patch.object(backend_module, "start_celery_worker_processes", return_value=[]), \
             patch.object(backend_module.subprocess, "Popen", return_value=fake_server) as mock_popen, \
             patch.object(backend_module.signal, "signal"), \
             patch.object(backend_module, "DatabaseSession"), \
             patch.object(backend_module, "clean_collection_status"), \
             patch.object(backend_module, "assign_orphan_repos_to_default_user"), \
             patch.object(backend_module, "GithubApiKeyHandler", return_value=MagicMock(keys=[])), \
             patch.object(backend_module, "GitlabApiKeyHandler", return_value=MagicMock(keys=[])), \
             patch.object(backend_module.time, "sleep"), \
             patch.object(backend_module.requests, "get", return_value=types.SimpleNamespace(ok=True, json=lambda: {"route": "/api"})):
            mock_keypub.return_value.wait.return_value = True
            result = runner.invoke(
                backend_module.cli,
                ["start", "--pidfile", str(pidfile)],
            )

        assert result.exit_code == 0, result.output
        mock_cleanup.assert_called_once()
        mock_keypub.assert_called_once()
        commands = [" ".join(call.args[0]) for call in mock_popen.call_args_list]
        assert any("beat" in cmd for cmd in commands)

    def test_service_manager_shutdown_skips_cleanup_when_collection_disabled(self, backend_module, tmp_path):
        """SystemServiceManager should skip KeyPublisher shutdown and queue cleanup when disable_collection is True."""
        del backend_module
        from collectoss.application.service_manager import SystemServiceManager

        pidfile = tmp_path / "mgr.pid"
        pidfile.write_text("1234", encoding="utf-8")
        ctx = MagicMock()
        manager = SystemServiceManager(ctx, str(pidfile), disable_collection=True)
        manager.keypub = None

        with patch("collectoss.application.service_manager.cleanup_collection_status_and_rabbit") as mock_cleanup, \
             pytest.raises(SystemExit) as exc_info:
            manager.shutdown_signal_handler(signal.SIGTERM, None)

        assert exc_info.value.code == 0
        mock_cleanup.assert_not_called()
        assert not pidfile.exists()

    def test_service_manager_shutdown_runs_cleanup_when_collection_enabled(self, backend_module, tmp_path):
        """SystemServiceManager should run KeyPublisher shutdown and queue cleanup when collection is enabled."""
        del backend_module
        from collectoss.application.service_manager import SystemServiceManager

        pidfile = tmp_path / "mgr_enabled.pid"
        pidfile.write_text("1234", encoding="utf-8")
        ctx = MagicMock()
        manager = SystemServiceManager(ctx, str(pidfile), disable_collection=False)
        manager.keypub = MagicMock()

        with patch("collectoss.application.service_manager.cleanup_collection_status_and_rabbit") as mock_cleanup, \
             pytest.raises(SystemExit) as exc_info:
            manager.shutdown_signal_handler(signal.SIGTERM, None)

        assert exc_info.value.code == 0
        manager.keypub.shutdown.assert_called_once()
        mock_cleanup.assert_called_once()
        assert not pidfile.exists()
