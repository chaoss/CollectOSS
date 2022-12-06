#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
import httpx
import logging
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_paginator import hit_api
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.github.util.gh_graphql_entities import hit_api_graphql
from augur.application.db.models import *
from augur.tasks.github.util.github_task_session import *


def query_committers_count(session, owner, repo):

    session.logger.info('Querying committers count\n')
    url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100'

    contributors = GithubPaginator(url, session.oauths, session.logger)
    
    return len(contributors)

def get_repo_data(session, url, response):
    data = {}
    try:
        data = response.json()
    except:
        data = json.loads(json.dumps(response.text))

    if 'errors' in data:
        session.logger.info("Error!: {}".format(data['errors']))
        raise Exception(f"Github returned error response! {data['errors']}")

    if 'id' not in data:
        session.logger.info("Request returned a non-data dict: {}\n".format(data))
        if data['message'] == 'Not Found':
            raise Exception(f"Github repo was not found or does not exist for endpoint: {url}\n")

    return data


def is_forked(session, owner, repo): #/repos/:owner/:repo parent
    session.logger.info('Querying parent info to verify if the repo is forked\n')
    url = f'https://api.github.com/repos/{owner}/{repo}'

    r = hit_api(session.oauths, url, session.logger)#requests.get(url, headers=self.headers)

    data = get_repo_data(session, url, r)

    if 'fork' in data:
        if 'parent' in data:
            return data['parent']['full_name']
        return 'Parent not available'

    return False

def is_archived(session, owner, repo):
    session.logger.info('Querying committers count\n')
    url = f'https://api.github.com/repos/{owner}/{repo}'

    r = hit_api(session.oauths, url, session.logger)#requests.get(url, headers=self.headers)
    #self.update_gh_rate_limit(r)

    data = get_repo_data(session, url, r)

    if 'archived' in data:
        if data['archived']:
            if 'updated_at' in data:
                return data['updated_at']
            return 'Date not available'
        return False

    return False

def grab_repo_info_from_graphql_endpoint(session,query):
    url = 'https://api.github.com/graphql'
    # Hit the graphql endpoint and retry 3 times in case of failure
    session.logger.info("Hitting endpoint: {} ...\n".format(url))
    r = hit_api_graphql(session.oauths, url, session.logger, query)
    
    data = {}
    try:
        data = r.json()
    except:
        data = json.loads(json.dumps(r.text))

    if 'errors' in data:
        raise Exception(f"Error!: {data['errors']}")
    
    if 'data' in data:
        data = data['data']['repository']
    else:
        session.logger.info("Request returned a non-data dict: {}\n".format(data))
        if data['message'] == 'Not Found':
            raise Exception(f"Github repo was not found or does not exist for endpoint: {url}\n")
    
    return data
    

def repo_info_model(session, repo_orm_obj):
    session.logger.info("Beginning filling the repo_info model for repo: " + repo_orm_obj.repo_git + "\n")

    owner, repo = get_owner_repo(repo_orm_obj.repo_git)

    url = 'https://api.github.com/graphql'

    query = """
        {
            repository(owner:"%s", name:"%s"){
                updatedAt
                hasIssuesEnabled
                issues(states:OPEN) {
                    totalCount
                }
                hasWikiEnabled
                forkCount
                defaultBranchRef {
                    name
                }
                watchers {
                    totalCount
                }
                id
                licenseInfo {
                    name
                    url
                }
                stargazers {
                    totalCount
                }
                codeOfConduct {
                    name
                    url
                }
                issue_count: issues {
                    totalCount
                }
                issues_closed: issues(states:CLOSED) {
                    totalCount
                }
                pr_count: pullRequests {
                    totalCount
                }
                pr_open: pullRequests(states: OPEN) {
                    totalCount
                }
                pr_closed: pullRequests(states: CLOSED) {
                    totalCount
                }
                pr_merged: pullRequests(states: MERGED) {
                    totalCount
                }
                ref(qualifiedName: "master") {
                    target {
                        ... on Commit {
                            history(first: 0){
                                totalCount
                            }
                        }
                    }
                }
            }
        }

    """ % (owner, repo)

    ##############################
    # {
    #   repository(owner: "chaoss", name: "augur") {
    #     updatedAt
    #     hasIssuesEnabled
    #     issues(states: OPEN) {
    #       totalCount
    #     }
    #     hasWikiEnabled
    #     forkCount
    #     defaultBranchRef {
    #       name
    #     }
    #     watchers {
    #       totalCount
    #     }
    #     id
    #     licenseInfo {
    #       name
    #       url
    #     }
    #     stargazers {
    #       totalCount
    #     }
    #     codeOfConduct {
    #       name
    #       url
    #     }
    #     issue_count: issues {
    #       totalCount
    #     }
    #     issues_closed: issues(states: CLOSED) {
    #       totalCount
    #     }
    #     pr_count: pullRequests {
    #       totalCount
    #     }
    #     pr_open: pullRequests(states: OPEN) {
    #       totalCount
    #     }
    #     pr_closed: pullRequests(states: CLOSED) {
    #       totalCount
    #     }
    #     pr_merged: pullRequests(states: MERGED) {
    #       totalCount
    #     }
    #     stargazerCount
    #   }
    # }

    try:
        data = grab_repo_info_from_graphql_endpoint(session, query)
    except Exception as e:
        session.logger.error(f"Could not grab info for repo {repo_orm_obj.repo_id}")
        raise e
        return

    # Just checking that the data is accessible (would not be if repo no longer exists)
    try:
        data['updatedAt']
    except Exception as e:
        raise Exception(f"Cannot access repo_info data: {data}\nError: {e}. \"Completing\" task.")
        return

    # Get committers count info that requires seperate endpoint  
    committers_count = query_committers_count(session, owner, repo)

    # Put all data together in format of the table
    session.logger.info(f'Inserting repo info for repo with id:{repo_orm_obj.repo_id}, owner:{owner}, name:{repo}\n')
    rep_inf = {
        'repo_id': repo_orm_obj.repo_id,
        'last_updated': data['updatedAt'] if 'updatedAt' in data else None,
        'issues_enabled': data['hasIssuesEnabled'] if 'hasIssuesEnabled' in data else None,
        'open_issues': data['issues']['totalCount'] if data['issues'] else None,
        'pull_requests_enabled': None,
        'wiki_enabled': data['hasWikiEnabled'] if 'hasWikiEnabled' in data else None,
        'pages_enabled': None,
        'fork_count': data['forkCount'] if 'forkCount' in data else None,
        'default_branch': data['defaultBranchRef']['name'] if data['defaultBranchRef'] else None,
        'watchers_count': data['watchers']['totalCount'] if data['watchers'] else None,
        'license': data['licenseInfo']['name'] if data['licenseInfo'] else None,
        'stars_count': data['stargazers']['totalCount'] if data['stargazers'] else None,
        'committers_count': committers_count,
        'issue_contributors_count': None,
        'changelog_file': None,
        'contributing_file': None,
        'license_file': data['licenseInfo']['url'] if data['licenseInfo'] else None,
        'code_of_conduct_file': data['codeOfConduct']['url'] if data['codeOfConduct'] else None,
        'security_issue_file': None,
        'security_audit_file': None,
        'status': None,
        'keywords': None,
        'commit_count': data['ref']['target']['history']['totalCount'] if data['ref'] else None,
        'issues_count': data['issue_count']['totalCount'] if data['issue_count'] else None,
        'issues_closed': data['issues_closed']['totalCount'] if data['issues_closed'] else None,
        'pull_request_count': data['pr_count']['totalCount'] if data['pr_count'] else None,
        'pull_requests_open': data['pr_open']['totalCount'] if data['pr_open'] else None,
        'pull_requests_closed': data['pr_closed']['totalCount'] if data['pr_closed'] else None,
        'pull_requests_merged': data['pr_merged']['totalCount'] if data['pr_merged'] else None,
        'tool_source': 'Repo_info Model',
        'tool_version': '0.42',
        'data_source': "Github"
    }

    #result = session.insert_data(rep_inf,RepoInfo,['repo_info_id']) #result = self.db.execute(self.repo_info_table.insert().values(rep_inf))
    insert_statement = s.sql.text("""INSERT INTO repo_info (repo_id,last_updated,issues_enabled,
			open_issues,pull_requests_enabled,wiki_enabled,pages_enabled,fork_count,
			default_branch,watchers_count,license,stars_count,
			committers_count,issue_contributors_count,changelog_file, contributing_file, license_file, code_of_conduct_file, security_issue_file,
            security_audit_file, status, keywords, commit_count, issues_count, issues_closed, pull_request_count, pull_requests_open, pull_requests_closed, pull_requests_merged,
            tool_source, tool_version, data_source)
			VALUES (:repo_id,:last_updated,:issues_enabled,
			:open_issues,:pull_requests_enabled,:wiki_enabled,:pages_enabled,:fork_count,
			:default_branch,:watchers_count,:license,:stars_count,
			:committers_count,:issue_contributors_count,:changelog_file, :contributing_file, :license_file, :code_of_conduct_file, :security_issue_file,
            :security_audit_file,:status, :keywords, :commit_count, :issues_count,:issues_closed, :pull_request_count, :pull_requests_open, :pull_requests_closed, :pull_requests_merged,
            :tool_source, :tool_version, :data_source)
			""").bindparams(**rep_inf)

    session.execute_sql(insert_statement)

    # Note that the addition of information about where a repository may be forked from, and whether a repository is archived, updates the `repo` table, not the `repo_info` table.
    forked = is_forked(session, owner, repo)
    archived = is_archived(session, owner, repo)
    archived_date_collected = None
    if archived is not False:
        archived_date_collected = archived
        archived = 1
    else:
        archived = 0

    current_repo_dict = repo_orm_obj.__dict__

    #delete irrelevant sqlalchemy metadata
    del current_repo_dict['_sa_instance_state']

    rep_additional_data = {
        'forked_from': forked,
        'repo_archived': archived,
        'repo_archived_date_collected': archived_date_collected
    }

    current_repo_dict.update(rep_additional_data)
    result = session.insert_data(current_repo_dict, Repo, ['repo_id'])
    #result = self.db.execute(self.repo_table.update().where(
    #    self.repo_table.c.repo_id==repo_id).values(rep_additional_data))

    session.logger.info(f"Inserted info for {owner}/{repo}\n")


