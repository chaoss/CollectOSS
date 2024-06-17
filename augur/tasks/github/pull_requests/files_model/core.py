import sqlalchemy as s
from augur.tasks.github.util.gh_graphql_entities import GraphQlPageCollection
from augur.application.db.models import *
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.lib import bulk_insert_dicts, execute_sql
from augur.application.db.util import execute_session_query
from augur.application.db.lib import get_secondary_data_last_collected, get_updated_prs


def pull_request_files_model(repo_id,logger, augur_db, key_auth, full_collection=False):
    
    if full_collection:
        # query existing PRs and the respective url we will append the commits url to
        pr_number_sql = s.sql.text("""
            SELECT DISTINCT pr_src_number as pr_src_number, pull_requests.pull_request_id
            FROM pull_requests--, pull_request_meta
            WHERE repo_id = :repo_id
        """).bindparams(repo_id=repo_id)
        pr_numbers = []
        #pd.read_sql(pr_number_sql, self.db, params={})

        result = augur_db.execute_sql(pr_number_sql)#.fetchall()
        pr_numbers = [dict(row) for row in result.mappings()]

    else:
        last_collected = get_secondary_data_last_collected(repo_id).date()
        prs = get_updated_prs(repo_id, last_collected)

        pr_numbers = []
        for pr in prs:
            pr_numbers.append({
                'pr_src_number': pr.pr_src_number,
                'pull_request_id': pr.pull_request_id
            })

    query = augur_db.session.query(Repo).filter(Repo.repo_id == repo_id)
    repo = execute_session_query(query, 'one')
    owner, name = get_owner_repo(repo.repo_git)

    pr_file_rows = []
    logger.info(f"Getting pull request files for repo: {repo.repo_git}")
    for index, pr_info in enumerate(pr_numbers):

        logger.info(f'Querying files for pull request #{index + 1} of {len(pr_numbers)}')
        
        query = """
            query($repo: String!, $owner: String!,$pr_number: Int!, $numRecords: Int!, $cursor: String) {
                repository(name: $repo, owner: $owner) {
                    pullRequest(number: $pr_number) {
                        files ( first: $numRecords, after: $cursor) {
                            edges {
                                node {
                                    additions
                                    deletions
                                    path
                                }
                            }
                            totalCount
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                        }
                    }
                }
            }
        """
        
        values = ("repository", "pullRequest", "files")
        params = {
            'owner': owner,
            'repo': name,
            'pr_number': pr_info['pr_src_number'],
            'values': values
        }

        try:
            file_collection = GraphQlPageCollection(query, key_auth, logger, bind=params)

            pr_file_rows += [{
                'pull_request_id': pr_info['pull_request_id'],
                'pr_file_additions': pr_file['additions'] if 'additions' in pr_file else None,
                'pr_file_deletions': pr_file['deletions'] if 'deletions' in pr_file else None,
                'pr_file_path': pr_file['path'],
                'data_source': 'GitHub API',
                'repo_id': repo.repo_id,
            } for pr_file in file_collection if pr_file and 'path' in pr_file]
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting data from the GitHub API: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred while requesting data from the GitHub API: {e}")

    if len(pr_file_rows) > 0:
        # Execute a bulk upsert with sqlalchemy 
        pr_file_natural_keys = ["pull_request_id", "repo_id", "pr_file_path"]
        augur_db.insert_data(pr_file_rows, PullRequestFile, pr_file_natural_keys)
