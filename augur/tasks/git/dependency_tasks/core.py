from datetime import datetime
import json
import logging
import requests
import json
import os
import subprocess
import re
import traceback
from augur.application.db.data_parse import *
from augur.application.db.models import *
from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.application.db.util import execute_session_query
from augur.tasks.git.dependency_tasks.dependency_util import dependency_calculator as dep_calc

def generate_deps_data(session, repo_id, path):
        """Runs scc on repo and stores data in database
        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        
        scan_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        session.logger.info('Searching for deps in repo')
        session.logger.info(f'Repo ID: {repo_id}, Path: {path}, Scan date: {scan_date}')

        

        deps = dep_calc.get_deps(path)
        try: 
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

                session.insert_data(repo_deps,RepoDependency,["repo_id","dep_name","data_collection_date"])
        except Exception as e:
            session.logger.error(f"Could not complete generate_deps_data!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
        
        session.logger.info(f"Inserted {len(deps)} dependencies for repo {repo_id}")


def deps_model(session, repo_id,repo_git,repo_group_id):
    """ Data collection and storage method
    """
    session.logger.info(f"This is the deps model repo: {repo_git}.")

    

    #result = session.execute_sql(repo_path_sql)
    result = re.search(r"https:\/\/(github\.com\/[A-Za-z0-9 \- _]+\/)([A-Za-z0-9 \- _ .]+)$", repo_git).groups()
    
    relative_repo_path = f"{repo_group_id}/{result[0]}{result[1]}"
    config = AugurConfig(session.logger, session)
    absolute_repo_path = config.get_section("Facade")['repo_directory'] + relative_repo_path

    try:
        generate_deps_data(session,repo_id, absolute_repo_path)
    except Exception as e:
        session.logger.error(f"Could not complete deps_model!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")


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
    config = AugurConfig(session.logger, session)
    os.environ['GITHUB_AUTH_TOKEN'] = config.get_section("Keys")['github_api_key']#self.config['gh_api_key']
    
    p= subprocess.run(['./scorecard', command, '--format=json'], cwd= path_to_scorecard ,capture_output=True, text=True, timeout=None)
    session.logger.info('subprocess completed successfully... ')
    output = p.stdout

    try:
        required_output = json.loads(output)
    except Exception as e:
        session.logger.error(f"Could not parse required output! \n output: {output} \n Error: {e}")
        return

    session.logger.info('adding to database...')
    session.logger.debug(f"output: {required_output}")

    if not required_output['checks']:
        session.logger.info('No scorecard checks found!')
        return
    
    #Store the overall score first
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

    session.insert_data(overall_deps_scorecard, RepoDepsScorecard, ["repo_id","name"])

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
        session.insert_data(repo_deps_scorecard, RepoDepsScorecard, ["repo_id","name"])
    
    session.logger.info(f"Done generating scorecard for repo {repo_id} from path {path}")


"""
    

    for test in required_output:
        temp = test.split()
        repo_deps_scorecard = {
            'repo_id': repo_id,
            'name': temp[0],
            'status': temp[1],
            'score': temp[2],
            'tool_source': 'scorecard_model',
            'tool_version': '0.43.9',
            'data_source': 'Git',
            'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        } 
        session.insert_data(repo_deps_scorecard, RepoDepsScorecard, ["repo_id","name"])
"""