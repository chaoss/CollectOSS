#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

from copy import deepcopy
import os, time, atexit, subprocess, click, atexit, logging, sys
import psutil
import signal
import multiprocessing as mp
import gunicorn.app.base
from gunicorn.arbiter import Arbiter
import sys
from subprocess import call
import json
import random
import string
import subprocess
from redis.exceptions import ConnectionError as RedisConnectionError
import uuid

from augur.tasks.init.redis_connection import redis_connection as redis_conn

# from augur.api.application import Application
# from augur.api.gunicorn import AugurGunicornApp
from augur.application.logs import AugurLogger

# from augur.server import Server
from celery import chain, signature, group

from augur.application.cli import test_connection, test_db_connection 

logger = AugurLogger("augur").get_logger()

@click.group('redis', short_help='Commands for managing redis cache')
def cli():
    pass

@cli.command("clear")
@test_connection
@test_db_connection
def clear():

    while True:

        user_input = str(input("Warning this will clear all redis databases on your redis cache!\nWould you like to proceed? [y/N]"))

        if not user_input:
            logger.info("Exiting")
            return
        
        if user_input in ("y", "Y", "Yes", "yes"):
            logger.info("Clearing call redis databases")
            redis_conn.flushall()
            return

        elif user_input in ("n", "N", "no", "NO"):
            logger.info("Exiting")
            return
        else:
            logger.error("Invalid input")
