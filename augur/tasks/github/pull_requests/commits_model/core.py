import logging
from typing import Dict, List, Tuple, Optional
import traceback
import sqlalchemy as s
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.application.db.models import *
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.util import execute_session_query


def pull_request_commits_model(repo_id,logger, augur_db, key_auth):
    
    # query existing PRs and the respective url we will append the commits url to
    pr_url_sql = s.sql.text("""
            SELECT DISTINCT pr_url, pull_requests.pull_request_id
            FROM pull_requests--, pull_request_meta
            WHERE repo_id = :repo_id
        """).bindparams(repo_id=repo_id)
    pr_urls = []
    #pd.read_sql(pr_number_sql, self.db, params={})

    pr_urls = augur_db.fetchall_data_from_sql_text(pr_url_sql)#session.execute_sql(pr_number_sql).fetchall()
    
    query = augur_db.session.query(Repo).filter(Repo.repo_id == repo_id)
    repo = execute_session_query(query, 'one')

    owner, name = get_owner_repo(repo.repo_git)

    task_name = f"{owner}/{name} Pr commits"

    logger.info(f"Getting pull request commits for repo: {repo.repo_git}")
        
    all_data = []
    for index,pr_info in enumerate(pr_urls):
        logger.info(f'{task_name}: Querying commits for pull request #{index + 1} of {len(pr_urls)}')

        commits_url = pr_info['pr_url'] + '/commits?state=all'

        #Paginate through the pr commits
        pr_commits = GithubPaginator(commits_url, key_auth, logger)
        
        for page_data in pr_commits:

            if page_data:
                logger.info(f"{task_name}: Processing pr commit with hash {page_data['sha']}")
                pr_commit_row = {
                    'pull_request_id': pr_info['pull_request_id'],
                    'pr_cmt_sha': page_data['sha'],
                    'pr_cmt_node_id': page_data['node_id'],
                    'pr_cmt_message': page_data['commit']['message'],
                    # 'pr_cmt_comments_url': pr_commit['comments_url'],
                    'tool_source': 'pull_request_commits_model',
                    'tool_version': '0.41',
                    'data_source': 'GitHub API',
                    'repo_id': repo_id,
                }

                all_data.append(pr_commit_row)
    
    if len(all_data) > 0:
        logger.info(f"{task_name}: Inserting {len(all_data)} rows")
        pr_commits_natural_keys = ["pull_request_id", "repo_id", "pr_cmt_sha"]
        augur_db.insert_data(all_data,PullRequestCommit,pr_commits_natural_keys)
            





