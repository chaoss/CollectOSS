#SPDX-License-Identifier: MIT
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import pandas as pd
import sqlalchemy as s
import requests, time, logging, json, os
from datetime import datetime
from workers.worker_base import Worker

class GitHubWorker(Worker):
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

        data_tables = ['contributors', 'issues', 'issue_labels', 'message',
            'issue_message_ref', 'issue_events','issue_assignees','contributors_aliases',
            'pull_request_assignees', 'pull_request_events', 'pull_request_reviewers', 'pull_request_meta',
            'pull_request_repo']
        operations_tables = ['worker_history', 'worker_job']

        # These 3 are included in every tuple the worker inserts (data collection info)
        self.tool_source = 'GitHub API Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'GitHub API'

        self.finishing_task = True # if we are finishing a previous task, pagination works differenty
        self.platform_id = 25150 # GitHub

        self.process_count = 1

        self.deep_collection = True

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

    def issues_model(self, entry_info, repo_id):
        """ Data collection function
        Query the GitHub API for issues
        """

        github_url = entry_info['given']['github_url']

        # Contributors are part of this model, and finding all for the repo saves us 
        #   from having to add them as we discover committers in the issue process
        self.query_github_contributors(entry_info, repo_id)

        owner, repo = self.get_owner_repo(github_url)

        issues_url = f"https://api.github.com/repos/{owner}/{repo}" + \
            "/issues?per_page=100&state=all&page={}"
        
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

        source_issues = self.paginate_endpoint(issues_url, action_map=action_map, 
            table=self.issues_table, where_clause=self.issues_table.c.repo_id == repo_id)

        if len(source_issues['all']) == 0:
            self.logger.info("There are no issues for this repository.\n")
            self.register_task_completion(entry_info, repo_id, 'issues')
            return

        issues_insert = [
            {
                'repo_id': repo_id,
                'reporter_id': self.find_id_from_login(issue['user']['login']),
                'pull_request': issue['pull_request']['url'].split('/')[-1] if 'pull_request' in issue else None,
                'pull_request_id': issue['pull_request']['url'].split('/')[-1] if 'pull_request' in issue else None,
                'created_at': issue['created_at'],
                'issue_title': issue['title'],
                'issue_body': issue['body'].replace('0x00', '____') if issue['body'] else None,
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
            } for issue in source_issues['insert']
        ]

        if len(source_issues['insert']) > 0 or len(source_issues['update']) > 0:

            issues_insert_result, issues_update_result = self.bulk_insert(self.issues_table, 
                update=source_issues['update'], unique_columns=action_map['insert']['augur'], 
                insert=issues_insert, update_columns=action_map['update']['augur'])

            source_data = source_issues['insert'] + source_issues['update']

        elif not self.deep_collection:
            self.logger.info("There are not issues to update, insert, or collect nested "
                "information for.\n")
            self.register_task_completion(entry_info, repo_id, 'issues')
            return

        if self.deep_collection:
            source_data = source_issues['all']

        # Merge source data to inserted data to have access to inserted primary keys

        gh_merge_fields = ['id']
        augur_merge_fields = ['gh_issue_id']

        pk_source_issues = self.enrich_data_primary_keys(source_data, self.issues_table, 
            gh_merge_fields, augur_merge_fields)

        # Messages/comments

        comments_url = f"https://api.github.com/repos/{owner}/{repo}" + \
            "/issues/comments?per_page=100&page={}"

        # Get contributors that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        comment_action_map = {
            'insert': {
                'source': ['created_at', 'body'],
                'augur': ['msg_timestamp', 'msg_text']
            }
        }

        # list to hold contributors needing insertion or update
        issue_comments = self.paginate_endpoint(comments_url, 
            action_map=comment_action_map, table=self.message_table, 
            where_clause=self.message_table.c.msg_id.in_(
                    [msg_row[0] for msg_row in self.db.execute(s.sql.select(
                        [self.issue_message_ref_table.c.msg_id]).where(
                        self.issue_message_ref_table.c.issue_id.in_(
                            set(pd.DataFrame(pk_source_issues)['issue_id'])
                        ))).fetchall()]
                ))

        issue_comments_insert = [
            {
                'pltfrm_id': self.platform_id,
                'msg_text': comment['body'],
                'msg_timestamp': comment['created_at'],
                'cntrb_id': self.find_id_from_login(comment['user']['login']),
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for comment in issue_comments['insert']
        ]

        self.bulk_insert(self.message_table, insert=issue_comments_insert, 
            unique_columns=comment_action_map['insert']['augur'])
            
        """ ISSUE MESSAGE REF TABLE """

        c_pk_source_comments = self.enrich_data_primary_keys(issue_comments['insert'], 
            self.message_table, comment_action_map['insert']['source'], comment_action_map['insert']['augur'])
        both_pk_source_comments = self.enrich_data_primary_keys(c_pk_source_comments, 
            self.issues_table, ['issue_url'], ['issue_url'])

        issue_message_ref_insert = [
            {
                'issue_id': comment['issue_id'],
                'msg_id': comment['msg_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source,
                'issue_msg_ref_src_comment_id': comment['id'],
                'issue_msg_ref_src_node_id': comment['node_id']
            } for comment in both_pk_source_comments
        ]

        self.bulk_insert(self.issue_message_ref_table, insert=issue_message_ref_insert, 
            unique_columns=['issue_msg_ref_src_comment_id'])

        # Issue Events          
    
        # Get events ready in case the issue is closed and we need to insert the closer's id
        events_url = f"https://api.github.com/repos/{owner}/{repo}" + \
            "/issues/events?per_page=100&page={}"

        # Get events that we already have stored
        #   Set pseudo key (something other than PK) to 
        #   check dupicates with
        event_action_map = {
            'insert': {
                'source': ['url'],
                'augur': ['node_url']
            }
        }

        #list to hold contributors needing insertion or update
        issue_events = self.paginate_endpoint(events_url, table=self.issue_events_table,
            action_map=event_action_map, where_clause=self.issue_events_table.c.issue_id.in_(
                    set(pd.DataFrame(pk_source_issues)['issue_id'])
                ))

        pk_issue_events = self.enrich_data_primary_keys(issue_events['insert'], 
            self.issues_table, ['issue.id'], ['gh_issue_id'])

        issue_events_insert = [
            {
                'issue_event_src_id': event['id'],
                'issue_id': event['issue_id'],
                'node_id': event['node_id'],
                'node_url': event['url'],
                'cntrb_id': self.find_id_from_login(event['actor']['login']),
                'created_at': event['created_at'],
                'action': event['event'],
                'action_commit_hash': event['commit_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for event in pk_issue_events if event['actor'] is not None
        ]

        self.bulk_insert(self.issue_events_table, insert=issue_events_insert, 
            unique_columns=event_action_map['insert']['augur'])

        closed_issue_updates = []
        assignees_insert = []
        labels_insert = []

        assignee_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['issue_assignee_src_id']
            }
        }

        label_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['label_src_id']
            }
        }

        # Issue nested info table insertions

        for issue in pk_source_issues:

            # Issue Assignees

            source_assignees = issue['assignees']
            if issue['assignee'] not in source_assignees and issue['assignee'] is not None:
                source_assignees.append(issue['assignee'])
            
            cols_to_query = self.get_relevant_columns(self.issue_assignees_table, assignee_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.issue_assignees_table.c.issue_id == issue['issue_id'])).fetchall()

            source_assignees_insert, _ = self.organize_needed_data(source_assignees, table_values, 
                list(self.issue_assignees_table.primary_key)[0].name, action_map=assignee_action_map)

            assignees_insert += [
                {
                    'issue_id': issue['issue_id'],
                    'cntrb_id': self.find_id_from_login(assignee['login']),
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'issue_assignee_src_id': assignee['id'],
                    'issue_assignee_src_node': assignee['node_id']
                } for assignee in assignees_insert
            ]

            # Issue Labels
            
            cols_to_query = self.get_relevant_columns(self.issue_labels_table, label_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.issue_labels_table.c.issue_id == issue['issue_id'])).fetchall()

            source_labels_insert, _ = self.organize_needed_data(issue['labels'], table_values, 
                list(self.issue_labels_table.primary_key)[0].name, action_map=label_action_map)

            labels_insert += [
                {
                    'issue_id': issue['issue_id'],
                    'label_text': label['name'],
                    'label_description': label['description'] if 'description' in label else None,
                    'label_color': label['color'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source,
                    'label_src_id': label['id'],
                    'label_src_node_id': label['node_id']
                } for label in labels_insert
            ]

            # If the issue is closed, then we search for the closing event and store the user's id
            if 'closed_at' in issue:

                events_df = pd.DataFrame(issue_events['insert'])
                                
                closed_event = events_df.loc[events_df['event'] == 'closed'].tail(1)
                
                if len(closed_event) == 0:
                    self.logger.info("Warning! We do not have the closing event of this issue stored\n")
                else:
                    closer_cntrb_id = self.find_id_from_login(closed_event['actor'].values[0]['login'])

                    closed_issue_updates.append({
                        'b_issue_id': issue['issue_id'],
                        'cntrb_id': closer_cntrb_id
                    })

        # Closed issues, update with closer id
        self.bulk_insert(self.issues_table, update=closed_issue_updates, unique_columns=['issue_id'], 
            update_columns=['cntrb_id'])

        # Issue assignees insertion
        self.bulk_insert(self.issue_assignees_table, insert=assignees_insert, 
            unique_columns=assignee_action_map['insert']['augur'])

        # Issue labels insertion
        self.bulk_insert(self.issue_labels_table, insert=labels_insert, 
            unique_columns=label_action_map['insert']['augur'])
        
        # Register this task as completed
        self.register_task_completion(entry_info, repo_id, 'issues')
