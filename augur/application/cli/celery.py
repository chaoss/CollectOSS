#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

import os
import click
import subprocess
from redis.exceptions import ConnectionError as RedisConnectionError

from augur import instance_id
from augur.application.logs import AugurLogger
from augur.tasks.init.redis_connection import redis_connection
from augur.application.cli import test_connection, test_db_connection 

logger = AugurLogger("augur", reset_logfiles=True).get_logger()

@click.group('celery', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    """Placeholder docstring."""

@cli.command("start")
@test_connection
@test_db_connection
def start():
    """Start Augur's celery process."""
    celery_process = None

    celery_command = f"celery -A augur.tasks.init.celery_app.celery_app worker --loglevel=info --concurrency=20 -n {instance_id}@%h"
    celery_process = subprocess.Popen(celery_command.split(" "))

    try:
        celery_process.wait()
    except KeyboardInterrupt:

        if celery_process:
            logger.info("Shutting down celery process")
            celery_process.terminate()

        try:
            logger.info("Flusing redis cache")
            redis_connection.flushdb()
            
        except RedisConnectionError:
            pass
