#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker

class ContributorBreadthWorker(Worker):
    def __init__(self, config={}):
        
    
        worker_type = "contributor_breadth_worker"

    
        given = [['github_url']]


        models = ['contributor_breadth']


        data_tables = ['contributor_repo']

        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'Contributor Breadth Worker'
        self.tool_version = '0.0.0'
        self.data_source = 'GitHub API'

        # Do any additional configuration after the general initialization has been run
        self.config.update(config)

    def contributor_breadth_model(self, task, repo_id):


        cntrb_login_query = s.sql.text("""
            SELECT DISTINCT gh_login, cntrb_id 
            FROM augur_data.contributors 
            WHERE gh_login IS NOT NULL
        """)

        cntrb_logins = json.loads(pd.read_sql(cntrb_login_query, self.db, \
            params={}).to_json(orient="records"))

        action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['event_id']
            }
        }

        for cntrb in cntrb_logins:

            repo_cntrb_url = f"https://api.github.com/users/{cntrb['gh_login']}/events"

            source_cntrb_repos = self.paginate_endpoint(repo_cntrb_url, action_map=action_map,
                 table=self.contributor_repo_table)

            if len(source_cntrb_repos['all']) == 0:
                self.logger.info("There are no issues for this repository.\n")
                self.register_task_completion(task, repo_id, 'contributor_breadth')

            cntrb_repos_insert = [
                {
                    "cntrb_id": cntrb['cntrb_id'],
                    "repo_git": cntrb_repo['repo']['url'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "repo_name": cntrb_repo['repo']['name'],
                    "gh_repo_id": cntrb_repo['repo']['id'],
                    "cntrb_category": cntrb_repo['type'],
                    "event_id": cntrb_repo['id'],
                    "created_at": cntrb_repo['created_at']['created_at']
                } for cntrb_repo in source_cntrb_repos['insert']
            ]

            if len(source_cntrb_repos['insert']) > 0:

                cntrb_repo_insert_result, cntrb_repo_update_result = self.bulk_insert(self.contributor_repo_table,
                     unique_columns=action_map['insert']['augur'], insert=cntrb_repos_insert)

 
        self.register_task_completion(task, None, 'contributor_breadth')

