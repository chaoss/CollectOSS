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

from workers.deps_worker import dependancy_calculator as dep_calc

class DepsWorker(Worker):
    def __init__(self, config={}):

        worker_type = "deps_worker"

        # Define what this worker can be given and know how to interpret
        given = [['git_url']]
        models = ['deps', 'ossf_scorecard']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['repo_dependencies', '_dev1_repo_deps_scorecard']
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

    def ossf_scorecard_model(self, entry_info, repo_id):
        """ Data collection and storage method
        """
        self.logger.info('Scorecard Model called...')
        self.logger.info(entry_info)
        self.logger.info(repo_id)

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
            self.logger.error(e)

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
        command = '--repo='+ path
        self.logger.info('command generated..')
        #this is path where our scorecard project is located
        path_to_scorecard = os.environ['HOME'] + '/scorecard'

        #setting the enviror scorecard if it does not exsists alreadyonment variable f 
        
        os.environ['GITHUB_AUTH_TOKEN'] = self.config['gh_api_key']

        p= subprocess.run(['./scorecard', command], cwd= path_to_scorecard ,capture_output=True, text=True)
        self.logger.info('subprocess completed successfully... ')
        output = p.stdout.split('\n')
        required_output = output[4:20]
        self.logger.info('required output generated..')
        # here scorecard becomes a list of lists where it has list of 16 list in which each list is a test and has name, status and score. 
        scorecard_score = dict()
        scorecard_status = dict()
        self.logger.info('adding to list...')
        for test in required_output:
            temp = test.split()
            scorecard_status[temp[0]] = temp[1]
            scorecard_score[temp[0]] = temp[2]

        self.logger.info('adding to database')
        repo_deps_scorecard = {
            'repo_id': repo_id,
            "ossf_active_status": scorecard_status.get('Active:'),
            "ossf_automated_dendency_update_status": scorecard_status.get('Automatic-Dependency-Update:'),
            "ossf_branch_protection_status": scorecard_status.get('Branch-Protection:'),
            "ossf_ci_tests_status": scorecard_status.get('CI-Tests:'),
            "ossf_cii_best_practices_status": scorecard_status.get('CII-Best-Practices:'),
            "ossf_code_review_status": scorecard_status.get('Code-Review:'),
            "ossf_contributors_status":scorecard_status.get('Contributors:'),
            "ossf_frozen_deps_status": scorecard_status.get('Frozen-Deps:'),
            "ossf_fuzzing_status": scorecard_status.get('Fuzzing:'),
            "ossf_packaging_status": scorecard_status.get('Packaging:'),
            "ossf_pull_request_status": scorecard_status.get('Pull-Requests:'),
            "ossf_sast_status": scorecard_status.get('SAST:'),
            "ossf_security_policy_status": scorecard_status.get('Security-Policy:'),
            "ossf_signed_releases_status":scorecard_status.get('Signed-Releases:'),
            "ossf_signed_tags_status":scorecard_status.get('Signed-Tags:'),
            "ossf_token_permissions_status": scorecard_status.get('Token-Permissions:'),
            "ossf_active_score": scorecard_score.get('Active:'),
            "ossf_automated_dendency_update_score": scorecard_score.get('Automatic-Dependency-Update:'),
            "ossf_branch_protection_score":scorecard_score.get('Branch-Protection:'),
            "ossf_ci_tests_score": scorecard_score.get('CI-Tests:'),
            "ossf_cii_best_practices_score": scorecard_score.get('CII-Best-Practices:'),
            "ossf_code_review_score": scorecard_score.get('Code-Review:'),
            "ossf_contributors_score":scorecard_score.get('Contributors:'),
            "ossf_frozen_deps_score": scorecard_score.get('Frozen-Deps:'),
            "ossf_fuzzing_score": scorecard_score.get('Fuzzing:'),
            "ossf_packaging_score": scorecard_score.get('Packaging:'),
            "ossf_pull_request_score": scorecard_score.get('Pull-Requests:'),
            "ossf_sast_score": scorecard_score.get('SAST:'),
            "ossf_security_policy_score": scorecard_score.get('Security-Policy:'),
            "ossf_signed_releases_score": scorecard_score.get('Signed-Releases:'), 
            "ossf_signed_tags_score": scorecard_score.get('Signed-Tags:'),
            "ossf_token_permissions_score": scorecard_score.get('Token-Permissions:'),
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source,
            'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

        }  
        result = self.db.execute(self._dev1_repo_deps_scorecard_table.insert().values(repo_deps_scorecard)) 
        self.logger.info(f"Added OSSF scorecard data : {result.inserted_primary_key}") 



    def generate_deps_data(self, repo_id, path):
        """Runs scc on repo and stores data in database

        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        self.logger.info('Searching for deps in repo')
        self.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        deps = dep_calc.get_deps(path)

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
