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
from augur.tasks.git.dependency_tasks.dependency_util import dependency_calculator as dep_calc
from augur.tasks.util.worker_util import parse_json_from_subprocess_call

def generate_deps_data(session, repo_id, path):
        """Run dependency logic on repo and stores data in database
        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        
        scan_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        session.logger.info('Searching for deps in repo')
        session.logger.info(f'Repo ID: {repo_id}, Path: {path}, Scan date: {scan_date}')

        

        deps = dep_calc.get_deps(path,session.logger)
        
        to_insert = []
        for dep in deps:
            repo_deps = {
                'repo_id': repo_id,
                'dep_name' : dep.name,
                'dep_count' : dep.count,
                'dep_language' : dep.language,
                'tool_source': 'deps_model',
                'tool_version': '0.43.9',
                'data_source': 'Git',
                'data_collection_date': scan_date
            }

            to_insert.append(repo_deps)
            
        session.insert_data(to_insert,RepoDependency,["repo_id","dep_name","data_collection_date"])
        
        session.logger.info(f"Inserted {len(deps)} dependencies for repo {repo_id}")

"""
def deps_model(session, repo_id,repo_git,repo_path,repo_name):
    # Data collection and storage method

    session.logger.info(f"This is the deps model repo: {repo_git}.")

    

    generate_deps_data(session,repo_id, absolute_repo_path)
"""

def generate_scorecard(session,repo_id,path):
    """Runs scorecard on repo and stores data in database
        :param repo_id: Repository ID
        :param path: URL path of the Repostiory
    """
    session.logger.info('Generating scorecard data for repo')
    session.logger.info(f"Repo ID: {repo_id}, Path: {path}")

    # we convert relative path in the format required by scorecard like github.com/chaoss/augur
    # raw_path,_ = path.split('-')
    # scorecard_repo_path = raw_path[2:]
    path = path[8:]
    if path[-4:] == '.git':
        path = path.replace(".git", "")
    command = '--repo='+ path
    
    #this is path where our scorecard project is located
    path_to_scorecard = os.environ['HOME'] + '/scorecard'

    #setting the environmental variable which is required by scorecard
    key_handler = GithubApiKeyHandler(session)       
    os.environ['GITHUB_AUTH_TOKEN'] = key_handler.get_random_key()
    
    required_output = parse_json_from_subprocess_call(session.logger,['./scorecard', command, '--format=json'],cwd=path_to_scorecard)
    
    session.logger.info('adding to database...')
    session.logger.debug(f"output: {required_output}")

    if not required_output['checks']:
        session.logger.info('No scorecard checks found!')
        return
    
    #Store the overall score first
    to_insert = []
    overall_deps_scorecard = {
        'repo_id': repo_id,
        'name': 'OSSF_SCORECARD_AGGREGATE_SCORE',
        'scorecard_check_details': required_output['repo'],
        'score': required_output['score'],
        'tool_source': 'scorecard_model',
        'tool_version': '0.43.9',
        'data_source': 'Git',
        'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    to_insert.append(overall_deps_scorecard)
   # session.insert_data(overall_deps_scorecard, RepoDepsScorecard, ["repo_id","name"])

    #Store misc data from scorecard in json field. 
    for check in required_output['checks']:
        repo_deps_scorecard = {
            'repo_id': repo_id,
            'name': check['name'],
            'scorecard_check_details': check,
            'score': check['score'],
            'tool_source': 'scorecard_model',
            'tool_version': '0.43.9',
            'data_source': 'Git',
            'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        to_insert.append(repo_deps_scorecard)
    
    session.insert_data(to_insert, RepoDepsScorecard, ["repo_id","name"])
    
    session.logger.info(f"Done generating scorecard for repo {repo_id} from path {path}")


