
#SPDX-License-Identifier: MIT
# import ast
import json
# import logging
# import os
# import sys
# import time
# import traceback
# import requests
# import copy
# from datetime import datetime
# from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
# from sqlalchemy.sql.expression import bindparam
from workers.worker_git_integration import WorkerGitInterfaceable

class GerritChangeRequestWorker(WorkerGitInterfaceable):
    """
    Worker that collects Change Request related data from the
    Gerrit API and stores it in our database.

    :param task: most recent task the broker added to the worker's queue
    :param config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = "gerrit_change_request_worker"

        # Define what this worker can be given and know how to interpret
        given = [['git_url']]
        models = ['change_requests']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['change_requests', 'change_requests_messages', 'change_request_reviewers', 'change_request_labels', 'change_request_commits', 'change_request_files']
        operations_tables = ['worker_history', 'worker_job']

        self.deep_collection = True
        self.platform_id = 25152 #Gerrit

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        ## This is metadata at the end of the table for GERRIT
        self.tool_source = 'Gerrit Change Request Worker'
        self.tool_version = '0.0.1'
        self.data_source = 'Gerrit API'

    def change_requests_model(self, entry_info, repo_id):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """

        self.logger.info("Beginning collection of Change Requests...\n")

        # Url to collect the change request json data from gerrit api
        #It is hard coded as the AGL api because we do not collect
        #project data for gerrit so the housekeeper cannot generate a valid job for the worker
        cr_url = (
            "https://gerrit.automotivelinux.org/gerrit/changes/?q=changes&no-limit"
        )

        # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
        # whether newly collected data needs to be added to table, or whether a record needs to be update
        cr_action_amp = {
            'insert': {
                'source': ['id'],
                'augur': ['change_src_id']
            },
            'update': {
                'source': ['status'],
                'augur': ['change_src_state']
            }
        }

        # hits the cr_url to collect the data and organizes it into json and returns it here
        # returns a dict with three keys ('insert', 'update', and 'all')
        # Method file: worker_git_integration.py
        source_crs = self.paginate_endpoint(
            cr_url, action_map=cr_action_amp, table=self.change_requests_table, platform="gerrit")

        self.logger.info(f"{len(source_crs['insert'])} change requests to insert")

        self.write_debug_data(source_crs, 'source_prs')

        # if no data was collected then register the task as completed
        if len(source_crs['all']) == 0:
            self.logger.info("There are no crs for this repository.\n")
            self.register_task_completion(self.task_info, self.repo_id, 'change_requests')
            return

        # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
        # This is organized as an array of dicts
        # The keys in each dict are the same name as the field names in the database tables
        crs_insert = [
            {
                'change_src_id': cr['id'],
                'change_project': cr['project'],
                'change_branch': cr['branch'],
                'change_id': cr['change_id'],
                'change_src_state': cr['status'],
                'change_created_at': cr['created'],
                'change_updated_at': cr['updated'],
                'change_submitted_at': cr['submitted'] if 'submitted' in cr.keys() else None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'Gerrit API'
            } for cr in source_crs['insert']
        ]

        # If there are crs to insert of update then call bulk_insert
        if len(source_crs['insert']) > 0 or len(source_crs['update']) > 0:

            # Call bulk_insert to insert and update all the needed data into the database
            # Method file: worker_git_integration.py
            pr_insert_result, pr_update_result = self.bulk_insert(
                self.change_requests_table,
                update=source_crs['update'], unique_columns=cr_action_amp['insert']['augur'],
                insert=crs_insert, update_columns=cr_action_amp['update']['augur']
            )

        # Create an array of chnage_ids
        # A change_id is needed to collect comments and reviewers so this array is passed to those models
        self.change_ids = []
        for cr in source_crs['insert']:
            self.change_ids.append(cr['id'])

        self.logger.info("Finished gathering change requests")

        self.change_request_files_model()
        # self.change_request_commits_model()

        # If there are change_ids then call models, to collect comments, labels, and reviewers
        if self.change_ids:
            self.change_request_comments_model()
            self.change_request_nested_data_model()

        self.register_task_completion(self.task_info, self.repo_id, 'change_requests')

    # Collect comments related to change requests
    def change_request_comments_model(self):

        self.logger.info("Starting change request message collection")

        self.logger.info(f"{len(self.change_ids)} change requests to collect messages for")

        # Loop through the change_ids to collect all the comments for each change request
        for index, change_id in enumerate(self.change_ids, start=1):

            self.logger.info(f"Message collection {index} of {len(self.change_ids)}")

            # Url to collect the change request comments json data from gerrit api
            #It is hard coded as the AGL api because we do not collect
            #project data for gerrit so the housekeeper cannot generate a valid job for the worker
            comments_url = (
                'https://gerrit.automotivelinux.org/gerrit/changes/{}/comments'.format(change_id)
            )

            # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
            # whether newly collected data needs to be added to table, or whether a record needs to be update
            comment_action_map = {
                'insert': {
                    'source': ['id'],
                    'augur': ['msg_id']
                }
            }

            # hits the comments_url to collect the data and organizes it into json and returns it here
            # returns a dict with three keys ('insert', 'update', and 'all')
            # Method file: worker_git_integration.py
            cr_comments = self.paginate_endpoint(
                comments_url, action_map=comment_action_map, table=self.change_requests_messages_table, platform="gerrit"
            )

            self.write_debug_data(cr_comments, 'cr_comments')

            # pr_comments['insert'] = self.text_clean(pr_comments['insert'], 'message')

            # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
            # This is organized as an array of dicts
            # The keys in each dict are the same name as the field names in the database tables
            cr_comments_insert = [
                {
                    'msg_id': comment['id'],
                    'change_src_id': change_id,
                    'change_project': change_id.split('~')[0],
                    'change_branch': change_id.split('~')[1],
                    'change_id': change_id.split('~')[2],
                    'msg_text': comment['message'],
                    'msg_updated': comment['updated'],
                    'author_id': comment['author']['_account_id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for comment in cr_comments['insert']
            ]

            # Insert data into database
            self.bulk_insert(self.change_requests_messages_table, insert=cr_comments_insert)

        self.logger.info("Finished change request message collection")

# ### If you could comment this so we knew what the fuck it did, that would be great. :)
    def change_request_nested_data_model(self):

            self.logger.info("Starting Labels Colletion")

            # Url to collect the change request labels json data from gerrit api
            #It is hard coded as the AGL api because we do not collect
            #project data for gerrit so the housekeeper cannot generate a valid job for the worker
            labels_url = (
                'https://gerrit.automotivelinux.org/gerrit/changes/?q=changes&o=LABELS'
            )

            # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
            # whether newly collected data needs to be added to table, or whether a record needs to be update
            labels_action_map = {
                'insert': {
                    'source': ['id', 'label'],
                    'augur': ['change_src_id', 'label']
                }
            }

            # hits the labels_url to collect the data and organizes it into json and returns it here
            # returns a dict with three keys ('insert', 'update', and 'all')
            # Method file: worker_git_integration.py
            cr_labels = self.paginate_endpoint(
                labels_url, action_map=labels_action_map, table=self.change_request_labels_table, platform="gerrit"
            )

            self.write_debug_data(cr_labels, 'cr_labels')

            # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
            # This is organized as an array of dicts
            # The keys in each dict are the same name as the field names in the database tables
            cr_labels_insert = [
                {
                    'change_src_id': label['id'],
                    'change_project': label['project'],
                    'change_branch': label['branch'],
                    'change_id': label['change_id'],
                    'label': label['label'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for label in cr_labels['insert']
            ]

            # Insert data into database
            self.bulk_insert(self.change_request_labels_table, insert=cr_labels_insert)

            self.logger.info("Finished Labels Connection")

            self.logger.info("Starting change request reviewers collection")

            # Loop through the change_ids to collect all the reviewers for each change request
            self.logger.info(f"{len(self.change_ids)} change requests to collect reviewers for")

            # Loop through the change_ids to collect all the comments for each change request
            for index, change_id in enumerate(self.change_ids, start=1):

                self.logger.info(f"Reviewers collection {index} of {len(self.change_ids)}")

                # Url to collect the change request reviewers json data from gerrit api
                #It is hard coded as the AGL api because we do not collect
                #project data for gerrit so the housekeeper cannot generate a valid job for the worker
                reviewers_url = (
                    'https://gerrit.automotivelinux.org/gerrit/changes/{}/reviewers'.format(change_id)
                )

                # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
                # whether newly collected data needs to be added to table, or whether a record needs to be update
                reviewer_action_map = {
                    'insert': {
                        'source': ['_account_id'],
                        'augur': ['reviewer_id']
                    }
                }

                # hits the reviewers_url to collect the data and organizes it into json and returns it here
                # returns a dict with three keys ('insert', 'update', and 'all')
                # Method file: worker_git_integration.py
                cr_reviewers = self.paginate_endpoint(
                    reviewers_url, action_map=reviewer_action_map, table=self.change_request_reviewers_table, platform="gerrit"
                )

                self.write_debug_data(cr_reviewers, 'cr_reviewers')

                # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
                # This is organized as an array of dicts
                # The keys in each dict are the same name as the field names in the database tables
                cr_reviewers_insert = [
                    {
                        'reviewer_id': int(reviewer['_account_id']),
                        'change_src_id': change_id,
                        'change_project': change_id.split('~')[0],
                        'change_branch': change_id.split('~')[1],
                        'change_id': change_id.split('~')[2],
                        'reviewer_name': reviewer['name'],
                        'reviewer_email': reviewer['email'] if 'email' in reviewer.keys() else None,
                        'reviewer_username': reviewer['username'],
                        'tool_source': self.tool_source,
                        'tool_version': self.tool_version,
                        'data_source': self.data_source
                    } for reviewer in cr_reviewers['insert']
                ]

                # Insert data into database
                self.bulk_insert(self.change_request_reviewers_table, insert=cr_reviewers_insert)


    def change_request_commits_model(self):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """

        self.logger.info("Beginning collection of Change Request Commits...\n")

        # Url to collect the change request json data from gerrit api
        #It is hard coded as the AGL api because we do not collect
        #project data for gerrit so the housekeeper cannot generate a valid job for the worker
        cr_commits_url = (
            "https://gerrit.automotivelinux.org/gerrit/changes/?q=status:abandoned&o=ALL_REVISIONS&o=ALL_COMMITS&o=ALL_FILES&no-limit"
        )

        # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
        # whether newly collected data needs to be added to table, or whether a record needs to be update
        cr_commits_action_map = {
            'insert': {
                'source': ['cmt_id'],
                'augur': ['cr_cmt_id']
            }
        }

        # hits the cr_url to collect the data and organizes it into json and returns it here
        # returns a dict with three keys ('insert', 'update', and 'all')
        # Method file: worker_git_integration.py
        source_cr_commits = self.paginate_endpoint(
            cr_commits_url, action_map=cr_commits_action_map, table=self.change_request_commits_table, platform="gerrit")

        self.logger.info(f"{len(source_cr_commits['insert'])} change request commits to insert")

        self.write_debug_data(source_cr_commits, 'source_prs')

        # if no data was collected then register the task as completed
        if len(source_cr_commits['all']) == 0:
            self.logger.info("There are no crs for this repository.\n")
            self.register_task_completion(self.task_info, self.repo_id, 'change_requests')
            return

        # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
        # This is organized as an array of dicts
        # The keys in each dict are the same name as the field names in the database tables
        cr_commits_insert = [
            {
                'change_src_id': cr_commit['id'],
                'change_project': cr_commit['project'],
                'change_branch': cr_commit['branch'],
                'change_id': cr_commit['change_id'],
                'cr_cmt_id': cr_commit['cmt_id'],
                'cr_cmt_timestamp': cr_commit['cmt_timestamp'],
                'cr_cmt_message': cr_commit['cmt_message'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'Gerrit API'
            } for cr_commit in source_cr_commits['insert']
        ]

        # If there are crs to insert of update then call bulk_insert
        if len(source_cr_commits['insert']) > 0 or len(source_cr_commits['update']) > 0:

            # Call bulk_insert to insert and update all the needed data into the database
            # Method file: worker_git_integration.py
            self.bulk_insert(self.change_request_commits_table, unique_columns=cr_commits_action_map['insert']['augur'], insert=cr_commits_insert)

        self.logger.info("Finished gathering change request commits")



    def change_request_files_model(self):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """

        self.logger.info("Beginning collection of Change Request Files...\n")

        cr_commit_query = s.sql.text("""
            SELECT change_src_id, cr_cmt_id FROM change_request_commits
        """)

        commit_data = json.loads(pd.read_sql(cr_commit_query, self.db, \
            params={}).to_json(orient="records"))

        # self.logger.info(f"Commit data: {commit_data[0]}")
        self.logger.info(f"{len(commit_data)} commits to collect files for")


        for index, commit in enumerate(commit_data, start=1):


            # Url to collect the change request json data from gerrit api
            #It is hard coded as the AGL api because we do not collect
            #project data for gerrit so the housekeeper cannot generate a valid job for the worker
            cr_files_url = (
                f"https://gerrit.automotivelinux.org/gerrit/changes/{commit['change_src_id']}/revisions/{commit['cr_cmt_id']}/files/"
            )

            # dict used in the worker_base.py, worker_git_integration.py, and worker_persistance.py files to determine
            # whether newly collected data needs to be added to table, or whether a record needs to be update
            cr_files_action_map = {
                'insert': {
                    'source': ['cmt_id', 'file_name'],
                    'augur': ['cr_cmt_id', 'cr_file_name']
                }
            }

        # hits the cr_url to collect the data and organizes it into json and returns it here
        # returns a dict with three keys ('insert', 'update', and 'all')
        # Method file: worker_git_integration.py
            source_cr_files = self.paginate_endpoint(
                cr_files_url, action_map=cr_files_action_map, table=self.change_request_files_table, platform="gerrit")

            self.logger.info(f"Source files: {source_cr_files['insert']}")



        self.logger.info(f"{len(source_cr_files['insert'])} change request commits to insert")
        
        self.logger.info(f"Example data: {source_cr_files['insert'][0]}")
        #
        # self.write_debug_data(source_cr_files, 'source_cr_files')
        #
        # # if no data was collected then register the task as completed
        # # if len(source_cr_files['all']) == 0:
        # #     self.logger.info("There are no crs for this repository.\n")
        # #     self.register_task_completion(self.task_info, self.repo_id, 'change_requests')
        # #     return
        #
        # # Takes all the data that needs inserting and extracts the fields that needs inserted in the database
        # # This is organized as an array of dicts
        # # The keys in each dict are the same name as the field names in the database tables
        # cr_files_insert = [
        #     {
        #         'change_src_id': cr_file['id'],
        #         'change_project': cr_file['project'],
        #         'change_branch': cr_file['branch'],
        #         'change_id': cr_file['change_id'],
        #         'cr_cmt_id': cr_file['cmt_id'],
        #         'cr_file_name': cr_file['file_name'],
        #         'cr_file_additions': cr_file['file_additions'],
        #         'cr_file_deletions': cr_file['file_deletions'],
        #         'tool_source': self.tool_source,
        #         'tool_version': self.tool_version,
        #         'data_source': 'Gerrit API'
        #     } for cr_file in source_cr_files['insert']
        # ]
        #
        # # If there are crs to insert of update then call bulk_insert
        # if len(source_cr_files['insert']) > 0 or len(source_cr_files['update']) > 0:
        #
        #     # Call bulk_insert to insert and update all the needed data into the database
        #     # Method file: worker_git_integration.py
        #     self.bulk_insert(self.change_request_files_table, unique_columns=cr_files_action_map['insert']['augur'], insert=cr_files_insert)
        #
        # self.logger.info("Finished gathering change request files")
