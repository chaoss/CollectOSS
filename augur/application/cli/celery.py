#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

from copy import deepcopy
import os, time, atexit, subprocess, click, atexit, logging, sys
import psutil
import signal
import sys
import json
import random
import string
import subprocess
from redis.exceptions import ConnectionError as RedisConnectionError
import uuid

from augur import instance_id
from augur.application.logs import AugurLogger

# from augur.server import Server
from celery import chain, signature, group

from augur.application.cli import test_connection, test_db_connection 

logger = AugurLogger("augur", reset_logfiles=True).get_logger()

@click.group('celery', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    pass

@cli.command("start")
@test_connection
@test_db_connection
def start():
    """
    Start Augur's backend server
    """
    celery_process = None

    celery_command = f"celery -A augur.tasks.init.celery_app.celery_app worker --loglevel=info --concurrency=20 -n {instance_id}@%h"
    celery_process = subprocess.Popen(celery_command.split(" "))

    try:
        celery_process.wait()
    except KeyboardInterrupt:

        if celery_process:
            logger.info("Shutting down celery process")
            celery_process.terminate

        try:
            logger.info("Flusing redis cache")
            redis_connection.flushdb()
            
        except RedisConnectionError:
            pass
