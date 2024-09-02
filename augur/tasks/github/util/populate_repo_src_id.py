import logging
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.lib import get_repo_by_repo_git, execute_sql
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.github_graphql_data_access import GithubGraphQlDataAccess
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth

@celery.task
def populate_repo_src_id_task(repo_git):

    logger = logging.getLogger(populate_repo_src_id_task.__name__)

    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    owner, repo = get_owner_repo(repo_git)

    key_auth = GithubRandomKeyAuth(logger)

    repo_src_id = get_repo_src_id(owner, repo, logger, key_auth)

    update_repo_src_id(repo_id, repo_src_id)
    

def get_repo_src_id(owner, repo, logger, key_auth):
    

    query = """query($repo: String!, $owner: String!) {
                    repository(name: $repo, owner: $owner) {
                        updatedAt
                    }
                }
                """
    
    github_graphql_data_access = GithubGraphQlDataAccess(key_auth, logger)

    variables = {
        "owner": owner,
        "repo": repo
    }

    result_keys = ["repository", "databaseId"]

    repo_src_id = github_graphql_data_access.get_resource(query, variables, result_keys)

    return repo_src_id



def update_repo_src_id(repo_id, repo_src_id):
    
    query = s.sql.text("""UPDATE repo SET repo_src_id=:repo_src_id WHERE repo_id=:repo_id;
        """).bindparams(repo_src_id=repo_src_id, repo_id=repo_id)
    
    execute_sql(query)
