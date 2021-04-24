#SPDX-License-Identifier: MIT
import os, subprocess
from datetime import datetime
import logging
import requests
import json
from urllib.parse import quote
from multiprocessing import Process, Queue

import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
from workers.worker_base import Worker

#THIS IS A PLACEHOLDER FILE AND NEEDS MORE EDITS
#IT'S CURRENTLY BASICALLY A COPY OF VALUE WORKER TO SERVE AS A CODE STUB
#PROBABLY DOESN'T WORK

class DepsWorker(Worker):
    def __init__(self, config={}):

        worker_type = "deps_worker"

        # Define what this worker can be given and know how to interpret
        given = [['git_url']]
        models = ['deps']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_labor']
        operations_tables = ['worker_history', 'worker_job']


        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        self.config.update({
            'repo_directory': self.augur_config.get_deps('Workers', 'facade_worker')['repo_directory']
        })

        self.tool_source = 'Deps Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'SCC'

    def deps_model(self, entry_info, repo_id):
        """ Data collection and storage method
        """
        self.logger.info(entry_info)
        self.logger.info(repo_id)

        repo_path_sql = s.sql.text("""
            SELECT repo_id, CONCAT(repo_group_id || chr(47) || repo_path || repo_name) AS path
            FROM repo
            WHERE repo_id = :repo_id
        """)

        relative_repo_path = self.db.execute(repo_path_sql, {'repo_id': repo_id}).fetchone()[1]
        absolute_repo_path = self.config['repo_directory'] + relative_repo_path

        try:
            self.generate_deps_data(repo_id, absolute_repo_path)
        except Exception as e:
            self.logger.error(e)

        self.register_task_completion(entry_info, repo_id, "deps")

    def generate_deps_data(self, repo_id, path):
        """Runs scc on repo and stores data in database

        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        self.logger.info('Running `scc`....')
        self.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        output = subprocess.check_output([self.config['scc_bin'], '-f', 'json', path])
        records = json.loads(output.decode('utf8'))

        for record in records:
            for file in record['Files']:
                repo_labor = {
                    'repo_id': repo_id,
                    'rl_analysis_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'programming_language': file['Language'],
                    'file_path': file['Location'],
                    'file_name': file['Filename'],
                    'total_lines': file['Lines'],
                    'code_lines': file['Code'],
                    'comment_lines': file['Comment'],
                    'blank_lines': file['Blank'],
                    'code_complexity': file['Complexity'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                }

                result = self.db.execute(self.repo_labor_table.insert().deps(repo_labor))
                self.logger.info(f"Added Repo Labor Data: {result.inserted_primary_key}")
