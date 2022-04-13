#SPDX-License-Identifier: MIT
from multiprocessing import Process, Queue
from urllib.parse import urlparse
from workers.worker_git_integration import WorkerGitInterfaceable
import pandas as pd
import sqlalchemy as s
import requests
import time
import logging
import traceback
import json
import traceback
import os
import psycopg2 #really only to catch type errors for database methods
import math
from datetime import datetime   
from workers.worker_base import Worker

### Revision History: 
# Source assignees were not getting made in version 1.0.0
# Version 1.1.0 fixes this issue. 

class GitHubWorker(WorkerGitInterfaceable):
    """ Worker that collects data from the Github API and stores it in our database
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = 'github_worker'

        given = [['github_url']]
        models = ['issues']

        data_tables = [
            'contributors', 'issues', 'issue_labels', 'message',
            'issue_message_ref', 'issue_events','issue_assignees','contributors_aliases',
            'pull_request_assignees', 'pull_request_events', 'pull_request_reviewers',
            'pull_request_meta', 'pull_request_repo'
        ]
        operations_tables = ['worker_history', 'worker_job']

        # These 3 are included in every tuple the worker inserts (data collection info)
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '1.1.0'
        self.data_source = 'GitHub API'

        # if we are finishing a previous task, pagination works differenty (deprecated)
        self.finishing_task = True

        self.platform_id = 25150  # GitHub
        self.process_count = 1
        self.deep_collection = True

        #Needs to be an attribute of the class for incremental database insert using paginate_endpoint
        self.pk_source_issues = []

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

    def _get_pk_source_issues(self):

        issues_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
            "/issues?per_page=100&state=all&page={}"
        )

        action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['gh_issue_id']
            },
            'update': {
                'source': ['comments', 'state'],
                'augur': ['comment_count', 'issue_state']
            }
        }

        def pk_source_issues_increment_insert(inc_source_issues,action_map):
            if len(inc_source_issues['all']) == 0:
                self.logger.info("There are no issues for this repository.\n")
                self.register_task_completion(self.task_info, self.repo_id, 'issues')
                return False

            def is_valid_pr_block(issue):
                return (
                    'pull_request' in issue and issue['pull_request']
                    and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
                )

            #This is sending empty data to enrich_cntrb_id, fix with check.
            #The problem happens when ['insert'] is empty but ['all'] is not.
            if len(inc_source_issues['insert']) > 0:
                inc_source_issues['insert'] = self.enrich_cntrb_id(
                    inc_source_issues['insert'], str('user.login'), action_map_additions={
                        'insert': {
                            'source': ['user.node_id'],
                            'augur': ['gh_node_id']
                        }
                    }, prefix='user.'
                )
            else:
                self.logger.info("Contributor enrichment is not needed, no inserts in action map.")

            issues_insert = [
                {
                    'repo_id': self.repo_id,
                    'reporter_id': issue['cntrb_id'],
                    'pull_request': (
                        issue['pull_request']['url'].split('/')[-1]
                        if is_valid_pr_block(issue) else None
                    ),
                    'pull_request_id': (
                        issue['pull_request']['url'].split('/')[-1]
                        if is_valid_pr_block(issue) else None
                    ),
                    'created_at': issue['created_at'],
                    'issue_title': str(issue['title']).encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                        issue['title']
                    ) else None,
                   # 'issue_body': issue['body'].replace('0x00', '____') if issue['body'] else None,
                    'issue_body': str(issue['body']).encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                        issue['body']
                    ) else None,
                    'comment_count': issue['comments'],
                    'updated_at': issue['updated_at'],
                    'closed_at': issue['closed_at'],
                    'repository_url': issue['repository_url'],
                    'issue_url': issue['url'],
                    'labels_url': issue['labels_url'],
                    'comments_url': issue['comments_url'],
                    'events_url': issue['events_url'],
                    'html_url': issue['html_url'],
                    'issue_state': issue['state'],
                    'issue_node_id': issue['node_id'],
                    'gh_issue_id': issue['id'],
                    'gh_issue_number': issue['number'],
                    'gh_user_id': issue['user']['id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for issue in inc_source_issues['insert']
            ]

            if len(inc_source_issues['insert']) > 0 or len(inc_source_issues['update']) > 0:
                issues_insert_result, issues_update_result = self.bulk_insert(
                    self.issues_table, update=inc_source_issues['update'],
                    unique_columns=action_map['insert']['augur'],
                    insert=issues_insert, update_columns=action_map['update']['augur']
                )

                source_data = inc_source_issues['insert'] + inc_source_issues['update']

            elif not self.deep_collection:
                self.logger.info(
                    "There are not issues to update, insert, or collect nested information for.\n"
                )
                #This might cause problems if staggered.
                #self.register_task_completion(entry_info, self.repo_id, 'issues')
                return

            if self.deep_collection:
                source_data = inc_source_issues['all']

            '''Commented these fields out because they are already defined in the action_map. '''

#            gh_merge_fields = ['id']
#            augur_merge_fields = ['gh_issue_id']

            self.pk_source_issues += self.enrich_data_primary_keys(
                source_data, self.issues_table, action_map['insert']['source'], action_map['insert']['augur']
            )

            return

        source_issues = self.paginate_endpoint(
            issues_url, action_map=action_map,
            table=self.issues_table, where_clause=self.issues_table.c.repo_id == self.repo_id,
            stagger=True,insertion_method=pk_source_issues_increment_insert
        )

        #Use the increment insert method in order to do the
        #remaining pages of the paginated endpoint that weren't inserted inside the paginate_endpoint method
        #empty data is checked for in the method so it's not needed outside of it.
        pk_source_issues_increment_insert(source_issues,action_map)

        pk_source_issues = self.pk_source_issues
        self.pk_source_issues = []

        return pk_source_issues

    def issues_model(self, entry_info, repo_id):
        """ Data collection function
        Query the GitHub API for issues
        """
        github_url = entry_info['given']['github_url']

        # Contributors are part of this model, and finding all for the repo saves us
        #   from having to add them as we discover committers in the issue process
        # self.query_github_contributors(entry_info, self.repo_id)

        pk_source_issues = self._get_pk_source_issues()
        if pk_source_issues:
            try:
                self.issue_comments_model(pk_source_issues)
                issue_events_all = self.issue_events_model(pk_source_issues)
                self.issue_nested_data_model(pk_source_issues, issue_events_all)
            except Exception as e:
                self.print_traceback("one of the issue models failed", e, False)
            finally:
                try:
                    issue_events_all = self.issue_events_model(pk_source_issues)
                except Exception as e:
                    self.print_traceback("issue events model failed", e, False)
                finally:
                    try:
                        self.issue_nested_data_model(pk_source_issues, issue_events_all)
                    except Exception as e:
                        self.print_traceback("issue nested model failed", e, False)


        # Register this task as completed
        self.register_task_completion(entry_info, self.repo_id, 'issues')

    def issue_comments_model(self, pk_source_issues):
        # https://api.github.com/repos/chaoss/augur/issues/comments
        comments_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
            "/issues/comments?per_page=100&page={}"
        )

        # Get contributors that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to
        #   check dupicates/needed column updates with

        ''' Consistent action maps require them to be consistent with what is passed to
            paginate_endpoint. '''
        comment_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['platform_msg_id']
            }
        }

        comment_ref_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['issue_msg_ref_src_comment_id']
            }
        }

        def issue_comments_insert(inc_issue_comments, comment_action_map):

            inc_issue_comments['insert'] = self.text_clean(inc_issue_comments['insert'], 'body')

            #This is sending empty data to enrich_cntrb_id, fix with check
            if len(inc_issue_comments['insert']) > 0:
                inc_issue_comments['insert'] = self.enrich_cntrb_id(
                    inc_issue_comments['insert'], str('user.login'), action_map_additions={
                        'insert': {
                            'source': ['user.node_id'],
                            'augur': ['gh_node_id']
                        }
                    }, prefix='user.'
                )
            else:
                self.logger.info("Contributor enrichment is not needed, no inserts in action map.")

            issue_comments_insert = [
                {
                    'pltfrm_id': self.platform_id,
                    'msg_text': comment['body'].encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                        comment['body']
                    ) else ' ',
                    'msg_timestamp': comment['created_at'] if (
                        comment['created_at']
                    ) else is_nan(comment['created_at']),
                    'cntrb_id': comment['cntrb_id'] if (
                        comment['cntrb_id']
                    ) else is_na(comment['cntrb_id']),
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'platform_msg_id': int(comment['id']),
                    'platform_node_id': comment['node_id'],
                    'repo_id': self.repo_id 
                } for comment in inc_issue_comments['insert']
            ]
            try:
                # self.bulk_insert(self.message_table, insert=issue_comments_insert,
                #     unique_columns=comment_action_map['insert']['augur'])
                # Using the action map resulted consistently in a duplicate key error
                # Which really should not be possible ... ?? Trying hard coding the map.
                self.bulk_insert(self.message_table, insert=issue_comments_insert,
                    unique_columns=comment_action_map['insert']['augur'])
            except Exception as e:
                self.print_traceback("bulk insert of issue comments", e, False)

            """ ISSUE MESSAGE REF TABLE """
            try:
                c_pk_source_comments = self.enrich_data_primary_keys(
                    inc_issue_comments['insert'], self.message_table,
                    comment_action_map['insert']['source'], comment_action_map['insert']['augur']
                )
            except Exception as e:
                self.print_traceback("enrich data primary keys for getting msg_id for issue comments", e, False)

            self.logger.info(f"log of the length of c_pk_source_comments {len(c_pk_source_comments)}.")

            try:
                # source data, tables, gh_merge fields, augur merge fields are the parameters for enrich_data_primary_keys method
                # This one does not make a lot of sense to SPG on 9/15/2021. Why is the issues table getting updated here? we have
                # Comment source data, the issues table, and issue table merge info. Not following this at all. TODO

                both_pk_source_comments = self.enrich_data_primary_keys(
                    c_pk_source_comments, self.issues_table, ['issue_url'], ['issue_url']
                )
            except Exception as e:
                self.print_traceback("enrich data primary keys for getting issue_id for issue comments", e, False)

            issue_message_ref_insert = [
                {
                    'issue_id': comment['issue_id'],
                    'msg_id': comment['msg_id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'issue_msg_ref_src_comment_id': int(comment['id']),
                    'issue_msg_ref_src_node_id': comment['node_id'],
                    'repo_id': self.repo_id
                } for comment in both_pk_source_comments
            ]
            try:
                self.logger.debug(f"inserting into {self.issue_message_ref_table}.")
                self.bulk_insert(
                    self.issue_message_ref_table, insert=issue_message_ref_insert,
                    unique_columns=comment_ref_action_map['insert']['augur']
                )
            except Exception as e:
                self.print_traceback("bulk insert on issue_msg_ref_table", e, False)

        # list to hold contributors needing insertion or update
        try:
            issue_comments = self.paginate_endpoint(
                comments_url, action_map=comment_action_map, table=self.message_table,
                where_clause=self.message_table.c.msg_id.in_(
                    [
                        msg_row[0] for msg_row in self.db.execute(
                            s.sql.select(
                                [self.issue_message_ref_table.c.msg_id]
                            ).where(
                                self.issue_message_ref_table.c.issue_id.in_(
                                    set(pd.DataFrame(pk_source_issues)['issue_id'])
                                )
                            )
                        ).fetchall()
                    ]
                ),
                stagger=True,
                insertion_method=issue_comments_insert
            )

            issue_comments_insert(issue_comments,comment_action_map)
            self.logger.info(f"comments inserted for repo_id: {self.repo_id}")
            #self.logger.debug(f"Contents of issue_comments: {issue_comments}.")
            return

        except Exception as e:
            self.print_traceback("paginate endpoint for issue comments", e, False)

    def issue_events_model(self, pk_source_issues):

        # Get events ready in case the issue is closed and we need to insert the closer's id
        events_url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}"
            "/issues/events?per_page=100&page={}"
        )

        # Get events that we already have stored
        #   Set pseudo key (something other than PK) to
        #   check dupicates with
        event_action_map = {
            'insert': {
                'source': ['url'],
                'augur': ['node_url']
            }
        }

        self.logger.info(pk_source_issues[0])
        self.logger.info(pd.DataFrame(pk_source_issues).columns)
        self.logger.info(pd.DataFrame(pk_source_issues))
        #list to hold contributors needing insertion or update
        issue_events = self.new_paginate_endpoint(
            events_url, table=self.issue_events_table, action_map=event_action_map,
            where_clause=self.issue_events_table.c.issue_id.in_(
                set(pd.DataFrame(pk_source_issues)['issue_id'])
            )
        )

        '''This works, but its a little confusing. The keys mapped here are the identity keys for the
        issues table, which are used to let us know if we need to insert them here. '''

        pk_issue_events = self.enrich_data_primary_keys(
            issue_events['insert'], self.issues_table, ['issue.id'], ['gh_issue_id']
        )

        if len(pk_issue_events):
            pk_issue_events = pd.DataFrame(pk_issue_events)[
                ['id', 'issue_id', 'node_id', 'url', 'actor', 'created_at', 'event', 'commit_id']
            ].to_dict(orient='records')

        #This is sending empty data to enrich_cntrb_id, fix with check
        if len(pk_issue_events) > 0:
            pk_issue_events = self.enrich_cntrb_id(
                pk_issue_events, str('actor.login'), action_map_additions={
                    'insert': {
                        'source': ['actor.node_id'],
                        'augur': ['gh_node_id']
                    }
                }, prefix='actor.'
            )
        else:
            self.logger.info("Contributor enrichment is not needed, no inserts in action map.")

        for index, issue in enumerate(pk_issue_events):

            if 'cntrb_id' not in issue:
                self.logger.debug(f"Exception registered. Dict has null cntrb_id: {issue}")

        issue_events_insert = [
            {
                'issue_event_src_id': int(event['id']),
                'issue_id': int(event['issue_id']),
                'node_id': event['node_id'],
                'node_url': event['url'],
                'cntrb_id': int(event['cntrb_id']),
                'created_at': event['created_at'] if (
                    event['created_at']
                    ) else None,
                'action': event['event'],
                'action_commit_hash': event['commit_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'repo_id': self.repo_id,
                'platform_id': self.platform_id
            } for event in pk_issue_events if event['actor'] is not None
        ]

        self.bulk_insert(
            self.issue_events_table, insert=issue_events_insert,
            unique_columns=event_action_map['insert']['augur']
        )

        return issue_events['all']

    def issue_nested_data_model(self, pk_source_issues, issue_events_all):

        self.logger.info("In the issue nested model.")

        closed_issue_updates = []

        skip_closed_issue_update = False
        if len(issue_events_all):
            self.logger.info("entering events df.")
            events_df = pd.DataFrame(
                self._get_data_set_columns(
                    issue_events_all, [
                        'event', 'issue.number', 'actor.login', 'actor.node_id', 'actor'
                    ]
                )
            )
            events_df = events_df.loc[events_df.event == 'closed']

            self.logger.info(f"Events dataframe is: {events_df}.")

            self.logger.info("Entering the processing of the events dataframe.")


            if len(events_df):
                events_df = pd.DataFrame(
                    self.enrich_cntrb_id(
                        events_df.to_dict(orient='records'), str('actor.login'), action_map_additions={
                            'insert': {
                                'source': ['actor.node_id'],
                                'augur': ['gh_node_id']
                            }
                        }, prefix='actor.'
                    )
                )
                if not len(events_df):  # no cntrb ids were available
                    self.logger.info("Skipping issue update: No cntrb id's available.")
                    #skip_closed_issue_update = True
            else:
                self.logger.info("Skipping issue update: Second else.")
                #skip_closed_issue_update = True
        else:
            self.logger.info("Skipping issue update: Second else.")
            #kip_closed_issue_update = True

        self.logger.info("Entering Assignee's.")

        # assignees_all = []
        # labels_all = []

        def is_nan(value):
            return type(value) == float and math.isnan(value)

        for issue in pk_source_issues:

            self.logger.debug(f"on issue: there are {len(pk_source_issues)} issues total. Editing assignee next.")
            try: 
                # Issue Assignees
                ### 12/20/2021: Trying `is_na` instead of `is_nan`
                source_assignees = [
                    assignee for assignee in issue['assignees'] if assignee
                    and not is_nan(assignee)
                ]
                if (
                    issue['assignee'] not in source_assignees and issue['assignee']
                    and not is_nan(issue['assignee'])
                ):
                    source_assignees.append(issue['assignee'])
                    # assignees_all += source_assignees

                # self.logger.info(f"Total of assignee's is: {assignees_all}. Labels are next.")
            except Exception as e:
                self.print_traceback("when creating source assignees list", e, False)
                
            finally: 

                try: 
                    # Issue Labels
                    # labels_all += issue['labels']

                    # If the issue is closed, then we search for the closing event and store the user's id
                    if 'closed_at' in issue and not skip_closed_issue_update:

                        try:
                            closed_event = events_df.loc[
                                events_df['issue.number'] == issue['number']
                            ].iloc[-1]

                            self.logger.info(f"In the closed events section.")

                        except IndexError:
                            self.logger.info(
                                "Warning! We do not have the closing event of this issue stored. "
                                f"Pk: {issue['issue_id']}. exception registered."
                            )
                            continue
                        except Exception as e:
                            self.logger.info(f"exception is {e} and not an IndexError.. exception registered")
                            continue
                        ### Updated this on 9/17/2021 due to error:
                        '''
                                2021-09-17 15:55:10,377,377ms [PID: 2078591] workers.github_worker.57631 [INFO] Warning! Error bulk updating data: (psycopg2.ProgrammingError) can't adapt type 'numpy.int64'
                                [SQL: UPDATE issues SET cntrb_id=%(cntrb_id)s, closed_at=%(closed_at)s, issue_state=%(issue_state)s WHERE issues.issue_id = %(b_issue_id)s]
                                [parameters: ({'cntrb_id': 277403, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345071}, {'cntrb_id': 277403, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345072}, {'cntrb_id': 277403, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345073}, {'cntrb_id': 277403, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345074}, {'cntrb_id': 277403, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345075}, {'cntrb_id': 277762, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345077}, {'cntrb_id': 277762, 'closed_at': 'closed_at', 'issue_state': 'issue_state', 'b_issue_id': 345078})]
                                (Background on this error at: http://sqlalche.me/e/13/f405)
                        '''

                        ## Cast the numerics as ints, as prior update on 9/17 did not eliminate the error noted above. SPG, 9/18/2021
                        self.logger.info(f"issue closed_at is: {issue['closed_at']}")
                        closed_issue_updates.append({
                            'b_issue_id': int(issue['issue_id']),
                            'cntrb_id': int(closed_event['cntrb_id']),
                            'issue_state': issue['state'],
                            'closed_at': issue['closed_at'] if not pd.isnull(issue['closed_at']) else None,
                        })

                        self.logger.info(f"Current closed issue count is {len(closed_issue_updates)}.")

                    # Closed issues, update with closer id
                    ''' TODO: Right here I am not sure if the update columns are right, and will catch the state changes. '''
                except Exception as e:
                    self.print_traceback("issue assignees", e, True)

            try:

                self.bulk_insert(
                    self.issues_table, update=closed_issue_updates, unique_columns=['issue_id'],
                    update_columns=['cntrb_id', 'issue_state', 'closed_at']
                )
            except Exception as e:
                self.print_traceback("bulk insert on issues table", e, False)

            ''' Action maps are used to determine uniqueness based on the natural key at the source. '''

            self.logger.info("Entering assignee insertion.")

            # Issue assignees insertion
            assignee_action_map = {
                'insert': {
                    'source': ['id'],
                    'augur': ['issue_assignee_src_id']
                }
            }

            table_values_issue_assignees = self.db.execute(
                s.sql.select(self.get_relevant_columns(self.issue_assignees_table,assignee_action_map))
            ).fetchall()

            self.logger.info(f"Issue assignee retrieved total: {len(table_values_issue_assignees)}.")

            self.logger.info(f"source_assigneess before organize_needed_data: {source_assignees}")
            source_assignees_insert, _ = self.organize_needed_data(
                source_assignees, table_values=table_values_issue_assignees,
                action_map=assignee_action_map
            )
            self.logger.info(f"source_assignees_insert after organize_needed_data: {source_assignees_insert}")
            if len(source_assignees_insert) > 0:
                source_assignees_insert = self.enrich_cntrb_id(
                    source_assignees_insert, str('login'), action_map_additions={
                        'insert': {
                            'source': ['node_id'],
                            'augur': ['gh_node_id']
                        }
                    }
                )
            else:
                self.logger.info("Contributor enrichment is not needed, no inserts in action map.")

            assignees_insert = [
                {
                    'issue_id': issue['issue_id'],
                    'cntrb_id': assignee['cntrb_id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'issue_assignee_src_id': int(assignee['id']),
                    'issue_assignee_src_node': assignee['node_id'],
                    'repo_id': self.repo_id 
                } for assignee in source_assignees_insert
            ]
            try:
                self.bulk_insert(
                    self.issue_assignees_table, insert=assignees_insert,
                    unique_columns=['issue_id', 'issue_assignee_src_id']
                )
            except Exception as e:
                self.logger.info(f"assignees failed on {e}. exception registerred.")

            # Issue labels insertion

                ## Probably need to do the map like PRs again.
                # 'insert': {
                #     'source': ['pull_request_id', 'id'],
                #     'augur': ['pull_request_id', 'pr_src_id']
                # }
            ''' Action maps are used to determine uniqueness based on the natural key at the source. '''

            label_action_map = {
                'insert': {
                    'source': ['id'],
                    'augur': ['label_src_id']
                }
            }

            try:
                table_values_issue_labels = self.db.execute(
                    s.sql.select(self.get_relevant_columns(self.issue_labels_table,label_action_map))
                ).fetchall()
            except Exception as e:
                self.logger.info(f"Exception in label insert for PRs: {e}.. exception registerred")


            # self.logger.info(f"Exception registered. labels_all[0]: {labels_all[0]}")
            self.logger.info(f"issue['labels'] before organize_needed_data: {issue['labels']}")

            source_labels_insert, _ = self.organize_needed_data(
                issue['labels'], table_values=table_values_issue_labels,
                action_map=label_action_map
            )
            self.logger.info(f"source_labels_insert after organize_needed_data: {source_labels_insert}")
            labels_insert = [
                {
                    'issue_id': issue['issue_id'],
                    'label_text': label['name'],
                    'label_description': label['description'] if 'description' in label else None,
                    'label_color': label['color'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'label_src_id': int(label['id']),
                    'label_src_node_id': label['node_id'],
                    'repo_id': self.repo_id 
                } for label in source_labels_insert
            ]

            #Trying to fix an error with creating bigInts using pandas
            try:
                self.bulk_insert(
                    self.issue_labels_table, insert=labels_insert,
                    unique_columns=['label_src_id']
                )
            except psycopg2.errors.InvalidTextRepresentation as e:
                #If there was an error constructing a type try to redo the insert with a conversion.
                self.logger.warning(f"Type error when attempting to insert data in issue_nested_data_model with the github worker. Trying again with type conversion on. ERROR: {e}. exception registerred \n")
                self.bulk_insert(
                    self.issue_labels_table, insert=labels_insert,
                    unique_columns=['label_src_id'],
                    convert_float_int=True
                )
