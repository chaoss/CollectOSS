# SPDX-License-Identifier: MIT
"""
Helpers for starting Gunicorn from CollectOSS CLI commands.
"""
from __future__ import annotations

import os
from typing import Optional

from collectoss.application.environment import SystemEnv


def is_docker_deploy() -> bool:
    return SystemEnv.get_bool("COLLECTOSS_DOCKER_DEPLOY", False)


def build_gunicorn_command(
    gunicorn_config: str,
    host: str,
    port: str,
    app: str = "collectoss.api.server:app",
    log_file: Optional[str] = None,
    docker_deploy: Optional[bool] = None,
) -> list[str]:
    """
    Build a Gunicorn command while preserving Docker stderr logging.

    In Docker, Gunicorn's config sends error logs to "-" so failures are visible
    through container logs. Passing --log-file would override that setting.
    """
    command = [
        "gunicorn",
        "-c",
        gunicorn_config,
        "-b",
        f"{host}:{port}",
        app,
    ]

    if docker_deploy is None:
        docker_deploy = is_docker_deploy()

    if log_file and not docker_deploy:
        command.extend(["--log-file", os.fspath(log_file)])

    return command
