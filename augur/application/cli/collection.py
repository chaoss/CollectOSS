#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""
import resource
import os
import time
import subprocess
import click
import logging
import psutil
import signal
import sys
from redis.exceptions import ConnectionError as RedisConnectionError
from celery import chain, signature, group
import uuid
import traceback
from sqlalchemy import update


from augur import instance_id
from augur.tasks.start_tasks import augur_collection_monitor, CollectionState
from augur.tasks.init.redis_connection import redis_connection 
from augur.application.db.models import Repo, CollectionStatus
from augur.application.db.session import DatabaseSession
from augur.application.db.util import execute_session_query

from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.application.cli import test_connection, test_db_connection 
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.github.util.github_paginator import hit_api

import sqlalchemy as s


logger = AugurLogger("augur", reset_logfiles=True).get_logger()

def get_page_count()


def check_collection(owner, repo, key_manager, session):

    # prs
    pr_url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    prs = hit_api(key_manager, pr_url, logger)
    

    # issues
    # issue_url = ""
    # issues = hit_api(key_manager, issue_url, logger)

    # # messages
    # message_url = ""
    # messages = hit_api(key_manager, message_url, logger)

    # # events
    # event_url = ""
    # events = hit_api(key_manager, event_url, logger)

    return True, True, True, True


@click.group('collection', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    pass

@cli.command("status")
@click.option("--failed", is_flag=True, default=False, help="Only shows repos that failed")
@test_connection
@test_db_connection
def status(failed):

    with DatabaseSession(logger) as session:

        key_manager = GithubRandomKeyAuth(session)

        query = session.query(Repo)
        repos = execute_session_query(query, 'all')

        for repo in repos:

            repo_git = repo.repo_git

           

            
        