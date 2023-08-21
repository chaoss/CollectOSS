from datetime import datetime
import logging
import requests
import json
import os
import subprocess
import re
import traceback
from augur.application.db.models import *
from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.application.db.util import execute_session_query
from augur.tasks.util.worker_util import parse_json_from_subprocess_call

def value_model(session,repo_id, path):
    """Runs scc on repo and stores data in database
        :param repo_id: Repository ID
        :param path: absolute file path of the Repostiory
    """

    session.logger.info('Generating value data for repo')
    session.logger.info(f"Repo ID: {repo_id}, Path: {path}")
    session.logger.info('Running scc...')

    path_to_scc = os.environ['HOME'] + '/scc'

    required_output = parse_json_from_subprocess_call(session.logger,['./scc', '-f','json', path], cwd=path_to_scc)
    
    session.logger.info('adding scc data to database... ')
    session.logger.debug(f"output: {required_output}")

    