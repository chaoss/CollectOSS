#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker
from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base

class ExperienceWorker(Worker):
    def __init__(self, config={}):
        
        # Define the worker's type, which will be used for self identification.
        #   Should be unique among all workers and is the same key used to define 
        #   this worker's settings in the configuration file.
        worker_type = "experience_worker"

        # Define what this worker can be given and know how to interpret
        # given is usually either [['github_url']] or [['git_url']] (depending if your 
        # worker is exclusive to repos that are on the GitHub platform)
        given = [[]]

        # The name the housekeeper/broker use to distinguish the data model this worker can fill
        #   You will also need to name the method that does the collection for this model
        #   in the format *model name*_model() such as fake_data_model() for example
        models = ['contributor_language_experience', 'repo_language_info', 'language_experience', 
            'contributor_keyword_experience']

        # Define the tables needed to insert, update, or delete on
        #   The Worker class will set each table you define here as an attribute
        #   so you can reference all of them like self.message_table or self.repo_table
        data_tables = []
        # For most workers you will only need the worker_history and worker_job tables
        #   from the operations schema, these tables are to log worker task histories
        operations_tables = ['worker_history', 'worker_job']

        self.toss_tables = ['contributor_library_experience', 'contributor_language_experience',
            'repo_library_info', 'repo_language_info', 'file_extension_language_map', 
            'contributor_keyword_experience']

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

        for table in self.toss_tables:
            setattr(self, '{}_table'.format(table), TossBase.classes[table].__table__)

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1

        # Organize different api keys/oauths available
        if 'gh_api_key' in self.config or 'gitlab_api_key' in self.config:
            self.init_oauths(self.platform)
        else:
            self.oauths = [{'oauth_id': 0}]

    def get_language_from_extension(self, extension):
        if self.file_extension_language_map:
            try:
                return self.file_extension_language_map[extension]
            except:
                return f"Language not found for extension: {extension}"
        
        self.logger.info("First time calling get_language_from_extension, querying all "
            "file_extension_language_map rows...\n")
        extension_language_sql = s.sql.text("""
            SELECT * FROM toss_specific.file_extension_language_map
        """)

        extension_language = pd.read_sql(extension_language_sql, self.db, params={})
        self.file_extension_language_map = {
            extension: language for extension, language in \
                zip(extension_language['file_extension'], extension_language['language'])
        }
        return self.get_language_from_extension(extension)

    def language_experience_model(self, task, repo_id):
        self.contributor_language_experience_model(task, repo_id)
        self.repo_language_experience_model(task, repo_id)
        self.register_task_completion(task, None, 'language_experience')

    def timestamp_if_not_null(self, input):
        return None if not input or np.isnat(datetime.fromtimestamp(input/1000)) else \
            datetime.fromtimestamp(input/1000)

    def contributor_language_experience_model(self, task):
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
            SELECT cntrb_id, cntrb_login, extension, additions, deletions, additions + deletions AS total_changed, 
                (additions + deletions) / CASE SUM(additions + deletions) OVER (PARTITION BY cntrb_id)
                    WHEN 0 THEN 1
                    ELSE SUM(additions + deletions) OVER (PARTITION BY cntrb_id)
                END AS percentage,
                earliest_experience_time, latest_experience_time, commit_count, file_count
            FROM 
            (
                SELECT cntrb_id, cntrb_login, reverse(SPLIT_PART(reverse(pr_file_path), '.', 1)) AS extension, 
                    SUM(pr_file_additions) AS additions, SUM(pr_file_deletions) AS deletions, 
                    MIN(pr_cmt_date) AS earliest_experience_time, MAX(pr_cmt_date) AS latest_experience_time,
                    COUNT(DISTINCT pr_cmt_sha) AS commit_count, COUNT(DISTINCT pr_file_path) AS file_count
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

        self.logger.info("Querying aggregated contributor language contribution data...\n")
        cntrb_extensions = pd.read_sql(cntrb_extensions_sql, self.db, params={})

        self.logger.info("Applying extension -> language map for every row of data...\n")
        cntrb_extensions['language'] = cntrb_extensions.apply(
            lambda row: self.get_language_from_extension(row['extension']), axis=1)

        cntrb_extensions = json.loads(cntrb_extensions.to_json(
            orient='records'))

        cntrb_language_action_map = {
            'insert': {
                'source': ['cntrb_id', 'language'],
                'augur': ['augur_cntrb_id', 'language']
            },
            'update': {
                'source': ['additions', 'deletions', 'latest_experience_time', 'commit_count', 'file_count'],
                'augur': ['loc_additions', 'loc_deletions', 'latest_commit_time', 'commit_count', 'file_count']
            }
        }
        
        cols_to_query = self.get_relevant_columns(self.contributor_language_experience_table, 
            cntrb_language_action_map)

        self.logger.info("Querying all contributor_language_experience table rows...\n")
        table_values = self.toss_db.execute(s.sql.select(cols_to_query)).fetchall()

        source_cntrb_language_insert, source_cntrb_language_update = self.organize_needed_data(
            cntrb_extensions, table_values, 
            list(self.contributor_language_experience_table.primary_key)[0].name, 
            action_map=cntrb_language_action_map)

        cntrb_language_insert = [{
            'augur_cntrb_id': cntrb_extension['cntrb_id'],
            'language': cntrb_extension['language'],
            'earliest_commit_time': self.timestamp_if_not_null(cntrb_extension['earliest_experience_time']),
            'latest_commit_time': self.timestamp_if_not_null(cntrb_extension['latest_experience_time']),
            'commit_count': cntrb_extension['commit_count'],
            'file_count': cntrb_extension['file_count'],
            'loc_additions': cntrb_extension['additions'],
            'loc_deletions': cntrb_extension['deletions']
        } for cntrb_extension in cntrb_extensions]

        self.bulk_insert(self.contributor_language_experience_table, insert=cntrb_language_insert,
            update=source_cntrb_language_update, unique_columns=cntrb_language_action_map['insert']['augur'],
            update_columns=cntrb_language_action_map['update']['augur'], database=self.toss_db)

        # Register this task as completed.
        #   This is a method of the worker class that is required to be called upon completion
        #   of any data collection model, this lets the broker know that this worker is ready
        #   for another task
        self.register_task_completion(task, None, 'contributor_language_experience')

    def repo_language_info_model(self, task):
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

        repo_extensions_sql = s.sql.text("""
            SELECT repo_id, repo_git, extension, additions, deletions, additions + deletions AS total_changed, 
                (additions + deletions) / CASE SUM(additions + deletions) OVER (PARTITION BY repo_id)
                    WHEN 0 THEN 1
                    ELSE SUM(additions + deletions) OVER (PARTITION BY repo_id) END AS percentage,
                earliest_experience_time, latest_experience_time, commit_count, file_count
            FROM 
            (
                SELECT repo.repo_id, repo_git, reverse(SPLIT_PART(reverse(pr_file_path), '.', 1)) AS extension, 
                        SUM(pr_file_additions) AS additions, SUM(pr_file_deletions) AS deletions, 
                        MIN(pr_cmt_date) AS earliest_experience_time, MAX(pr_cmt_date) AS latest_experience_time,
                        COUNT(DISTINCT pr_cmt_sha) AS commit_count, COUNT(DISTINCT pr_file_path) AS file_count
                FROM augur_data.repo LEFT OUTER JOIN augur_data.pull_requests ON 
                        pull_requests.repo_id = repo.repo_id LEFT OUTER JOIN augur_data.pull_request_files ON 
                        pull_requests.pull_request_id = pull_request_files.pull_request_id LEFT OUTER JOIN 
                        augur_data.pull_request_commits ON
                        pull_requests.pull_request_id = pull_request_commits.pull_request_id 
                WHERE pr_file_additions IS NOT NULL
                GROUP BY repo.repo_id, extension
                ORDER BY repo.repo_id DESC
            ) A
            GROUP BY repo_id, repo_git, extension, additions, deletions, 
                earliest_experience_time, latest_experience_time, commit_count, file_count
            ORDER BY repo_id, percentage DESC
        """)

        self.logger.info("Querying aggregated repo language contribution data...\n")
        repo_extensions = pd.read_sql(repo_extensions_sql, self.db, params={})

        self.logger.info("Applying extension -> language map for every row of data...\n")
        repo_extensions['language'] = repo_extensions.apply(
            lambda row: self.get_language_from_extension(row['extension']), axis=1)
        repo_extensions= json.loads(repo_extensions.to_json(
            orient='records'))

        repo_language_action_map = {
            'insert': {
                'source': ['repo_id', 'language'],
                'augur': ['repo_id', 'language']
            },
            'update': {
                'source': ['additions', 'deletions', 'latest_experience_time', 'commit_count', 'file_count'],
                'augur': ['loc_additions', 'loc_deletions', 'latest_commit_time', 'commit_count', 'file_count']
            }
        }
        
        cols_to_query = self.get_relevant_columns(self.repo_language_info_table, 
            repo_language_action_map)

        table_values = self.toss_db.execute(s.sql.select(cols_to_query)).fetchall()

        source_repo_language_insert, source_repo_language_update = self.organize_needed_data(
            repo_extensions, table_values, 
            list(self.repo_language_info_table.primary_key)[0].name, 
            action_map=repo_language_action_map)

        repo_language_insert = [{
            'repo_id': repo_extension['repo_id'],
            'language': repo_extension['language'],
            'percentage': repo_extension['percentage'],
            'earliest_commit_time': self.timestamp_if_not_null(repo_extension['earliest_experience_time']),
            'latest_commit_time': self.timestamp_if_not_null(repo_extension['latest_experience_time']),
            'commit_count': repo_extension['commit_count'],
            'file_count': repo_extension['file_count'],
            'loc_additions': repo_extension['additions'],
            'loc_deletions': repo_extension['deletions']
        } for repo_extension in repo_extensions]

        self.bulk_insert(self.repo_language_info_table, insert=repo_language_insert,
            update=source_repo_language_update, unique_columns=repo_language_action_map['insert']['augur'],
            update_columns=repo_language_action_map['update']['augur'], database=self.toss_db)

        # Register this task as completed.
        #   This is a method of the worker class that is required to be called upon completion
        #   of any data collection model, this lets the broker know that this worker is ready
        #   for another task
        self.register_task_completion(task, None, 'repo_language_info')

    def contributor_keyword_experience_model(self, task, repo_id):
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

        contributor_keyword_sql = s.sql.text("""
            SELECT canonical_id, cntrb_canonical, unnest(keywords) as keyword FROM (
                SELECT repo_id, canonical_id, cntrb_canonical FROM augur_data.pull_requests LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = pull_requests.pr_augur_contributor_id
                    LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                    FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                    ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                GROUP BY repo_id, canonical_id, cntrb_canonical
            ) contributor_repo LEFT OUTER JOIN augur_data.repo_info on contributor_repo.repo_id = repo_info.repo_id
            WHERE canonical_id IS NOT NULL
        """)

        self.logger.info("Querying contributor keyword data...\n")
        contributor_keywords = json.loads(pd.read_sql(contributor_keyword_sql, self.db, params={}
            ).to_json(orient='records'))

        contributor_keyword_action_map = {
            'insert': {
                'source': ['canonical_id', 'keyword'],
                'augur': ['augur_cntrb_id', 'keyword']
            }
        }
        
        cols_to_query = self.get_relevant_columns(self.contributor_keyword_experience_table, 
            contributor_keyword_action_map)

        table_values = self.toss_db.execute(s.sql.select(cols_to_query)).fetchall()

        source_contributor_keyword_insert, _ = self.organize_needed_data(
            contributor_keywords, table_values, 
            list(self.contributor_keyword_experience_table.primary_key)[0].name, 
            action_map=contributor_keyword_action_map)

        contributor_keyword_insert = [{
            'augur_cntrb_id': contributor_keyword['canonical_id'],
            'keyword': contributor_keyword['keyword']
        } for contributor_keyword in contributor_keywords]

        self.bulk_insert(self.repo_language_info_table, insert=contributor_keyword_insert,
            database=self.toss_db)

        # Register this task as completed.
        #   This is a method of the worker class that is required to be called upon completion
        #   of any data collection model, this lets the broker know that this worker is ready
        #   for another task
        self.register_task_completion(task, None, 'contributor_keyword_experience')

