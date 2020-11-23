#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker

class ExperienceWorker(Worker):
    def __init__(self, config={}):
        
        # Define the worker's type, which will be used for self identification.
        #   Should be unique among all workers and is the same key used to define 
        #   this worker's settings in the configuration file.
        worker_type = "experience_worker"

        # Define what this worker can be given and know how to interpret
        # given is usually either [['github_url']] or [['git_url']] (depending if your 
        # worker is exclusive to repos that are on the GitHub platform)
        given = [['github_url']]

        # The name the housekeeper/broker use to distinguish the data model this worker can fill
        #   You will also need to name the method that does the collection for this model
        #   in the format *model name*_model() such as fake_data_model() for example
        models = ['contributor_experience', 'repo_experience']

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
        self.tool_source = 'Fake Template Worker'
        self.tool_version = '0.0.0'
        self.data_source = 'Non-existent API'

    def initialize_database_connections(self):
        """ Custom initialize_database_connections method as to handle
            having to insert on the toss_specific schema 
        """
        DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            self.config['user_database'], self.config['password_database'], self.config['host_database'], self.config['port_database'], self.config['name_database']
        )

        # Create an sqlalchemy engine for both database schemas
        self.logger.info("Making database connections")

        db_schema = 'augur_data'
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

        for table in self.data_tables:
            setattr(self, '{}_table'.format(table), Base.classes[table].__table__)

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1

        # Organize different api keys/oauths available
        if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
            self.init_oauths(self.platform)
        else:
            self.oauths = [{'oauth_id': 0}]

    def get_language_from_extension(self, extension):
        if self.file_extension_language_map:
            return self.file_extension_language_map[extension]
        
        extension_language_sql = s.sql.text("""
            SELECT * FROM file_extension_language_map
        """)

        extension_language = pd.read_sql(cntrb_extensions_sql, self.db, params={})
        self.file_extension_language_map = {
            extension: language for extension, language in \
                zip(extension_language['file_extension'], extension_language['language'])
        }
        return self.get_language_from_extension(extension)

    def contributor_language_experience_model(self, task, repo_id):
        """ Collects data regarding contributors' experiences with different languages

            :param task: the task generated by the housekeeper and sent to the broker which 
            was then sent to this worker. Takes the example dict format of:
                {
                    'job_type': 'MAINTAIN', 
                    'models': ['fake_data'], 
                    'display_name': 'fake_data model for url: https://github.com/vmware/vivace',
                    'given': {
                        'git_url': 'https://github.com/vmware/vivace'
                    }
                }
            :param repo_id: the collect() method queries the repo_id given the git/github url
            and passes it along to make things easier. An int such as: 27869

        """

        cntrb_extensions_sql = s.sql.text("""
            SELECT cntrb_id, cntrb_login, extension, additions, deletions, additions + deletions as total_changed, 
                (additions + deletions) / SUM(additions + deletions) OVER (PARTITION BY cntrb_id) AS percentage,
                earliest_experience_time, latest_experience_time, commit_count, file_count
            FROM 
            (
                SELECT cntrb_id, cntrb_login, reverse(SPLIT_PART(reverse(pr_file_path), '.', 1)) AS extension, 
                    SUM(pr_file_additions) AS additions, SUM(pr_file_deletions) AS deletions, 
                    MIN(pr_cmt_date) as earliest_experience_time, MAX(pr_cmt_date) as latest_experience_time,
                    COUNT(DISTINCT pr_cmt_sha) as commit_count, COUNT(DISTINCT file_path) as file_count
                FROM augur_data.contributors LEFT OUTER JOIN augur_data.pull_requests ON 
                    pr_augur_contributor_id = cntrb_id LEFT OUTER JOIN augur_data.pull_request_files ON 
                    pull_requests.pull_request_id = pull_request_files.pull_request_id LEFT OUTER JOIN 
                    augur_data.pull_request_commits ON
                    pull_requests.pull_request_id = pull_request_commits.pull_request_id 
                WHERE pr_file_additions IS NOT NULL
                GROUP BY cntrb_id, extension
                ORDER BY cntrb_id DESC
            ) A
            GROUP BY cntrb_id, cntrb_login, extension, additions, deletions, 
                earliest_experience_time, latest_experience_time, commit_count, file_count
            ORDER BY cntrb_id, percentage DESC
        """)

        cntrb_extensions = pd.read_sql(cntrb_extensions_sql, self.db, params={})

        cntrb_language_row = {
            'augur_cntrb_id': cntrb_extensions['cntrb_id'],
            'language': self.get_language_from_extension(cntrb_extensions['extension']),
            'earliest_commit_time': cntrb_extensions['earliest_experience_time'],
            'latest_commit_time': cntrb_extensions['latest_experience_time'],
            'commit_count': cntrb_extensions['commit_count'],
            'file_count':

        }

        # Register this task as completed.
        #   This is a method of the worker class that is required to be called upon completion
        #   of any data collection model, this lets the broker know that this worker is ready
        #   for another task
        self.register_task_completion(task, repo_id, 'fake_data')

