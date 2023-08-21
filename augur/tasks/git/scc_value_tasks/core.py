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

def value_model(session,repo_id, path):
    """Runs scc on repo and stores data in database
        :param repo_id: Repository ID
        :param path: absolute file path of the Repostiory
    """

    session.logger.info('Generating value data for repo')
    session.logger.info(f"Repo ID: {repo_id}, Path: {path}")
    session.logger.info('Running scc...')

    path_to_scc = os.environ['HOME'] + '/scc'

    p = subprocess.run(['./scc', '-f','json', path], cwd=path_to_scc, capture_output=True, text=True, timeout=None)
    session.logger.info('scc has completed... ')
    output = p.stdout

    try:
        required_data = json.loads(output)
    except json.decoder.JSONDecodeError as e:
        session.logger.error(f"Could not parse required output! \n output: {output} \n Error: {e}")
        return
    
    session.logger.info('adding scc data to database... ')
    session.logger.debug(f"output: {required_output}")

    