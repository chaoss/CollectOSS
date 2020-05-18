import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base
from workers.worker_template import Worker

class RepoInfoWorker(Worker):
    def __init__(self, config):
        
        # Define what this worker can be given and know how to interpret
        given = [['github_url']]
        models = ['repo_info']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_info']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Repo Info Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'GitHub API'

    def repo_info_model(self, task, repo_id):

        github_url = task['given']['github_url']

        logging.info("Beginning filling the repo_info model for repo: " + github_url + "\n")

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
        while num_attempts < 3:
            logging.info("Hitting endpoint: {} ...\n".format(url))
            r = requests.post(url, json={'query': query}, headers=self.headers)
            self.update_gh_rate_limit(r)

            try:
                j = r.json()
            except:
                j = json.loads(json.dumps(r.text))

            if 'errors' in j:
                logging.info("Error!: {}".format(j['errors']))
                if j['errors']['message'] == 'API rate limit exceeded':
                    self.update_gh_rate_limit(r)
                    continue

            if 'data' in j:
                success = True
                j = j['data']['repository']
                break
            else:
                logging.info("Request returned a non-data dict: {}\n".format(j))
                if j['message'] == 'Not Found':
                    logging.info("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                    break
                if j['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                    self.update_gh_rate_limit(r, temporarily_disable=True)
                    continue
                if j['message'] == 'Bad credentials':
                    self.update_gh_rate_limit(r, bad_credentials=True)
                    continue
            num_attempts += 1
        if not success:
            self.register_task_failure(task, repo_id, "Failed to hit endpoint: {}".format(url))
            return

        # Get committers count info that requires seperate endpoint
        committers_count = self.query_committers_count(owner, repo)

        # Put all data together in format of the table
        logging.info(f'Inserting repo info for repo with id:{repo_id}, owner:{owner}, name:{repo}\n')
        rep_inf = {
            'repo_id': repo_id,
            'last_updated': j['updatedAt'] if 'updatedAt' in j else None,
            'issues_enabled': j['hasIssuesEnabled'] if 'hasIssuesEnabled' in j else None,
            'open_issues': j['issues']['totalCount'] if j['issues'] else None,
            'pull_requests_enabled': None,
            'wiki_enabled': j['hasWikiEnabled'] if 'hasWikiEnabled' in j else None,
            'pages_enabled': None,
            'fork_count': j['forkCount'] if 'forkCount' in j else None,
            'default_branch': j['defaultBranchRef']['name'] if j['defaultBranchRef'] else None,
            'watchers_count': j['watchers']['totalCount'] if j['watchers'] else None,
            'UUID': None,
            'license': j['licenseInfo']['name'] if j['licenseInfo'] else None,
            'stars_count': j['stargazers']['totalCount'] if j['stargazers'] else None,
            'committers_count': committers_count,
            'issue_contributors_count': None,
            'changelog_file': None,
            'contributing_file': None,
            'license_file': j['licenseInfo']['url'] if j['licenseInfo'] else None,
            'code_of_conduct_file': j['codeOfConduct']['url'] if j['codeOfConduct'] else None,
            'security_issue_file': None,
            'security_audit_file': None,
            'status': None,
            'keywords': None,
            'commit_count': j['ref']['target']['history']['totalCount'] if j['ref'] else None,
            'issues_count': j['issue_count']['totalCount'] if j['issue_count'] else None,
            'issues_closed': j['issues_closed']['totalCount'] if j['issues_closed'] else None,
            'pull_request_count': j['pr_count']['totalCount'] if j['pr_count'] else None,
            'pull_requests_open': j['pr_open']['totalCount'] if j['pr_open'] else None,
            'pull_requests_closed': j['pr_closed']['totalCount'] if j['pr_closed'] else None,
            'pull_requests_merged': j['pr_merged']['totalCount'] if j['pr_merged'] else None,
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source
        }

        result = self.db.execute(self.repo_info_table.insert().values(rep_inf))
        logging.info(f"Primary Key inserted into repo_info table: {result.inserted_primary_key}\n")
        self.results_counter += 1

        logging.info(f"Inserted info for {owner}/{repo}\n")

        #Register this task as completed
        self.register_task_completion(task, repo_id, "repo_info")

    def query_committers_count(self, owner, repo):
        logging.info('Querying committers count\n')
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
            logging.exception('An error occured while querying contributor count\n')

        return committers

