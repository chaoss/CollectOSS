#SPDX-License-Identifier: MIT
import os, subprocess
from datetime import datetime
import logging
from workers.worker_git_integration import WorkerGitInterfaceable
import requests
import json
from urllib.parse import quote
from multiprocessing import Process, Queue

import traceback

import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from workers.worker_base import Worker

# from workers.deps_worker import dependancy_calculator as dep_calc
from libyear_utils import get_deps_libyear_data

class DepsLibyearWorker(WorkerGitInterfaceable):
    def __init__(self, config={}):

        worker_type = "deps_libyear_worker"

        # Define what this worker can be given and know how to interpret
        given = [['git_url']]
        models = ['deps_libyear']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_deps_libyear']
        operations_tables = ['worker_history', 'worker_job']


        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        self.config.update({
            'repo_directory': self.augur_config.get_value('Workers', 'facade_worker')['repo_directory']
        })

        self.tool_source = 'Deps Libyear Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'Augur Repository Data'

    def deps_libyear_model(self, entry_info, repo_id):
        """ Data collection and storage method
        """
        self.logger.info(f"This is the entry info: {entry_info}.")
        self.logger.info(f"This is the repo id: {repo_id}")

        repo_path_sql = s.sql.text("""
            SELECT repo_id, CONCAT(repo_group_id || chr(47) || repo_path || repo_name) AS path
            FROM repo
            WHERE repo_id = :repo_id
        """)

        relative_repo_path = self.db.execute(repo_path_sql, {'repo_id': repo_id}).fetchone()[1]
        absolute_repo_path = self.config['repo_directory'] + relative_repo_path

        try:
            self.generate_deps_libyear_data(repo_id, absolute_repo_path)
        except Exception as e:
            self.print_traceback("Deps_libyear_worker: generate_deps_libyear_data", e, True)

        self.register_task_completion(entry_info, repo_id, "deps_libyear")

    def generate_deps_libyear_data(self, repo_id, path):
        """Scans for package files and calculates libyear 

        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        self.logger.info('Searching for deps in repo')
        self.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        deps = get_deps_libyear_data(path)

        try: 

            for dep in deps:
                    repo_deps = {
                        'repo_id': repo_id,
                        'name' : dep['name'],
    	                'requirement' : dep['requirement'],
    	                'type' : dep['type'],
                        'package_manager' : dep['package'],
                        'current_verion' : dep['current_version'],
                        'latest_version' : dep['latest_version'],
                        'current_release_date' : dep['current_release_date'],
                        'latest_release_date' : dep['latest_release_date'],
                        'libyear' : dep['libyear'],
                        'tool_source': self.tool_source,
                        'tool_version': self.tool_version,
                        'data_source': self.data_source,
                        'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    result = self.db.execute(self.repo_deps_libyear_table.insert().values(repo_deps))
                    self.logger.info(f"Added dep: {result.inserted_primary_key}")
        except Exception as e:
            self.print_traceback("Deps_libyear_worker: generating and inserting data", e, True)
