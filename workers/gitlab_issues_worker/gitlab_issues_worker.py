#SPDX-License-Identifier: MIT
import logging, os, sys, time, requests, json
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from workers.worker_base import Worker


class GitLabIssuesWorker(Worker):
    def __init__(self, config={}):
    
        worker_type = "gitlab_issues_worker"
        given = [['git_url']]
        models = ['gitlab_issues']
        data_tables = ['contributors', 'issues', 'issue_labels', 'message', 'repo',
            'issue_message_ref', 'issue_events','issue_assignees','contributors_aliases',
            'pull_request_assignees', 'pull_request_events', 'pull_request_reviewers', 'pull_request_meta',
            'pull_request_repo']
        operations_tables = ['worker_history', 'worker_job']
        super().__init__(worker_type, config, given, models, data_tables, operations_tables, platform='gitlab')
        gitlab_api_key = self.augur_config.get_value("Database", "gitlab_api_key")
        self.config.update({
                           "gitlab_api_key": gitlab_api_key
                           })
        self.headers = {"PRIVATE-TOKEN" : self.config['gitlab_api_key']}


        # Define data collection info
        self.tool_source = 'Gitlab API Worker'
        self.tool_version = '0.0.0'
        self.data_source = 'GitLab API'
        self.platform_id = 25150


    def gitlab_issues_model(self, task, repo_id):

        # Collection and insertion of data happens here

        # Collecting issue info from Gitlab API
        self.issue_id_inc = self.get_max_id('issues', 'issue_id')
        self.msg_id_inc = self.get_max_id('message', 'msg_id')
        self.logger.info('Beginning the process of GitLab Issue Collection...'.format(str(os.getpid())))
        gitlab_base = 'https://gitlab.com/api/v4'
        # adding the labels attribute in the query params to avoid additional API calls
        intermediate_url = '{}/projects/{}/issues?per_page=100&state=opened&with_labels_details=True&'.format(gitlab_base, repo_id)
        gitlab_issues_url = intermediate_url + "page={}"
        
        table = 'issues'
        table_pkey = 'issue_id'
        update_col_map = {'issue_state': 'state'}
        duplicate_col_map = {'gh_issue_id': 'id'}

        #list to hold issues needing insertion
        issues = self.paginate(gitlab_issues_url, duplicate_col_map, update_col_map, table, table_pkey, 
            'WHERE repo_id = {}'.format(repo_id), platform="gitlab")
        
        self.logger.info(issues)
        self.logger.info("Count of issues needing update or insertion: " + str(len(issues)) + "\n")
        for issue_dict in issues:
            self.logger.info("Begin analyzing the issue with title: " + issue_dict['title'] + "\n")
            pr_id = None
            if "pull_request" in issue_dict:
                self.logger.info("This is an MR\n")
                # Right now we are just storing our issue id as the MR id if it is one
                pr_id = self.issue_id_inc
            else:
                self.logger.info("Issue is not an MR\n")

            # Insert data into models
            issue = {
                    "repo_id": issue_dict['project_id'],
                    "reporter_id": self.find_id_from_login(issue_dict['author']['username'], platform='gitlab'),
                    "pull_request": pr_id,
                    "pull_request_id": pr_id,
                    "created_at": issue_dict['created_at'],
                    "issue_title": issue_dict['title'],
                    "issue_body": issue_dict['description'] if 'description' in issue_dict else None,
                    "comment_count": issue_dict['user_notes_count'],
                    "updated_at": issue_dict['updated_at'],
                    "closed_at": issue_dict['closed_at'],
                    "repository_url": issue_dict['_links']['project'],
                    "issue_url": issue_dict['_links']['self'],
                    "labels_url": None,
                    "comments_url": issue_dict['_links']['notes'],
                    "events_url": None,
                    "html_url": issue_dict['_links']['self'],
                    "issue_state": issue_dict['state'],
                    "issue_node_id": None,
                    "gh_issue_id": issue_dict['id'],
                    "gh_issue_number": issue_dict['iid'],
                    "gh_user_id": issue_dict['author']['id'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
            }
        # Commit insertion to the issues table
            if issue_dict['flag'] == 'need_update':
                self.logger.info("UPDATE FLAG")
                result = self.db.execute(self.issues_table.update().where(
                    self.issues_table.c.gh_issue_id==issue_dict['id']).values(issue))
                self.logger.info("Updated tuple in the issues table with existing gh_issue_id: {}".format(
                    issue_dict['id']))
                self.issue_id_inc = issue_dict['pkey']
            elif issue_dict['flag'] == 'need_insertion':
                self.logger.info("INSERT FLAG")
                try:
                    result = self.db.execute(self.issues_table.insert().values(issue))
                    self.logger.info("Primary key inserted into the issues table: " + str(result.inserted_primary_key))
                    self.results_counter += 1
                    self.issue_id_inc = int(result.inserted_primary_key[0])
                    self.logger.info("Inserted issue with our issue_id being: {}".format(self.issue_id_inc) + 
                        " and title of: {} and gh_issue_num of: {}\n".format(issue_dict['title'], issue_dict['iid']))
                except Exception as e:
                    self.logger.info("When inserting an issue, ran into the following error: {}\n".format(e))
                    self.logger.info(issue)
                # continue
        
        # issue_assigness
            self.logger.info("assignees", issue_dict['assignees'])
            collected_assignees = issue_dict['assignees']
            if issue_dict['assignee'] not in collected_assignees:
                collected_assignees.append(issue_dict['assignee'])
            if collected_assignees[0] is not None:
                self.logger.info("Count of assignees to insert for this issue: " + str(len(collected_assignees)) + "\n")
                for assignee_dict in collected_assignees:
                    if type(assignee_dict) != dict:
                        continue
                    assignee = {
                        "issue_id": self.issue_id_inc,
                        "cntrb_id": self.find_id_from_login(assignee_dict['username'], platform='gitlab'),
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source,
                        "issue_assignee_src_id": assignee_dict['id'],
                        "issue_assignee_src_node": None
                    }
                    self.logger.info("assignee info", assignee)
                    # Commit insertion to the assignee table
                    result = self.db.execute(self.issue_assignees_table.insert().values(assignee))
                    self.logger.info("Primary key inserted to the issues_assignees table: " + str(result.inserted_primary_key))
                    self.results_counter += 1

                    self.logger.info("Inserted assignee for issue id: " + str(self.issue_id_inc) + 
                        " with login/cntrb_id: " + assignee_dict['username'] + " " + str(assignee['cntrb_id']) + "\n")
            else:
                self.logger.info("Issue does not have any assignees\n")

            # Insert the issue labels to the issue_labels table
            for label_dict in issue_dict['labels']:
                desc = None
                if 'description' in label_dict:
                    desc = label_dict['description']
                label = {
                    "issue_id": self.issue_id_inc,
                    "label_text": label_dict["name"],
                    "label_description": desc,
                    "label_color": label_dict['color'],
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "label_src_id": label_dict['id'],
                    "label_src_node_id": None
                }

                result = self.db.execute(self.issue_labels_table.insert().values(label))
                self.logger.info("Primary key inserted into the issue_labels table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                self.logger.info("Inserted issue label with text: " + label_dict['name'] + "\n")

            # issue notes (comments are called 'notes' in Gitlab's language)
            notes_endpoint = gitlab_base + "/projects/{}/issues/{}/notes?per_page=100".format(10525408, issue_dict['iid'])
            notes_paginated_url = notes_endpoint + "&page={}"
            # Get contributors that we already have stored
            #   Set our duplicate and update column map keys (something other than PK) to 
            #   check dupicates/needed column updates with
            table = 'message'
            table_pkey = 'msg_id'
            update_col_map = None #updates for comments not necessary
            duplicate_col_map = {'msg_id': 'id'}

            issue_comments = self.paginate(notes_paginated_url, duplicate_col_map, update_col_map, table, table_pkey, 
                where_clause="WHERE msg_id IN (SELECT msg_id FROM issue_message_ref WHERE issue_id = {})".format(
                    self.issue_id_inc), platform='gitlab')
            
            self.logger.info("Number of comments needing insertion: {}\n".format(len(issue_comments)))

            for comment in issue_comments:
                try:
                    commenter_cntrb_id = self.find_id_from_login(comment['author']['username'])
                except:
                    commenter_cntrb_id = None
                issue_comment = {
                    "pltfrm_id": self.platform_id,
                    "msg_text": comment['body'],
                    "msg_timestamp": comment['created_at'],
                    "cntrb_id": commenter_cntrb_id,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }
                try:
                    result = self.db.execute(self.message_table.insert().values(issue_comment))
                    self.logger.info("Primary key inserted into the message table: {}".format(result.inserted_primary_key))
                    self.results_counter += 1
                    self.msg_id_inc = int(result.inserted_primary_key[0])

                    self.logger.info("Inserted issue comment with id: {}\n".format(self.msg_id_inc))
                except Exception as e:
                    self.logger.info("Worker ran into error when inserting a message, likely had invalid characters. error: {}".format(e))

                ### ISSUE MESSAGE REF TABLE ###

                issue_message_ref = {
                    "issue_id": self.issue_id_inc,
                    "msg_id": self.msg_id_inc,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source,
                    "issue_msg_ref_src_comment_id": comment['id'],
                    "issue_msg_ref_src_node_id": None
                }

                result = self.db.execute(self.issue_message_ref_table.insert().values(issue_message_ref))
                self.logger.info("Primary key inserted into the issue_message_ref table: {}".format(result.inserted_primary_key))
                self.results_counter += 1
            
            # issue events

            issue_events_url = gitlab_base + '/projects/{}/events?target_type=issue&per_page=100'.format(10525408)
            issue_events_url += "&page={}"

            table = 'issue_events'
            table_pkey = 'event_id'
            update_col_map = None # updates for issue events not applicable here
            duplicate_col_map = {'event_id': 'target_id'}

            issue_events = self.paginate(issue_events_url, duplicate_col_map, update_col_map, table, table_pkey, 
                                           where_clause="", platform='gitlab')

            for event in issue_events:
                issue_event = {
                    "issue_event_src_id": event['target_id'],
                    "issue_id": self.issue_id_inc,
                    "node_id": None,
                    "node_url": None,
                    "cntrb_id": self.find_id_from_login(event['author_username'], platform='gitlab'),
                    "created_at": event['created_at'],
                    "action": event["action_name"],
                    "action_commit_hash": None,
                    "tool_source": self.tool_source,
                    "tool_version": self.tool_version,
                    "data_source": self.data_source
                }

                result = self.db.execute(self.issue_events_table.insert().values(issue_event))
                self.logger.info("Primary key inserted into the issue_events table: " + str(result.inserted_primary_key))
                self.results_counter += 1

                self.logger.info("Inserted issue event: " + event['action_name'] + " for issue id: {}\n".format(self.issue_id_inc))



        self.register_task_completion(task, repo_id, 'gitlab_issues')