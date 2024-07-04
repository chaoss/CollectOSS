from datetime import datetime
import os
from augur.application.db.models import *
from augur.application.db.lib import bulk_insert_dicts, get_repo_by_repo_git, get_value, get_session
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.tasks.git.dependency_tasks.dependency_util import dependency_calculator as dep_calc
from augur.tasks.util.worker_util import parse_json_from_subprocess_call
from augur.tasks.git.util.facade_worker.facade_worker.utilitymethods import get_absolute_repo_path
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.util.metadata_exception import MetadataException


def generate_deps_data(logger, repo_git):
        """Run dependency logic on repo and stores data in database
        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """

        logger.info(f"repo_git: {repo_git}")
        
        repo = get_repo_by_repo_git(repo_git)
        repo_id = repo.repo_id
    
        path = get_absolute_repo_path(get_value("Facade", "repo_directory"),repo.repo_id,repo.repo_path,repo.repo_name)

        logger.debug(f"This is the deps model repo: {repo_git}.")
        
        scan_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        logger.info('Searching for deps in repo')
        logger.info(f'Repo ID: {repo_id}, Path: {path}, Scan date: {scan_date}')
        
        deps = dep_calc.get_deps(path,logger)
        
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
        
        bulk_insert_dicts(logger, to_insert,RepoDependency,["repo_id","dep_name","data_collection_date"])
        
        logger.info(f"Inserted {len(deps)} dependencies for repo {repo_id}")

"""
def deps_model(session, repo_id,repo_git,repo_path,repo_name):
    # Data collection and storage method

    logger.info(f"This is the deps model repo: {repo_git}.")

    

    generate_deps_data(session,repo_id, absolute_repo_path)
"""

def generate_scorecard(logger, repo_git):
    """Runs scorecard on repo and stores data in database
        :param repo_id: Repository ID
        :param repo_git: URL path of the Repository
    """    
    repo = get_repo_by_repo_git(repo_git)
    repo_id = repo.repo_id

    logger.info('Generating scorecard data for repo')
    # we convert relative path in the format required by scorecard like github.com/chaoss/augur
    # raw_path,_ = path.split('-')
    # scorecard_repo_path = raw_path[2:]
    path = repo_git[8:]
    if path[-4:] == '.git':
        path = path.replace(".git", "")
    command = '--repo=' + path
    
    #this is path where our scorecard project is located
    path_to_scorecard = os.environ['HOME'] + '/scorecard'

    #setting the environmental variable which is required by scorecard

    with get_session() as session:
        #key_handler = GithubRandomKeyAuth(logger)
        key_handler = GithubApiKeyHandler(logger)       
        os.environ['GITHUB_AUTH_TOKEN'] = key_handler.get_random_key()

    # This seems outdated
    #setting the environmental variable which is required by scorecard
    #key_handler = GithubApiKeyHandler(session, session.logger)       
    #os.environ['GITHUB_AUTH_TOKEN'] = key_handler.get_random_key()
    
    try: 
        required_output = parse_json_from_subprocess_call(logger,['./scorecard', command, '--format=json'],cwd=path_to_scorecard)
    
        logger.info('adding to database...')
        logger.debug(f"output: {required_output}")

        if not required_output['checks']:
            logger.info('No scorecard checks found!')
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
    # bulk_insert_dicts(overall_deps_scorecard, RepoDepsScorecard, ["repo_id","name"])

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
        
        bulk_insert_dicts(logger, to_insert, RepoDepsScorecard, ["repo_id","name"])
        
        logger.info(f"Done generating scorecard for repo {repo_id} from path {path}")

    except Exception as e: 
        
        raise MetadataException(e, f"required_output: {required_output}")
