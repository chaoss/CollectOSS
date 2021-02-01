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
            'pull_request_files', 'pull_request_reviews', 'pull_request_review_message_ref']
        operations_tables = ['worker_history', 'worker_job']

        self.deep_collection = True
        self.platform_id = 25150 # GitHub

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

        github_url = entry_info['given']['github_url']

        self.query_github_contributors(entry_info, repo_id)

        self.logger.info('Beginning collection of Pull Requests...\n')
        self.logger.info(f'Repo ID: {repo_id}, Git URL: {github_url}\n')

        owner, repo = self.get_owner_repo(github_url)

        pr_url = (f'https://api.github.com/repos/{owner}/{repo}/pulls?state=all&' +
            'direction=asc&per_page=100&page={}')

        pr_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['pr_src_id']
            },
            'update': {
                'source': ['state'],
                'augur': ['pr_src_state']
            }
        }

        source_prs = self.paginate_endpoint(pr_url, action_map=pr_action_map, 
            table=self.pull_requests_table, where_clause=self.pull_requests_table.c.repo_id == repo_id)

        if len(source_prs['all']) == 0:
            self.logger.info("There are no prs for this repository.\n")
            self.register_task_completion(entry_info, repo_id, 'pull_requests')
            return

        prs_insert = [
            {
                'repo_id': repo_id,
                'pr_url': pr['url'],
                'pr_src_id': pr['id'],
                'pr_src_node_id': None,
                'pr_html_url': pr['html_url'],
                'pr_diff_url': pr['diff_url'],
                'pr_patch_url': pr['patch_url'],
                'pr_issue_url': pr['issue_url'],
                'pr_augur_issue_id': None,
                'pr_src_number': pr['number'],
                'pr_src_state': pr['state'],
                'pr_src_locked': pr['locked'],
                'pr_src_title': pr['title'],
                'pr_augur_contributor_id': self.find_id_from_login(pr['user']['login']),
                'pr_body': pr['body'],
                'pr_created_at': pr['created_at'],
                'pr_updated_at': pr['updated_at'],
                'pr_closed_at': pr['closed_at'],
                'pr_merged_at': pr['merged_at'],
                'pr_merge_commit_sha': pr['merge_commit_sha'],
                'pr_teams': None,
                'pr_milestone': pr['milestone']['title'] if pr['milestone'] else None,
                'pr_commits_url': pr['commits_url'],
                'pr_review_comments_url': pr['review_comments_url'],
                'pr_review_comment_url': pr['review_comment_url'],
                'pr_comments_url': pr['comments_url'],
                'pr_statuses_url': pr['statuses_url'],
                'pr_meta_head_id': None,
                'pr_meta_base_id': None,
                'pr_src_issue_url': pr['issue_url'],
                'pr_src_comments_url': pr['comments_url'], # NOTE: this seems redundant
                'pr_src_review_comments_url': pr['review_comments_url'], # this too
                'pr_src_commits_url': pr['commits_url'], # this one also seems redundant
                'pr_src_statuses_url': pr['statuses_url'],
                'pr_src_author_association': pr['author_association'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': 'GitHub API'
            } for pr in source_prs['insert']
        ]

        if len(source_prs['insert']) > 0 or len(source_prs['update']) > 0:

            pr_insert_result, pr_update_result = self.bulk_insert(self.pull_requests_table, 
                update=source_prs['update'], unique_columns=pr_action_map['insert']['augur'], 
                insert=prs_insert, update_columns=pr_action_map['update']['augur'])

            source_data = source_prs['insert'] + source_prs['update']

        elif not self.deep_collection:
            self.logger.info("There are no prs to update, insert, or collect nested "
                "information for.\n")
            self.register_task_completion(entry_info, repo_id, 'pull_requests')
            return

        if self.deep_collection:
            source_data = source_prs['all']

        # Merge source data to inserted data to have access to inserted primary keys

        gh_merge_fields = ['id']
        augur_merge_fields = ['pr_src_id']

        pk_source_prs = self.enrich_data_primary_keys(source_data, self.pull_requests_table, 
            gh_merge_fields, augur_merge_fields)

        # Messages/comments

        comments_url = (f'https://api.github.com/repos/{owner}/{repo}/issues' +
            '/comments?per_page=100&page={}')

        comment_action_map = {
            'insert': {
                'source': ['created_at', 'body'],
                'augur': ['msg_timestamp', 'msg_text']
            }
        }

        pr_comments = self.paginate_endpoint(comments_url, 
            action_map=comment_action_map, table=self.message_table)

        pr_comments['insert'] = self.text_clean(pr_comments['insert'], 'body')

        pr_comments_insert = [
            {
                'pltfrm_id': self.platform_id,
                'msg_text': comment['body'].replace("\x00", "\uFFFD"),
                'msg_timestamp': comment['created_at'],
                'cntrb_id': self.find_id_from_login(comment['user']['login']),
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for comment in pr_comments['insert']
        ]

        self.bulk_insert(self.message_table, insert=pr_comments_insert)
            
        # PR MESSAGE REF TABLE

        c_pk_source_comments = self.enrich_data_primary_keys(pr_comments['insert'], 
            self.message_table, ['created_at', 'body'], ['msg_timestamp', 'msg_text'])

        both_pk_source_comments = self.enrich_data_primary_keys(c_pk_source_comments, 
            self.pull_requests_table, ['issue_url'], ['pr_issue_url'])

        pr_message_ref_insert = [
            {
                'pull_request_id': comment['pull_request_id'],
                'msg_id': comment['msg_id'],
                'pr_message_ref_src_comment_id': comment['id'],
                'pr_message_ref_src_node_id': comment['node_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for comment in both_pk_source_comments
        ]

        self.bulk_insert(self.pull_request_message_ref_table, insert=pr_message_ref_insert)

        # PR Events          
    
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
        pr_events = self.paginate_endpoint(events_url, table=self.pull_request_events_table,
            action_map=event_action_map, where_clause=self.pull_request_events_table.c.pull_request_id.in_(
                    set(pd.DataFrame(pk_source_prs)['pull_request_id'])
                ))

        pk_pr_events = self.enrich_data_primary_keys(pr_events['insert'], 
            self.pull_requests_table, ['issue.url'], ['pr_issue_url'])

        pr_events_insert = [
            {
                'pull_request_id': event['pull_request_id'],
                'cntrb_id': self.find_id_from_login(event['actor']['login']),
                'action': event['event'],
                'action_commit_hash': None,
                'created_at': event['created_at'],
                'issue_event_src_id': event['id'],
                'node_id': event['node_id'],
                'node_url': event['url'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for event in pk_pr_events if event['actor'] is not None
        ]

        self.bulk_insert(self.pull_request_events_table, insert=pr_events_insert)

        # Reviews

        review_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['pr_review_src_id']
            },
            'update': {
                'source': ['state'],
                'augur': ['pr_review_state']
            }
        }

        reviews_urls = [
            (f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr['number']}/reviews?per_page=100",
                {'pull_request_id': pr['pull_request_id']})
            for pr in pk_source_prs
        ]

        pr_pk_source_reviews = self.multi_thread_urls(reviews_urls)

        cols_to_query = self.get_relevant_columns(self.pull_request_reviews_table, review_action_map)

        table_values = self.db.execute(s.sql.select(cols_to_query).where(
            self.pull_request_reviews_table.c.pull_request_id.in_(
                    set(pd.DataFrame(pk_source_prs)['pull_request_id'])
                ))).fetchall()

        source_reviews_insert, source_reviews_update = self.organize_needed_data(pr_pk_source_reviews, 
            table_values, list(self.pull_request_reviews_table.primary_key)[0].name, action_map=review_action_map)

        reviews_insert = [
            {
                'pull_request_id': review['pull_request_id'],
                'cntrb_id': self.find_id_from_login(review['user']['login']),
                'pr_review_author_association': review['author_association'],
                'pr_review_state': review['state'],
                'pr_review_body': review['body'],
                'pr_review_submitted_at': review['submitted_at'] if 'submitted_at' in review else None,
                'pr_review_src_id': review['id'],
                'pr_review_node_id': review['node_id'],
                'pr_review_html_url': review['html_url'],
                'pr_review_pull_request_url': review['pull_request_url'],
                'pr_review_commit_id': review['commit_id'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for review in source_reviews_insert if review['user'] and 'login' in review['user']
        ]

        self.bulk_insert(self.pull_request_reviews_table, insert=reviews_insert, update=source_reviews_update,
            unique_columns=review_action_map['insert']['augur'], update_columns=review_action_map['update']['augur'])

        # Merge source data to inserted data to have access to inserted primary keys

        gh_merge_fields = ['id']
        augur_merge_fields = ['pr_review_src_id']

        both_pr_review_pk_source_reviews = self.enrich_data_primary_keys(pr_pk_source_reviews, 
            self.pull_request_reviews_table, gh_merge_fields, augur_merge_fields)

        # Review Comments

        review_msg_url = (f'https://api.github.com/repos/{owner}/{repo}/pulls' +
            '/comments?per_page=100&page={}')

        review_msg_action_map = {
            'insert': {
                'source': ['created_at', 'body'],
                'augur': ['msg_timestamp', 'msg_text']
            }
        }

        in_clause = [] if len(both_pr_review_pk_source_reviews) == 0 else \
            set(pd.DataFrame(both_pr_review_pk_source_reviews)['pr_review_id'])

        review_msgs = self.paginate_endpoint(review_msg_url, 
            action_map=review_msg_action_map, table=self.message_table, 
            where_clause=self.message_table.c.msg_id.in_(
                    [msg_row[0] for msg_row in self.db.execute(s.sql.select(
                        [self.pull_request_review_message_ref_table.c.msg_id]).where(
                        self.pull_request_review_message_ref_table.c.pr_review_id.in_(
                            in_clause
                        ))).fetchall()]
                ))

        review_msg_insert = [
            {
                'pltfrm_id': self.platform_id,
                'msg_text': comment['body'],
                'msg_timestamp': comment['created_at'],
                'cntrb_id': self.find_id_from_login(comment['user']['login']),
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for comment in review_msgs['insert'] if comment['user'] and 'login' in comment['user']
        ]

        self.bulk_insert(self.message_table, insert=review_msg_insert)
            
        # PR REVIEW MESSAGE REF TABLE

        c_pk_source_comments = self.enrich_data_primary_keys(review_msgs['insert'], 
            self.message_table, ['created_at', 'body'], ['msg_timestamp', 'msg_text'])
        both_pk_source_comments = self.enrich_data_primary_keys(c_pk_source_comments, 
            self.pull_request_reviews_table, ['pull_request_review_id'], ['pr_review_src_id'])

        pr_review_msg_ref_insert = [
            {
                'pr_review_id': comment['pr_review_id'],
                'msg_id': comment['msg_id'],
                'pr_review_msg_url': comment['url'],
                'pr_review_src_id': comment['pull_request_review_id'],
                'pr_review_msg_src_id': comment['id'],
                'pr_review_msg_node_id': comment['node_id'],
                'pr_review_msg_diff_hunk': comment['diff_hunk'],
                'pr_review_msg_path': comment['path'],
                'pr_review_msg_position': comment['position'],
                'pr_review_msg_original_position': comment['original_position'],
                'pr_review_msg_commit_id': comment['commit_id'],
                'pr_review_msg_original_commit_id': comment['original_commit_id'],
                'pr_review_msg_updated_at': comment['updated_at'],
                'pr_review_msg_html_url': comment['html_url'],
                'pr_url': comment['pull_request_url'],
                'pr_review_msg_author_association': comment['author_association'],
                'pr_review_msg_start_line': comment['start_line'],
                'pr_review_msg_original_start_line': comment['original_start_line'],
                'pr_review_msg_start_side': comment['start_side'],
                'pr_review_msg_line': comment['line'],
                'pr_review_msg_original_line': comment['original_line'],
                'pr_review_msg_side': comment['side'],
                'tool_source': self.tool_source,
                'tool_version': self.tool_version,
                'data_source': self.data_source
            } for comment in both_pk_source_comments
        ]

        self.bulk_insert(self.pull_request_review_message_ref_table, insert=pr_review_msg_ref_insert)

        # PR nested info table insertions

        labels_insert = []
        reviewers_insert = []
        assignees_insert = []
        meta_insert = []

        label_action_map = { 
            'insert': {
                'source': ['pull_request_id', 'id'],
                'augur': ['pull_request_id', 'pr_src_id']
            }
        }

        reviewer_action_map = {
            'insert': {
                'source': ['pull_request_id', 'id'],
                'augur': ['pull_request_id', 'pr_reviewer_src_id']
            }
        }

        assignee_action_map = {
            'insert': {
                'source': ['pull_request_id', 'id'],
                'augur': ['pull_request_id', 'pr_assignee_src_id']
            }
        }

        meta_action_map = {
            'insert': {
                'source': ['pull_request_id', 'sha', 'pr_head_or_base'],
                'augur': ['pull_request_id', 'pr_sha', 'pr_head_or_base']
            }
        }

        for pr in pk_source_prs:

            # PR Labels
            
            cols_to_query = self.get_relevant_columns(self.pull_request_labels_table, label_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.pull_request_labels_table.c.pull_request_id == pr['pull_request_id'])).fetchall()

            source_labels = pd.DataFrame(pr['labels'])
            source_labels['pull_request_id'] = pr['pull_request_id']

            source_labels_insert, _ = self.organize_needed_data(json.loads(source_labels.to_json(orient='records')), 
                table_values, list(self.pull_request_labels_table.primary_key)[0].name, action_map=label_action_map)

            labels_insert += [
                {
                    'pull_request_id': label['pull_request_id'],
                    'pr_src_id': label['id'],
                    'pr_src_node_id': label['node_id'],
                    'pr_src_url': label['url'],
                    'pr_src_description': label['name'],
                    'pr_src_color': label['color'],
                    'pr_src_default_bool': label['default'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for label in source_labels_insert
            ]

            # Reviewers

            cols_to_query = self.get_relevant_columns(self.pull_request_reviewers_table, reviewer_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.pull_request_reviewers_table.c.pull_request_id == pr['pull_request_id'])).fetchall()

            source_reviewers = pd.DataFrame(pr['requested_reviewers'])
            source_reviewers['pull_request_id'] = pr['pull_request_id']

            source_reviewers_insert, _ = self.organize_needed_data(json.loads(source_reviewers.to_json(orient='records')), 
                table_values, list(self.pull_request_reviewers_table.primary_key)[0].name, action_map=reviewer_action_map)

            reviewers_insert += [
                {
                    'pull_request_id': reviewer['pull_request_id'],
                    'cntrb_id': self.find_id_from_login(reviewer['login']),
                    'pr_reviewer_src_id': reviewer['id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for reviewer in source_reviewers_insert if 'login' in reviewer
            ]

            # Assignees

            cols_to_query = self.get_relevant_columns(self.pull_request_assignees_table, assignee_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.pull_request_assignees_table.c.pull_request_id == pr['pull_request_id'])).fetchall()

            source_assignees = pd.DataFrame(pr['assignees'])
            source_assignees['pull_request_id'] = pr['pull_request_id']

            source_assignees_insert, _ = self.organize_needed_data(json.loads(source_assignees.to_json(orient='records')), 
                table_values, list(self.pull_request_assignees_table.primary_key)[0].name, action_map=assignee_action_map)

            assignees_insert += [
                {
                    'pull_request_id': assignee['pull_request_id'],
                    'contrib_id': self.find_id_from_login(assignee['login']),
                    'pr_assignee_src_id': assignee['id'],
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for assignee in source_assignees_insert if 'login' in assignee
            ]

            # Meta

            cols_to_query = self.get_relevant_columns(self.pull_request_meta_table, meta_action_map)

            table_values = self.db.execute(s.sql.select(cols_to_query).where(
                self.pull_request_meta_table.c.pull_request_id == pr['pull_request_id'])).fetchall()

            pr['head'].update({'pr_head_or_base': 'head', 'pull_request_id': pr['pull_request_id']})
            pr['base'].update({'pr_head_or_base': 'base', 'pull_request_id': pr['pull_request_id']})

            source_meta_insert, _ = self.organize_needed_data([pr['head'], pr['base']], 
                table_values, list(self.pull_request_meta_table.primary_key)[0].name, action_map=meta_action_map)

            meta_insert += [
                {
                    'pull_request_id': meta['pull_request_id'],
                    'pr_head_or_base': meta['pr_head_or_base'],
                    'pr_src_meta_label': meta['label'],
                    'pr_src_meta_ref': meta['ref'],
                    'pr_sha': meta['sha'],
                    'cntrb_id': self.find_id_from_login(meta['user']['login']),
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                } for meta in source_meta_insert if meta['user'] and 'login' in meta['user']
            ]

        # PR labels insertion
        self.bulk_insert(self.pull_request_labels_table, insert=labels_insert)

        # PR reviewers insertion
        self.bulk_insert(self.pull_request_reviewers_table, insert=reviewers_insert)

        # PR assignees insertion
        self.bulk_insert(self.pull_request_assignees_table, insert=assignees_insert)

        # PR meta insertion
        self.bulk_insert(self.pull_request_meta_table, insert=meta_insert)

        self.register_task_completion(entry_info, repo_id, 'pull_requests')

    def query_pr_repo(self, pr_repo, pr_repo_type, pr_meta_id):
        """ TODO: insert this data as extra columns in the meta table """
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
