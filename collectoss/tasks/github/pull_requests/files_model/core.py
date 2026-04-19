import sqlalchemy as s
from collectoss.tasks.github.util.github_graphql_data_access import GithubGraphQlDataAccess, NotFoundException, InvalidDataException
from collectoss.application.db.models import *
from collectoss.tasks.github.util.util import get_owner_repo
from collectoss.application.db.util import execute_session_query
from collectoss.application.db.lib import get_secondary_data_last_collected, get_updated_prs, get_batch_size




def pull_request_files_model(repo_id,logger, db_session, key_auth, full_collection=False):

    pr_file_batch_size = get_batch_size()

    if full_collection:
        # query existing PRs and the respective url we will append the commits url to
        pr_number_sql = s.sql.text("""
            SELECT DISTINCT pr_src_number as pr_src_number, pull_requests.pull_request_id
            FROM pull_requests--, pull_request_meta
            WHERE repo_id = :repo_id
        """).bindparams(repo_id=repo_id)
        pr_numbers = []
        #pd.read_sql(pr_number_sql, self.db, params={})

        result = db_session.execute_sql(pr_number_sql)#.fetchall()
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

    query = db_session.session.query(Repo).filter(Repo.repo_id == repo_id)
    repo = execute_session_query(query, 'one')
    owner, name = get_owner_repo(repo.repo_git)

    task_name = f"{owner}/{name} Pr files"

    github_graphql_data_access = GithubGraphQlDataAccess(key_auth, logger)

    pr_file_natural_keys = ["pull_request_id", "repo_id", "pr_file_path"]
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

        values = ["repository", "pullRequest", "files"]
        params = {
            'owner': owner,
            'repo': name,
            'pr_number': pr_info['pr_src_number'],
        }

        try:
            for pr_file in github_graphql_data_access.paginate_resource(query, params, values):

                if not pr_file or 'path' not in pr_file:
                    continue

                data = {
                    'pull_request_id': pr_info['pull_request_id'],
                    'pr_file_additions': pr_file['additions'] if 'additions' in pr_file else None,
                    'pr_file_deletions': pr_file['deletions'] if 'deletions' in pr_file else None,
                    'pr_file_path': pr_file['path'],
                    'data_source': 'GitHub API',
                    'repo_id': repo.repo_id,
                }

                pr_file_rows.append(data)

                if len(pr_file_rows) >= pr_file_batch_size:
                    logger.info(f"{task_name}: Inserting {len(pr_file_rows)} rows")
                    db_session.insert_data(pr_file_rows, PullRequestFile, pr_file_natural_keys)
                    pr_file_rows.clear()
        except NotFoundException as e:
            logger.info(f"{task_name}: PR with number of {pr_info['pr_src_number']} returned 404 on file data. Skipping.")
            continue
        except InvalidDataException as e:
            logger.warning(f"{task_name}: PR with number of {pr_info['pr_src_number']} returned null for file data. Skipping.")
            continue


    if len(pr_file_rows) > 0:
        logger.info(f"{task_name}: Inserting {len(pr_file_rows)} rows")
        db_session.insert_data(pr_file_rows, PullRequestFile, pr_file_natural_keys)
