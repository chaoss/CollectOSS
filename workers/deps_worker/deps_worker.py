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

from workers.deps_worker import dependancy_calculator as dep_calc

class DepsWorker(WorkerGitInterfaceable):
    def __init__(self, config={}):

        worker_type = "deps_worker"

        # Define what this worker can be given and know how to interpret
        given = [['git_url']]
        models = ['deps', 'ossf_scorecard']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_dependencies', 'repo_deps_scorecard']
        operations_tables = ['worker_history', 'worker_job']


        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        self.config.update({
            'repo_directory': self.augur_config.get_value('Workers', 'facade_worker')['repo_directory']
        })

        self.tool_source = 'Deps Worker'
        self.tool_version = '2.0.0'
        self.data_source = 'Augur Repository Data'

    def deps_model(self, entry_info, repo_id):
        """ Data collection and storage method
        """
        self.logger.info(f"This is the deps model entry info: {entry_info}.")
        self.logger.info(f"This is the deps model repo: {repo_id}.")

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
            self.print_traceback("Deps model: generate_deps_data", e, True)

        self.register_task_completion(entry_info, repo_id, "deps")

    def ossf_scorecard_model(self, entry_info, repo_id):
        """ Data collection and storage method
        """
        self.logger.info('Scorecard Model called...')
        self.logger.info(f"The entry info: {entry_info}.")
        self.logger.info(f"The repo id: {repo_id}.")

        repo_path_sql = s.sql.text("""
            SELECT repo_id, repo_git AS path
            FROM repo
            WHERE repo_id = :repo_id
        """)

        scorecard_repo_path = self.db.execute(repo_path_sql, {'repo_id': repo_id}).fetchone()[1]
        # absolute_repo_path = self.config['repo_directory'] + relative_repo_path
## TODO: Flesh out generate_scorecard 
## You can look at the Value worker to see how Go Programs are already called in Augur.
#  
        try:
            self.generate_scorecard(repo_id, scorecard_repo_path)
        except Exception as e:
            self.print_traceback("Depts model: scorecard generation", e, True)

        self.register_task_completion(entry_info, repo_id, "deps")


    def generate_scorecard(self, repo_id, path): 
        """Runs scorecard on repo and stores data in database
        :param repo_id: Repository ID
        :param path: URL path of the Repostiory
        """
        self.logger.info('Generating scorecard data for repo...')
        self.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        # we convert relative path in the format required by scorecard like github.com/chaoss/augur
        # raw_path,_ = path.split('-')
        # scorecard_repo_path = raw_path[2:]
        path = path[8:]
        if path[-4:] == '.git':
            path = path.replace(".git", "")
        command = '--repo='+ path
        
        #this is path where our scorecard project is located
        path_to_scorecard = os.environ['HOME'] + '/scorecard'

        #setting the environmental variable which is required by scorecard  
        
        os.environ['GITHUB_AUTH_TOKEN'] = self.config['gh_api_key']
        

        p= subprocess.run(['./scorecard', command], cwd= path_to_scorecard ,capture_output=True, text=True, timeout=None)
        self.logger.info('subprocess completed successfully... ')
        output = p.stdout.split('\n')
        required_output = output[4:20]
        
       

        self.logger.info('adding to database...')
        
        try: 
            for test in required_output:
                temp = test.split()
                repo_deps_scorecard = {
                    'repo_id': repo_id,
                    'name': temp[0],
                    'status': temp[1],
                    'score': temp[2],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

                }  
                result = self.db.execute(self.repo_deps_scorecard_table.insert().values(repo_deps_scorecard)) 
                self.logger.info(f"Added OSSF scorecard data : {result.inserted_primary_key}") 
        except Exception as e:
            self.print_traceback("inserting scorecard info for deps_worker", e, True)

    def generate_deps_data(self, repo_id, path):
        """Runs scc on repo and stores data in database

        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        self.logger.info('Searching for deps in repo')
        self.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        deps = dep_calc.get_deps(path)
        try: 
            for dep in deps:
                    repo_deps = {
                        'repo_id': repo_id,
                        'dep_name' : dep.name,
    	                'dep_count' : dep.count,
    	                'dep_language' : dep.language,
                        'tool_source': self.tool_source,
                        'tool_version': self.tool_version,
                        'data_source': self.data_source,
                        'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    result = self.db.execute(self.repo_dependencies_table.insert().values(repo_deps))
                    self.logger.info(f"Added dep: {result.inserted_primary_key}")
        except Exception as e:
            self.print_traceback("Deps worker: generate_deps_data", e, True)
