#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json, re
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

from workers.worker_base import Worker

class LibraryExperienceWorker(Worker):
    def __init__(self, config={}):

        # Define the worker's type, which will be used for self identification.
        #   Should be unique among all workers and is the same key used to define
        #   this worker's settings in the configuration file.
        worker_type = "library_experience_worker"

        # Define what this worker can be given and know how to interpret
        # given is usually either [['github_url']] or [['git_url']] (depending if your
        # worker is exclusive to repos that are on the GitHub platform)
        given = [['github_url']]

        # The name the housekeeper/broker use to distinguish the data model this worker can fill
        #   You will also need to name the method that does the collection for this model
        #   in the format *model name*_model() such as fake_data_model() for example
        models = ['contributor_library_experience', 'repo_library_experience']

        # Define the tables needed to insert, update, or delete on
        #   The Worker class will set each table you define here as an attribute
        #   so you can reference all of them like self.message_table or self.repo_table
        data_tables = []
        # For most workers you will only need the worker_history and worker_job tables
        #   from the operations schema, these tables are to log worker task histories
        operations_tables = ['worker_history', 'worker_job']

        self.toss_tables = ['contributor_library_experience', 'contributor_language_experience',
            'repo_library_info', 'repo_language_info']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Do any additional configuration after the general initialization has been run
        self.config.update(config)

        # If you need to do some preliminary interactions with the database, these MUST go
        # in the model method. The database connection is instantiated only inside of each
        # data collection process
        self.file_extension_language_map = None

        # Define data collection info
        self.tool_source = 'Library Experience Worker'
        self.tool_version = '0.1.0'
        self.data_source = 'GitHub'

    def initialize_database_connections(self):
        """ Custom initialize_database_connections method as to handle
            having to insert on the toss_specific schema
        """
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user_database'], self.config['password_database'], self.config['host_database'], self.config['port_database'], self.config['name_database']
        )

        # Create an sqlalchemy engine for both database schemas
        self.logger.info("Making database connections")

        db_schema = 'augur_data,toss_specific'
        self.db = s.create_engine(DB_STR,  poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(db_schema)})

        helper_schema = 'augur_operations'
        self.helper_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(helper_schema)})

        toss_schema = 'toss_specific'
        self.toss_db = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(toss_schema)})

        metadata = MetaData()
        helper_metadata = MetaData()
        toss_metadata = MetaData()

        # Reflect only the tables we will use for each schema's metadata object
        metadata.reflect(self.db, only=self.data_tables)
        helper_metadata.reflect(self.helper_db, only=self.operations_tables)
        toss_metadata.reflect(self.toss_db, only=self.toss_tables)

        Base = automap_base(metadata=metadata)
        HelperBase = automap_base(metadata=helper_metadata)
        TossBase = automap_base(metadata=toss_metadata)

        Base.prepare()
        HelperBase.prepare()
        TossBase.prepare()

        # So we can access all our tables when inserting, updating, etc
        for table in self.data_tables:
            setattr(self, '{}_table'.format(table), Base.classes[table].__table__)

        for table in self.operations_tables:
            setattr(self, '{}_table'.format(table), HelperBase.classes[table].__table__)

        for table in self.toss_tables:
            setattr(self, '{}_table'.format(table), TossBase.classes[table].__table__)

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1

        # Organize different api keys/oauths available
        # if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
        #     self.init_oauths(self.platform)
        # else:
        self.oauths = [{'oauth_id': 0}]

    def find_python_dependencies(self, owner, repo):
        requirements_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{self.repo_info['default_branch']}/requirements.txt"
        response = requests.get(requirements_url)
        if response.ok is False:
            self.logger.info(f"A valid requirements.txt file could not be found on the default {self.repo_info['default_branch']} branch\n")
            return []
        else:
            libraries = [re.sub(r"(?:\W\=)(?:.*)", "", library) for library in response.text.split("\n") if library != ""]
            self.logger.info(f"Found {len(libraries)} Pyton dependencies in requirements.txt\n")
            return libraries

    def get_repo_info(self, owner, repo):
        repo_info_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.repo_info = requests.get(repo_info_url).json()

    def repo_library_experience_model(self, task, repo_id):
        github_url = task['given']['github_url']

        self.logger.info("Beginning filling the repo_info model for repo: " + github_url + "\n")

        owner, repo = self.get_owner_repo(github_url)
        self.get_repo_info(owner, repo)

        languages_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
        top_3_languages = [language for language in requests.get(languages_url).json()][:3]

        if "Python" in top_3_languages:
            self.logger.info("Searching for Python dependencies...\n")

            python_libraries = []
            python_libraries = self.find_python_dependencies(owner, repo)

            python_libraries_insert = [
                {
                    'repo_id': repo_id,
                    'library': library_name,
                    'percentage': None,
                    'commit_count': None,
                    'file_count': None,
                    'earliest_commit_time': None,
                    'latest_commit_time': None
                } for library_name in python_libraries
            ]
            if len(python_libraries_insert) > 0:
                python_libraries_insert_result = self.bulk_insert(self.repo_library_info_table, insert=python_libraries_insert)

        self.register_task_completion(task, repo_id, 'repo_library_experience')