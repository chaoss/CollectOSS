import logging
from typing import Dict, List, Tuple, Optional
import traceback
import sqlalchemy as s
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.gh_graphql_entities import GraphQlPageCollection, hit_api_graphql
from augur.application.db.models import *
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.util import execute_session_query

def pull_request_files_model(repo_id,logger, augur_db, key_auth):
    
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

    query = augur_db.session.query(Repo).filter(Repo.repo_id == repo_id)
    repo = execute_session_query(query, 'one')

    owner, name = get_owner_repo(repo.repo_git)

    pr_file_rows = []
    logger.info(f"Getting pull request files for repo: {repo.repo_git}")
    for index,pr_info in enumerate(pr_numbers):

        logger.info(f'Querying files for pull request #{index + 1} of {len(pr_numbers)}')
        
        query = """

            query($repo: String!, $owner: String!,$pr_number: Int!, $numRecords: Int!, $cursor: String) {
                repository(name: $repo, owner: $owner) {
                    pullRequest(number: $pr_number) {
                        files ( first: $numRecords, after: $cursor)
                        {
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
        
        values = ("repository","pullRequest","files")
        params = {
            'owner' : owner,
            'repo'  : name,
            'pr_number' : pr_info['pr_src_number'],
            'values' : values
        }

        
        file_collection = GraphQlPageCollection(query, key_auth, logger,bind=params)

        pr_file_rows += [{
            'pull_request_id': pr_info['pull_request_id'],
            'pr_file_additions': pr_file['additions'] if 'additions' in pr_file else None,
            'pr_file_deletions': pr_file['deletions'] if 'deletions' in pr_file else None,
            'pr_file_path': pr_file['path'],
            'data_source': 'GitHub API',
            'repo_id': repo_id, 
            } for pr_file in file_collection if pr_file and 'path' in pr_file]


    if len(pr_file_rows) > 0:
        #Execute a bulk upsert with sqlalchemy 
        pr_file_natural_keys = ["pull_request_id", "repo_id", "pr_file_path"]
        augur_db.insert_data(pr_file_rows, PullRequestFile, pr_file_natural_keys)
