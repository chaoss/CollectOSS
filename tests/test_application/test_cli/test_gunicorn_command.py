# SPDX-License-Identifier: MIT
"""Tests for Gunicorn CLI command construction."""

from collectoss.application.cli._gunicorn import build_gunicorn_command


def test_gunicorn_command_uses_log_file_outside_docker():
    command = build_gunicorn_command(
        "/collectoss/collectoss/api/gunicorn_conf.py",
        "0.0.0.0",
        "5000",
        log_file="/collectoss/logs/gunicorn.log",
        docker_deploy=False,
    )

    assert command == [
        "gunicorn",
        "-c",
        "/collectoss/collectoss/api/gunicorn_conf.py",
        "-b",
        "0.0.0.0:5000",
        "collectoss.api.server:app",
        "--log-file",
        "/collectoss/logs/gunicorn.log",
    ]


def test_gunicorn_command_does_not_override_docker_errorlog():
    command = build_gunicorn_command(
        "/collectoss/collectoss/api/gunicorn_conf.py",
        "0.0.0.0",
        "5000",
        log_file="/collectoss/logs/gunicorn.log",
        docker_deploy=True,
    )

    assert "--log-file" not in command
    assert command == [
        "gunicorn",
        "-c",
        "/collectoss/collectoss/api/gunicorn_conf.py",
        "-b",
        "0.0.0.0:5000",
        "collectoss.api.server:app",
    ]
