from datetime import datetime
import os
from augur.application.db.models import *
from augur.application.db.lib import bulk_insert_dicts, get_repo_by_repo_git, get_value
from augur.tasks.util.worker_util import parse_json_from_subprocess_call
from augur.tasks.git.util.facade_worker.facade_worker.utilitymethods import get_absolute_repo_path

def value_model(logger,repo_git):
    """Runs scc on repo and stores data in database
        :param repo_id: Repository ID
    """
    logger.info(f"repo_git: {repo_git}")

    repo = get_repo_by_repo_git(repo_git)
    repo_id = repo.repo_id

    path = get_absolute_repo_path(get_value("Facade", "repo_directory"),repo_id,repo.repo_path,repo.repo_name)

    logger.info('Generating value data for repo')
    logger.info(f"Repo ID: {repo_id}, Path: {path}")
    logger.info('Running scc...')

    path_to_scc = os.environ['HOME'] + '/scc'

    required_output = parse_json_from_subprocess_call(logger,['./scc', '-f','json','--by-file', path], cwd=path_to_scc)
    
    logger.info('adding scc data to database... ')
    logger.debug(f"output: {required_output}")

    to_insert = []
    for record in required_output:
        for file in record['Files']:
            repo_labor = {
                'repo_id': repo_id,
                'rl_analysis_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'programming_language': file['Language'],
                'file_path': file['Location'],
                'file_name': file['Filename'],
                'total_lines': file['Lines'],
                'code_lines': file['Code'],
                'comment_lines': file['Comment'],
                'blank_lines': file['Blank'],
                'code_complexity': file['Complexity'],
                'repo_url': repo_git,
                'tool_source': 'value_model',
                'data_source': 'Git',
                'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
            }

            to_insert.append(repo_labor)
    
    bulk_insert_dicts(logger, to_insert, RepoLabor, ["repo_id", "rl_analysis_date", "file_path", "file_name" ])

    logger.info(f"Done generating scc data for repo {repo_id} from path {path}")
