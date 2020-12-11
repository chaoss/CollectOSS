#SPDX-License-Identifier: MIT
import ast, json, logging, os, sys, time, traceback, requests
from datetime import datetime
from multiprocessing import Process, Queue
import pandas as pd
import sqlalchemy as s
from sqlalchemy.sql.expression import bindparam
from workers.worker_base import Worker

class GitHubPullRequestWorker(Worker):
    """
    Worker that collects Pull Request related data from the Github API and stores it in our database.

    :param task: most recent task the broker added to the worker's queue
    :param config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = "pull_request_worker"

        # Define what this worker can be given and know how to interpret
        given = [['github_url']]
        models = ['pull_requests', 'pull_request_commits', 'pull_request_files']

        # Define the tables needed to insert, update, or delete on
        data_tables = ['contributors', 'pull_requests',
            'pull_request_assignees', 'pull_request_events', 'pull_request_labels',
            'pull_request_message_ref', 'pull_request_meta', 'pull_request_repo',
            'pull_request_reviewers', 'pull_request_teams', 'message', 'pull_request_commits',
            'pull_request_files']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        # Define data collection info
        self.tool_source = 'GitHub Pull Request Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'GitHub API'
     
    def graphql_paginate(self, query, data_subjects, before_parameters=None):
        """ Paginate a GitHub GraphQL query backwards

        :param query: A string, holds the GraphQL query
        :rtype: A Pandas DataFrame, contains all data contained in the pages
        """

        self.logger.info(f'Start paginate with params: \n{data_subjects} '
            f'\n{before_parameters}')

        def all_items(dictionary):
            for key, value in dictionary.items():
                if type(value) is dict:
                    yield (key, value)
                    yield from all_items(value)
                else:
                    yield (key, value)

        if not before_parameters:
            before_parameters = {}
            for subject, _ in all_items(data_subjects):
                before_parameters[subject] = ''

        start_cursor = None
        has_previous_page = True
        base_url = 'https://api.github.com/graphql'
        tuples = []

        def find_root_of_subject(data, key_subject):
            self.logger.info(f'Finding {key_subject} root of {data}')
            key_nest = None
            for subject, nest in data.items():
                if key_subject in nest: 
                    key_nest = nest[key_subject]
                    break
                elif type(nest) == dict:
                    return find_root_of_subject(nest, key_subject)
            else:
                raise KeyError
            return key_nest
            
        for data_subject, nest in data_subjects.items():

            self.logger.info(f'Beginning paginate process for field {data_subject} '
                f'for query: {query}')

            page_count = 0
            while has_previous_page:

                page_count += 1

                num_attempts = 3
                success = False

                for attempt in range(num_attempts):
                    self.logger.info(f'Attempt #{attempt + 1} for hitting GraphQL endpoint '
                        f'page number {page_count}\n')

                    response = requests.post(base_url, json={'query': query.format(
                        **before_parameters)}, headers=self.headers)

                    self.update_gh_rate_limit(response)

                    try:
                        data = response.json()
                    except:
                        data = json.loads(json.dumps(response.text))

                    if 'errors' in data:
                        self.logger.info("Error!: {}".format(data['errors']))
                        if j['errors'][0]['type'] == 'NOT_FOUND':
                            self.logger.warning("Github repo was not found or does not exist for endpoint: {}\n".format(url))
                            break
                        if data['errors'][0]['type'] == 'RATE_LIMITED':
                            self.update_gh_rate_limit(response)
                            num_attempts -= 1
                        continue
                        

                    if 'data' in data:
                        success = True
                        root = find_root_of_subject(data, data_subject)
                        page_info = root['pageInfo']
                        data = root['edges']
                        break
                    else:
                        self.logger.info("Request returned a non-data dict: {}\n".format(data))
                        if data['message'] == 'Not Found':
                            self.logger.info("Github repo was not found or does not exist for endpoint: {}\n".format(base_url))
                            break
                        if data['message'] == 'You have triggered an abuse detection mechanism. Please wait a few minutes before you try again.':
                            num_attempts -= 1
                            self.update_gh_rate_limit(response, temporarily_disable=True)
                        if data['message'] == 'Bad credentials':
                            self.update_gh_rate_limit(response, bad_credentials=True)

                if not success:
                    self.logger.info('GraphQL query failed: {}'.format(query))
                    break

                before_parameters.update({
                    data_subject: ', before: \"{}\"'.format(page_info['startCursor'])
                })
                has_previous_page = page_info['hasPreviousPage']

                tuples += data

            self.logger.info(f'Paged through {page_count} pages and '
                f'collected {len(tuples)} data points\n')

            if not nest:
                return tuples

            return tuples + self.graphql_paginate(query, data_subjects[subject], 
                before_parameters=before_parameters)


    def pull_request_files_model(self, task_info, repo_id):

        owner, repo = self.get_owner_repo(task_info['given']['github_url'])

        # query existing PRs and the respective url we will append the commits url to
        pr_number_sql = s.sql.text("""
            SELECT DISTINCT pr_src_number as pr_src_number, pull_requests.pull_request_id
            FROM pull_requests--, pull_request_meta
            WHERE repo_id = {}
        """.format(repo_id))
        pr_numbers = pd.read_sql(pr_number_sql, self.db, params={})

        pr_file_rows = []

        for index, pull_request in enumerate(pr_numbers.itertuples()): 

            self.logger.info(f'Querying files for pull request #{index + 1} of {len(pr_numbers)}')
        
            query = """
                {{ 
                  repository(owner:"%s", name:"%s"){{
                    pullRequest (number: %s) {{
                """ % (owner, repo, pull_request.pr_src_number) + """
                      files (last: 100{files}) {{
                        pageInfo {{
                          hasPreviousPage
                          hasNextPage
                          endCursor
                          startCursor
                        }}
                        edges {{
                          node {{
                            additions
                            deletions
                            path
                          }}
                        }}
                      }}
                    }}
                  }}
                }}
            """ 

            pr_file_rows += [{
                'pull_request_id': pull_request.pull_request_id,
                'pr_file_additions': pr_file['node']['additions'],
                'pr_file_deletions': pr_file['node']['deletions'],
                'pr_file_path': pr_file['node']['path'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'GitHub API',
            } for pr_file in self.graphql_paginate(query, {'files': None})]


        # Get current table values
        table_values_sql = s.sql.text("""
            SELECT pull_request_files.* 
            FROM pull_request_files, pull_requests
            WHERE pull_request_files.pull_request_id = pull_requests.pull_request_id
            AND repo_id = :repo_id
        """)
        self.logger.info(f'Getting table values with the following PSQL query: \n{table_values_sql}\n')
        table_values = pd.read_sql(table_values_sql, self.db, params={'repo_id': repo_id})

        # Compare queried values against table values for dupes/updates
        if len(pr_file_rows) > 0:
            table_columns = pr_file_rows[0].keys()
        else:
            self.logger.info(f'No rows need insertion for repo {repo_id}\n')
            self.register_task_completion(task_info, repo_id, 'pull_request_files')
            return

        # Compare queried values against table values for dupes/updates
        pr_file_rows_df = pd.DataFrame(pr_file_rows)
        pr_file_rows_df = pr_file_rows_df.dropna(subset=['pull_request_id'])

        dupe_columns = ['pull_request_id', 'pr_file_path']
        update_columns = ['pr_file_additions', 'pr_file_deletions']

        need_insertion = pr_file_rows_df.merge(table_values, suffixes=('','_table'),
                            how='outer', indicator=True, on=dupe_columns).loc[
                                lambda x : x['_merge']=='left_only'][table_columns]

        need_updates = pr_file_rows_df.merge(table_values, on=dupe_columns, suffixes=('','_table'), 
                        how='inner',indicator=False)[table_columns].merge(table_values, 
                            on=update_columns, suffixes=('','_table'), how='outer',indicator=True
                                ).loc[lambda x : x['_merge']=='left_only'][table_columns]

        need_updates['b_pull_request_id'] = need_updates['pull_request_id'] 
        need_updates['b_pr_file_path'] = need_updates['pr_file_path'] 

        pr_file_insert_rows = need_insertion.to_dict('records')
        pr_file_update_rows = need_updates.to_dict('records')

        self.logger.info(f'Repo id {repo_id} needs {len(need_insertion)} insertions and '
            f'{len(need_updates)} updates.\n')

        if len(pr_file_update_rows) > 0:
            success = False
            while not success:
                try:
                    self.db.execute(
                        self.pull_request_files_table.update().where(
                            self.pull_request_files_table.c.pull_request_id == bindparam('b_pull_request_id') and
                            self.pull_request_files_table.c.pr_file_path == bindparam('b_pr_file_path')).values(
                                pr_file_additions=bindparam('pr_file_additions'), 
                                pr_file_deletions=bindparam('pr_file_deletions')),
                        pr_file_update_rows
                    )
                    success = True
                except Exception as e:
                    self.logger.info('error: {}'.format(e))
                time.sleep(5)

        if len(pr_file_insert_rows) > 0:
            success = False
            while not success:
                try:
                    self.db.execute(
                        self.pull_request_files_table.insert(),
                        pr_file_insert_rows
                    )
                    success = True
                except Exception as e:
                    self.logger.info('error: {}'.format(e))
                time.sleep(5)

        self.register_task_completion(task_info, repo_id, 'pull_request_files')

    def pull_request_commits_model(self, task_info, repo_id):
        """ Queries the commits related to each pull request already inserted in the db """

        self.logger.info("Querying starting ids info...\n")

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1
        self.pr_id_inc = self.get_max_id('pull_requests', 'pull_request_id')
        self.pr_meta_id_inc = self.get_max_id('pull_request_meta', 'pr_repo_meta_id')


        # query existing PRs and the respective url we will append the commits url to
        pr_url_sql = s.sql.text("""
            SELECT DISTINCT pr_url, pull_requests.pull_request_id
            FROM pull_requests--, pull_request_meta
            WHERE repo_id = {}
        """.format(repo_id))
        urls = pd.read_sql(pr_url_sql, self.db, params={})

        for pull_request in urls.itertuples(): # for each url of PRs we have inserted
            commits_url = pull_request.pr_url + '/commits?page={}'
            table = 'pull_request_commits'
            table_pkey = 'pr_cmt_id'
            duplicate_col_map = {'pr_cmt_sha': 'sha'}
            update_col_map = {}

            # Use helper paginate function to iterate the commits url and check for dupes
            pr_commits = self.paginate(commits_url, duplicate_col_map, update_col_map, table, table_pkey, 
                where_clause="where pull_request_id = {}".format(pull_request.pull_request_id))

            for pr_commit in pr_commits: # post-pagination, iterate results
                if pr_commit['flag'] == 'need_insertion': # if non-dupe
                    pr_commit_row = {
                        'pull_request_id': pull_request.pull_request_id,
                        'pr_cmt_sha': pr_commit['sha'],
                        'pr_cmt_node_id': pr_commit['node_id'],
                        'pr_cmt_message': pr_commit['commit']['message'],
                        # 'pr_cmt_comments_url': pr_commit['comments_url'],
                        'tool_source': self.tool_source,
                        'tool_version': self.tool_version,
                        'data_source': 'GitHub API',
                    }
                    result = self.db.execute(self.pull_request_commits_table.insert().values(pr_commit_row))
                    self.logger.info(f"Inserted Pull Request Commit: {result.inserted_primary_key}\n")

        self.register_task_completion(task_info, repo_id, 'pull_request_commits')

    def pull_requests_model(self, entry_info, repo_id):
        """Pull Request data collection function. Query GitHub API for PhubRs.

        :param entry_info: A dictionary consisiting of 'git_url' and 'repo_id'
        :type entry_info: dict
        """

        self.logger.info("Querying starting ids info...\n")

        # Increment so we are ready to insert the 'next one' of each of these most recent ids
        self.history_id = self.get_max_id('worker_history', 'history_id', operations_table=True) + 1
        self.pr_id_inc = self.get_max_id('pull_requests', 'pull_request_id')
        self.pr_meta_id_inc = self.get_max_id('pull_request_meta', 'pr_repo_meta_id')

        github_url = entry_info['given']['github_url']

        self.logger.info('Beginning collection of Pull Requests...\n')
        self.logger.info(f'Repo ID: {repo_id}, Git URL: {github_url}\n')

        owner, repo = self.get_owner_repo(github_url)

        url = (f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all&' +
            'direction=asc&per_page=100&page={}')

        # Get pull requests that we already have stored
        #   Set pseudo key (something other than PK) to 
        #   check dupicates with
        table = 'pull_requests'
        table_pkey = 'pull_request_id'
        update_col_map = {'pr_src_state': 'state'} 
        duplicate_col_map = {'pr_src_id': 'id'}

        #list to hold pull requests needing insertion
        prs = self.paginate(url, duplicate_col_map, update_col_map, table, table_pkey, 
            where_clause='WHERE repo_id = {}'.format(repo_id),
            value_update_col_map={'pr_augur_contributor_id': float('nan')})

        # Discover and remove duplicates before we start inserting
        self.logger.info("Count of pull requests needing update or insertion: " + str(len(prs)) + "\n")

        for pr_dict in prs:

            pr = {
                'repo_id': repo_id,
                'pr_url': pr_dict['url'],
                'pr_src_id': pr_dict['id'],
                'pr_src_node_id': None,
                'pr_html_url': pr_dict['html_url'],
                'pr_diff_url': pr_dict['diff_url'],
                'pr_patch_url': pr_dict['patch_url'],
                'pr_issue_url': pr_dict['issue_url'],
                'pr_augur_issue_id': None,
                'pr_src_number': pr_dict['number'],
                'pr_src_state': pr_dict['state'],
                'pr_src_locked': pr_dict['locked'],
                'pr_src_title': pr_dict['title'],
                'pr_augur_contributor_id': self.find_id_from_login(pr_dict['user']['login']),
                'pr_body': pr_dict['body'],
                'pr_created_at': pr_dict['created_at'],
                'pr_updated_at': pr_dict['updated_at'],
                'pr_closed_at': pr_dict['closed_at'],
                'pr_merged_at': pr_dict['merged_at'],
                'pr_merge_commit_sha': pr_dict['merge_commit_sha'],
                'pr_teams': None,
                'pr_milestone': pr_dict['milestone']['title'] if pr_dict['milestone'] else None,
                'pr_commits_url': pr_dict['commits_url'],
                'pr_review_comments_url': pr_dict['review_comments_url'],
                'pr_review_comment_url': pr_dict['review_comment_url'],
                'pr_comments_url': pr_dict['comments_url'],
                'pr_statuses_url': pr_dict['statuses_url'],
                'pr_meta_head_id': None,
                'pr_meta_base_id': None,
                'pr_src_issue_url': pr_dict['issue_url'],
                'pr_src_comments_url': pr_dict['comments_url'], # NOTE: this seems redundant
                'pr_src_review_comments_url': pr_dict['review_comments_url'], # this too
                'pr_src_commits_url': pr_dict['commits_url'], # this one also seems redundant
                'pr_src_statuses_url': pr_dict['statuses_url'],
                'pr_src_author_association': pr_dict['author_association'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'GitHub API'
            }

            if pr_dict['flag'] == 'need_insertion':
                self.logger.info(f'PR {pr_dict["id"]} needs to be inserted\n')

                result = self.db.execute(self.pull_requests_table.insert().values(pr))
                self.logger.info(f"Added Pull Request: {result.inserted_primary_key}")
                self.pr_id_inc = int(result.inserted_primary_key[0])

            elif pr_dict['flag'] == 'need_update':
                result = self.db.execute(self.pull_requests_table.update().where(
                    self.pull_requests_table.c.pr_src_id==pr_dict['id']).values(pr))
                self.logger.info("Updated tuple in the pull_requests table with existing pr_src_id: {}".format(
                    pr_dict['id']))
                self.pr_id_inc = pr_dict['pkey']

            else:
                self.logger.info("PR does not need to be inserted. Fetching its id from DB")
                pr_id_sql = s.sql.text("""
                    SELECT pull_request_id FROM pull_requests
                    WHERE pr_src_id={}
                """.format(pr_dict['id']))

                self.pr_id_inc = int(pd.read_sql(pr_id_sql, self.db).iloc[0]['pull_request_id'])

            self.query_labels(pr_dict['labels'], self.pr_id_inc)
            self.query_pr_events(owner, repo, pr_dict['number'], self.pr_id_inc)
            self.query_pr_comments(owner, repo, pr_dict['number'], self.pr_id_inc)
            self.query_reviewers(pr_dict['requested_reviewers'], self.pr_id_inc)
            self.query_pr_meta(pr_dict['head'], pr_dict['base'], self.pr_id_inc)

            self.logger.info(f"Inserted PR data for {owner}/{repo}")
            self.results_counter += 1

        self.register_task_completion(entry_info, repo_id, 'pull_requests')

    def query_labels(self, labels, pr_id):
        self.logger.info('Querying PR Labels\n')

        if len(labels) == 0:
            self.logger.info('No new labels to add\n')
            return

        table = 'pull_request_labels'
        duplicate_col_map = {'pr_src_id': 'id'}
        update_col_map = {}
        table_pkey = 'pr_label_id'

        update_keys = list(update_col_map.keys()) if update_col_map else []
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]

        pr_labels_table_values = self.get_table_values(cols_query, [table])

        new_labels = self.assign_tuple_action(labels, pr_labels_table_values, update_col_map, duplicate_col_map, 
                table_pkey)

        self.logger.info(f'Found {len(new_labels)} labels\n')

        for label_dict in new_labels:

            label = {
                'pull_request_id': pr_id,
                'pr_src_id': label_dict['id'],
                'pr_src_node_id': label_dict['node_id'],
                'pr_src_url': label_dict['url'],
                'pr_src_description': label_dict['name'],
                'pr_src_color': label_dict['color'],
                'pr_src_default_bool': label_dict['default'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            if label_dict['flag'] == 'need_insertion':
                result = self.db.execute(self.pull_request_labels_table.insert().values(label))
                self.logger.info(f"Added PR Label: {result.inserted_primary_key}\n")
                self.logger.info(f"Inserted PR Labels data for PR with id {pr_id}\n")

                self.results_counter += 1

    def query_pr_events(self, owner, repo, gh_pr_no, pr_id):
        self.logger.info('Querying PR Events\n')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/{gh_pr_no}' +
            '/events?per_page=100&page={}')

        # Get pull request events that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        table = 'pull_request_events'
        table_pkey = 'pr_event_id'
        update_col_map = {}
        duplicate_col_map = {'issue_event_src_id': 'id'}

        #list to hold contributors needing insertion or update
        pr_events = self.paginate(url, duplicate_col_map, update_col_map, table, table_pkey)
        
        self.logger.info("Count of pull request events needing insertion: " + str(len(pr_events)) + "\n")

        for pr_event_dict in pr_events:

            if pr_event_dict['actor']:
                cntrb_id = self.find_id_from_login(pr_event_dict['actor']['login'])
            else:
                cntrb_id = 1

            pr_event = {
                'pull_request_id': pr_id,
                'cntrb_id': cntrb_id,
                'action': pr_event_dict['event'],
                'action_commit_hash': None,
                'created_at': pr_event_dict['created_at'],
                'issue_event_src_id': pr_event_dict['id'],
                'node_id': pr_event_dict['node_id'],
                'node_url': pr_event_dict['url'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            result = self.db.execute(self.pull_request_events_table.insert().values(pr_event))
            self.logger.info(f"Added PR Event: {result.inserted_primary_key}\n")

            self.results_counter += 1

        self.logger.info(f"Inserted PR Events data for PR with id {pr_id}\n")

    def query_reviewers(self, reviewers, pr_id):
        self.logger.info('Querying Reviewers')

        if reviewers is None or len(reviewers) == 0:
            self.logger.info('No reviewers to add')
            return

        table = 'pull_request_reviewers'
        duplicate_col_map = {'pr_reviewer_map_id': 'id'}
        update_col_map = {}
        table_pkey = 'pr_reviewer_map_id'

        update_keys = list(update_col_map.keys()) if update_col_map else []
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]

        reviewers_table_values = self.get_table_values(cols_query, [table])

        new_reviewers = self.assign_tuple_action(reviewers, reviewers_table_values, update_col_map, duplicate_col_map, 
                table_pkey)

        for reviewers_dict in new_reviewers:

            if 'login' in reviewers_dict:
                cntrb_id = self.find_id_from_login(reviewers_dict['login'])
            else:
                cntrb_id = 1

            reviewer = {
                'pull_request_id': pr_id,
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            if reviewers_dict['flag'] == 'need_insertion':
                result = self.db.execute(self.pull_request_reviewers_table.insert().values(reviewer))
                self.logger.info(f"Added PR Reviewer {result.inserted_primary_key}")

                self.results_counter += 1

        self.logger.info(f"Finished inserting PR Reviewer data for PR with id {pr_id}")

    def query_assignee(self, assignees, pr_id):
        self.logger.info('Querying Assignees')

        if assignees is None or len(assignees) == 0:
            self.logger.info('No assignees to add')
            return

        table = 'pull_request_assignees'
        duplicate_col_map = {'pr_assignee_map_id': 'id'}
        update_col_map = {}
        table_pkey = 'pr_assignee_map_id'

        update_keys = list(update_col_map.keys()) if update_col_map else []
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]

        assignee_table_values = self.get_table_values(cols_query, [table])

        assignees = self.assign_tuple_action(assignees, assignee_table_values, update_col_map, duplicate_col_map, 
                table_pkey)

        for assignee_dict in assignees:

            if 'login' in assignee_dict:
                cntrb_id = self.find_id_from_login(assignee_dict['login'])
            else:
                cntrb_id = 1

            assignee = {
                'pull_request_id': pr_id,
                'contrib_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            if assignee_dict['flag'] == 'need_insertion':
                result = self.db.execute(self.pull_request_assignees_table.insert().values(assignee))
                self.logger.info(f'Added PR Assignee {result.inserted_primary_key}')

                self.results_counter += 1

        self.logger.info(f'Finished inserting PR Assignee data for PR with id {pr_id}')

    def query_pr_meta(self, head, base, pr_id):
        self.logger.info('Querying PR Meta')

        table = 'pull_request_meta'
        duplicate_col_map = {'pr_sha': 'sha'}
        update_col_map = {}
        value_update_col_map = {'pr_src_meta_label': None}
        table_pkey = 'pr_repo_meta_id'

        update_keys = list(update_col_map.keys()) if update_col_map else []
        update_keys += list(value_update_col_map.keys())
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]

        meta_table_values = self.get_table_values(cols_query, [table])

        pr_meta_dict = {
            'head': self.assign_tuple_action([head], meta_table_values, update_col_map, duplicate_col_map, 
                table_pkey, value_update_col_map=value_update_col_map)[0],
            'base': self.assign_tuple_action([base], meta_table_values, update_col_map, duplicate_col_map, 
                table_pkey, value_update_col_map=value_update_col_map)[0]
        }

        for pr_side, pr_meta_data in pr_meta_dict.items():
            pr_meta = {
                'pull_request_id': pr_id,
                'pr_head_or_base': pr_side,
                'pr_src_meta_label': pr_meta_data['label'],
                'pr_src_meta_ref': pr_meta_data['ref'],
                'pr_sha': pr_meta_data['sha'],
                'cntrb_id': self.find_id_from_login(pr_meta_data['user']['login']) if pr_meta_data['user'] \
                    and 'login' in pr_meta_data['user'] else None,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            if pr_meta_data['flag'] == 'need_update':
                result = self.db.execute(self.pull_request_meta_table.update().where(
                        self.pull_request_meta_table.c.pr_sha==pr_meta['pr_sha'] and
                        self.pull_request_meta_table.c.pr_head_or_base==pr_side 
                    ).values(pr_meta))
                # self.logger.info("Updated tuple in the issues table with existing gh_issue_id: {}".format(issue_dict['id']))
                self.pr_meta_id_inc = pr_meta_data['pkey']
            elif pr_meta_data['flag'] == 'need_insertion':

                result = self.db.execute(self.pull_request_meta_table.insert().values(pr_meta))
                self.logger.info(f'Added PR Head {result.inserted_primary_key}')

                self.pr_meta_id_inc = int(result.inserted_primary_key[0])
                self.results_counter += 1
            else:
                pr_meta_id_sql = """
                    SELECT pr_repo_meta_id FROM pull_request_meta
                    WHERE pr_sha='{}'
                """.format(pr_meta_data['sha'])

                self.pr_meta_id_inc = int(pd.read_sql(pr_meta_id_sql, self.db).iloc[0]['pr_repo_meta_id'])

            if pr_meta_data['repo']:
                self.query_pr_repo(pr_meta_data['repo'], pr_side, self.pr_meta_id_inc)
            else:
                self.logger.info('No new PR Head data to add')

        self.logger.info(f'Finished inserting PR Head & Base data for PR with id {pr_id}')

    def query_pr_comments(self, owner, repo, gh_pr_no, pr_id):
        self.logger.info('Querying PR Comments')

        url = (f'https://api.github.com/repos/{owner}/{repo}/issues/{gh_pr_no}' +
            '/comments?per_page=100&page={}')

        # Get pull request comments that we already have stored
        #   Set our duplicate and update column map keys (something other than PK) to 
        #   check dupicates/needed column updates with
        table = 'pull_request_message_ref'
        table_pkey = 'pr_msg_ref_id'
        update_col_map = {}
        duplicate_col_map = {'pr_message_ref_src_comment_id': 'id'}

        #list to hold contributors needing insertion or update
        pr_messages = self.paginate(url, duplicate_col_map, update_col_map, table, table_pkey)
        
        self.logger.info("Count of pull request comments needing insertion: " + str(len(pr_messages)) + "\n")

        for pr_msg_dict in pr_messages:

            if pr_msg_dict['user'] and 'login' in pr_msg_dict['user']:
                cntrb_id = self.find_id_from_login(pr_msg_dict['user']['login'])
            else:
                cntrb_id = 1

            msg = {
                'rgls_id': None,
                'msg_text': pr_msg_dict['body'].replace("0x00", "____") if \
                    'body' in pr_msg_dict else None,
                'msg_timestamp': pr_msg_dict['created_at'],
                'msg_sender_email': None,
                'msg_header': None,
                'pltfrm_id': '25150',
                'cntrb_id': cntrb_id,
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            result = self.db.execute(self.message_table.insert().values(msg))
            self.logger.info(f'Added PR Comment {result.inserted_primary_key}')

            pr_msg_ref = {
                'pull_request_id': pr_id,
                'msg_id': int(result.inserted_primary_key[0]),
                'pr_message_ref_src_comment_id': pr_msg_dict['id'],
                'pr_message_ref_src_node_id': pr_msg_dict['node_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            }

            result = self.db.execute(
                self.pull_request_message_ref_table.insert().values(pr_msg_ref)
            )
            self.logger.info(f'Added PR Message Ref {result.inserted_primary_key}')

            self.results_counter += 1

        self.logger.info(f'Finished adding PR Message data for PR with id {pr_id}')

    def query_pr_repo(self, pr_repo, pr_repo_type, pr_meta_id):
        self.logger.info(f'Querying PR {pr_repo_type} repo')

        table = 'pull_request_repo'
        duplicate_col_map = {'pr_src_repo_id': 'id'}
        update_col_map = {}
        table_pkey = 'pr_repo_id'

        update_keys = list(update_col_map.keys()) if update_col_map else []
        cols_query = list(duplicate_col_map.keys()) + update_keys + [table_pkey]

        pr_repo_table_values = self.get_table_values(cols_query, [table])

        new_pr_repo = self.assign_tuple_action([pr_repo], pr_repo_table_values, update_col_map, duplicate_col_map, 
                table_pkey)[0]

        if new_pr_repo['owner'] and 'login' in new_pr_repo['owner']:
            cntrb_id = self.find_id_from_login(new_pr_repo['owner']['login'])
        else:
            cntrb_id = 1

        pr_repo = {
            'pr_repo_meta_id': pr_meta_id,
            'pr_repo_head_or_base': pr_repo_type,
            'pr_src_repo_id': new_pr_repo['id'],
            # 'pr_src_node_id': new_pr_repo[0]['node_id'],
            'pr_src_node_id': None,
            'pr_repo_name': new_pr_repo['name'],
            'pr_repo_full_name': new_pr_repo['full_name'],
            'pr_repo_private_bool': new_pr_repo['private'],
            'pr_cntrb_id': cntrb_id,
            'tool_source': self.tool_source,
            'tool_version': self.tool_version,
            'data_source': self.data_source
        }

        if new_pr_repo['flag'] == 'need_insertion':
            result = self.db.execute(self.pull_request_repo_table.insert().values(pr_repo))
            self.logger.info(f'Added PR {pr_repo_type} repo {result.inserted_primary_key}')

            self.results_counter += 1

            self.logger.info(f'Finished adding PR {pr_repo_type} Repo data for PR with id {self.pr_id_inc}')
