#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker

# NOTE: This worker primarily inserts rows into the REPO_INFO table, which serves the primary purposes of 
# 1. Displaying discrete metadata like "number of forks" and how they change over time 
# 2. Validating other workers, like those related to pull requests, issues, and commits. Our totals should be at or very near the totals in the repo_info table.

# This table also updates the REPO table in 2 cases: 
# 1. Recognizing when a repository is a forked repository by updating the "forked_from" field and 
# 2. Recognizing when a repository is archived, and recording the data we observed the change in status. 

class RepoInfoWorker(Worker):
    def __init__(self, config={}):

        worker_type = "repo_info_worker"
        
        # Define what this worker can be given and know how to interpret
        given = [['github_url']]
        models = ['repo_info']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_info', 'repo']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Repo Info Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'GitHub API'

    def repo_info_model(self, task, repo_id):

        github_url = task['given']['github_url']

        self.logger.info("Beginning filling the repo_info model for repo: " + github_url + "\n")

        owner, repo = self.get_owner_repo(github_url)

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

        # Hit the graphql endpoint and retry 3 times in case of failure
        num_attempts = 0
        success = False
        data = None
        while num_attempts < 3:
            self.logger.info("Hitting endpoint: {} ...\n".format(url))
            r = requests.post(url, json={'query': query}, headers=self.headers)
            self.update_gh_rate_limit(r)

            try:
                data = r.json()
            except:
                data = json.loads(json.dumps(r.text))

            if 'errors' in data:
                self.logger.info("Error!: {}".format(data['errors']))
                if data['errors'][0]['message'] == 'API rate limit exceeded':
                    self.update_gh_rate_limit(r)
                    continue

            if 'data' in data:
                success = True
                data = data['data']['repository']
                break
            else:
                self.logger.info("Request returned a non-data dict: {}\n".format(data))
                if data['message'] == 'Not Found':
                    self.logger.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                    break
                if data['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                    self.update_gh_rate_limit(r, temporarily_disable=True)
                    continue
                if data['message'] == 'Bad credentials':
                    self.update_gh_rate_limit(r, bad_credentials=True)
                    continue
            num_attempts += 1
        if not success:
            self.logger.error('Cannot hit endpoint after 3 attempts. \"Completing\" task.\n')
            self.register_task_completion(self.task, repo_id, 'repo_info')
            return

        # Just checking that the data is accessible (would not be if repo no longer exists)
        try:
            data['updatedAt']
        except Exception as e:
            self.logger.error('Cannot access repo_info data: {}\nError: {}. \"Completing\" task.'.format(data, e))
            self.register_task_completion(self.task, repo_id, 'repo_info')
            return

        # Get committers count info that requires seperate endpoint
        committers_count = self.query_committers_count(owner, repo)

        # Put all data together in format of the table
        self.logger.info(f'Inserting repo info for repo with id:{repo_id}, owner:{owner}, name:{repo}\n')
        rep_inf = {
            'repo_id': repo_id,
            'last_updated': data['updatedAt'] if 'updatedAt' in data else None,
            'issues_enabled': data['hasIssuesEnabled'] if 'hasIssuesEnabled' in data else None,
            'open_issues': data['issues']['totalCount'] if data['issues'] else None,
            'pull_requests_enabled': None,
            'wiki_enabled': data['hasWikiEnabled'] if 'hasWikiEnabled' in data else None,
            'pages_enabled': None,
            'fork_count': data['forkCount'] if 'forkCount' in data else None,
            'default_branch': data['defaultBranchRef']['name'] if data['defaultBranchRef'] else None,
            'watchers_count': data['watchers']['totalCount'] if data['watchers'] else None,
            'UUID': None,
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
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source
        }

        result = self.db.execute(self.repo_info_table.insert().values(rep_inf))
        self.logger.info(f"Primary Key inserted into repo_info table: {result.inserted_primary_key}\n")
        self.results_counter += 1

        # Note that the addition of information about where a repository may be forked from, and whether a repository is archived, updates the `repo` table, not the `repo_info` table.
        forked = self.is_forked(owner, repo)
        archived = self.is_archived(owner, repo)
        archived_date_collected = None
        if archived is not False:
            archived_date_collected = archived
            archived = 1
        else:
            archived = 0

        rep_additional_data = {
            'forked_from': forked,
            'repo_archived': archived,
            'repo_archived_date_collected': archived_date_collected
        }
        result = self.db.execute(self.repo_table.update().where(
            self.repo_table.c.repo_id==repo_id).values(rep_additional_data))

        self.logger.info(f"Inserted info for {owner}/{repo}\n")

        # Register this task as completed
        self.register_task_completion(self.task, repo_id, "repo_info")

    def query_committers_count(self, owner, repo):
        self.logger.info('Querying committers count\n')
        url = f'https://api.github.com/repos/{owner}/{repo}/contributors?per_page=100'
        committers = 0

        try:
            while True:
                r = requests.get(url, headers=self.headers)
                self.update_gh_rate_limit(r)
                committers += len(r.json())

                if 'next' not in r.links:
                    break
                else:
                    url = r.links['next']['url']
        except Exception:
            self.logger.exception('An error occured while querying contributor count\n')

        return committers

    def is_forked(self, owner, repo): #/repos/:owner/:repo parent
        self.logger.info('Querying parent info to verify if the repo is forked\n')
        url = f'https://api.github.com/repos/{owner}/{repo}'

        r = requests.get(url, headers=self.headers)
        self.update_gh_rate_limit(r)

        data = self.get_repo_data(url, r)

        if 'fork' in data:
            if 'parent' in data:
                return data['parent']['full_name']
            return 'Parent not available'

        return False

    def is_archived(self, owner, repo):
        self.logger.info('Querying committers count\n')
        url = f'https://api.github.com/repos/{owner}/{repo}'

        r = requests.get(url, headers=self.headers)
        self.update_gh_rate_limit(r)

        data = self.get_repo_data(url, r)

        if 'archived' in data:
            if data['archived']:
                if 'updated_at' in data:
                    return data['updated_at']
                return 'Date not available'
            return False

        return False

    def get_repo_data(self, url, response):
        success = False
        try:
            data = response.json()
        except:
            data = json.loads(json.dumps(response.text))

        if 'errors' in data:
            self.logger.info("Error!: {}".format(data['errors']))
            if data['errors'][0]['message'] == 'API rate limit exceeded':
                self.update_gh_rate_limit(response)

        if 'id' in data:
            success = True
        else:
            self.logger.info("Request returned a non-data dict: {}\n".format(data))
            if data['message'] == 'Not Found':
                self.logger.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
            if data['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                self.update_gh_rate_limit(r, temporarily_disable=True)
            if data['message'] == 'Bad credentials':
                self.update_gh_rate_limit(r, bad_credentials=True)
        if not success:
            self.register_task_failure(self.task, repo_id, "Failed to hit endpoint: {}".format(url))

        return data
