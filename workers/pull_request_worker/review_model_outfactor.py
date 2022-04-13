    def pull_request_reviews_model(self, pk_source_prs=[]):

        if not pk_source_prs:
            pk_source_prs = self._get_pk_source_prs()

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
            (
                f"https://api.github.com/repos/{self.owner}/{self.repo}/pulls/{pr['number']}/"
                "reviews?per_page=100", {'pull_request_id': pr['pull_request_id']}
            )
            for pr in pk_source_prs
        ]

        pr_pk_source_reviews = self.multi_thread_urls(reviews_urls)
        self.write_debug_data(pr_pk_source_reviews, 'pr_pk_source_reviews')

        cols_to_query = self.get_relevant_columns(
            self.pull_request_reviews_table, review_action_map
        )

        #I don't know what else this could be used for so I'm using it for the function call
        table_values = self.db.execute(s.sql.select(cols_to_query).where(
            self.pull_request_reviews_table.c.pull_request_id.in_(
                    set(pd.DataFrame(pk_source_prs)['pull_request_id'])
                ))).fetchall()

        source_reviews_insert, source_reviews_update = self.organize_needed_data(
            pr_pk_source_reviews, table_values=table_values,
            action_map=review_action_map
        )

        if len(source_reviews_insert) > 0:
            source_reviews_insert = self.enrich_cntrb_id(
                source_reviews_insert, str('user.login'), action_map_additions={
                    'insert': {
                        'source': ['user.node_id'],
                        'augur': ['gh_node_id']
                    }
                }, prefix='user.'
            )
        else:
            self.logger.info("Contributor enrichment is not needed, source_reviews_insert is empty.")

        reviews_insert = [
            {
                'pull_request_id': review['pull_request_id'],
                'cntrb_id': review['cntrb_id'],
                'pr_review_author_association': review['author_association'],
                'pr_review_state': review['state'],
                'pr_review_body': str(review['body']).encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                    review['body']
                ) else None,
                'pr_review_submitted_at': review['submitted_at'] if (
                    'submitted_at' in review
                ) else None,
                'pr_review_src_id': int(float(review['id'])), #12/3/2021 cast as int due to error. # Here, `pr_review_src_id` is mapped to `id` SPG 11/29/2021. This is fine. Its the review id.
                'pr_review_node_id': review['node_id'],
                'pr_review_html_url': review['html_url'],
                'pr_review_pull_request_url': review['pull_request_url'],
                'pr_review_commit_id': review['commit_id'],
                'tool_source': 'pull_request_reviews model',
                'tool_version': self.tool_version+ "_reviews",
                'data_source': self.data_source,
                'repo_id': self.repo_id,
                'platform_id': self.platform_id 
            } for review in source_reviews_insert if review['user'] and 'login' in review['user']
        ]

        try:
            self.bulk_insert(
                self.pull_request_reviews_table, insert=reviews_insert, update=source_reviews_update,
                unique_columns=review_action_map['insert']['augur'],
                update_columns=review_action_map['update']['augur']
            )
        except Exception as e:
            self.print_traceback("PR reviews data model", e, True)

        # Merge source data to inserted data to have access to inserted primary keys

        gh_merge_fields = ['id']
        augur_merge_fields = ['pr_review_src_id']

        both_pr_review_pk_source_reviews = self.enrich_data_primary_keys(
            pr_pk_source_reviews, self.pull_request_reviews_table, gh_merge_fields,
            augur_merge_fields, in_memory=True
        )
        self.write_debug_data(both_pr_review_pk_source_reviews, 'both_pr_review_pk_source_reviews')

        # Review Comments

       #  https://api.github.com/repos/chaoss/augur/pulls

        review_msg_url = (f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls' +
            '/comments?per_page=100&page={}')

        '''This includes the two columns that are in the natural key for messages
            Its important to note the inclusion of tool_source on the augur side.
            That exists because of an anomaly in the GitHub API, where the messages
            API for Issues and the issues API will return all the messages related to
            pull requests.

            Logically, the only way to tell the difference is, in the case of issues, the
            pull_request_id in the issues table is null.

            The pull_request_id in the pull_requests table is never null.

            So, issues has the full set issues. Pull requests has the full set of pull requests.
            there are no issues in the pull requests table.
        '''

        review_msg_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['platform_msg_id']
            }
        }

        ''' This maps to the two unique columns that constitute the natural key in the table.
        '''

        review_msg_ref_action_map = {
            'insert': {
                'source': ['id'],
                'augur': ['pr_review_msg_src_id']
            }
        }

        in_clause = [] if len(both_pr_review_pk_source_reviews) == 0 else set(pd.DataFrame(both_pr_review_pk_source_reviews)['pr_review_id'])

        review_msgs = self.paginate_endpoint(
            review_msg_url, action_map=review_msg_action_map, table=self.message_table,
            where_clause=self.message_table.c.msg_id.in_(
                [
                    msg_row[0] for msg_row in self.db.execute(
                        s.sql.select([self.pull_request_review_message_ref_table.c.msg_id]).where(
                            self.pull_request_review_message_ref_table.c.pr_review_id.in_(
                                in_clause
                            )
                        )
                    ).fetchall()
                ]
            )
        )
        self.write_debug_data(review_msgs, 'review_msgs')

        if len(review_msgs['insert']) > 0:
            review_msgs['insert'] = self.enrich_cntrb_id(
                review_msgs['insert'], str('user.login'), action_map_additions={
                    'insert': {
                        'source': ['user.node_id'],
                        'augur': ['gh_node_id']
                    }
                }, prefix='user.'
            )
        else:
            self.logger.info("Contributor enrichment is not needed, nothing to insert from the action map.")

        review_msg_insert = [
            {
                'pltfrm_id': self.platform_id,
                'msg_text': str(comment['body']).encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                    comment['body']
                ) else None,
                'msg_timestamp': comment['created_at'],
                'cntrb_id': comment['cntrb_id'],
                'tool_source': self.tool_source +"_reviews",
                'tool_version': self.tool_version + "_reviews",
                'data_source': 'pull_request_reviews model',
                'repo_id': self.repo_id,
                'platform_msg_id': int(float(comment['id'])),
                'platform_node_id': comment['node_id']
            } for comment in review_msgs['insert']
            if comment['user'] and 'login' in comment['user']
        ]

        self.bulk_insert(self.message_table, insert=review_msg_insert,
            unique_columns = review_msg_action_map['insert']['augur'])

        # PR REVIEW MESSAGE REF TABLE

        c_pk_source_comments = self.enrich_data_primary_keys(
            review_msgs['insert'], self.message_table, review_msg_action_map['insert']['source'],
            review_msg_action_map['insert']['augur'], in_memory=True 
        )

        self.write_debug_data(c_pk_source_comments, 'c_pk_source_comments')

        ''' The action map does not apply here because this is a reference to the parent
        table.  '''


        both_pk_source_comments = self.enrich_data_primary_keys(
            c_pk_source_comments, self.pull_request_reviews_table, ['pull_request_review_id'],
            ['pr_review_src_id'], in_memory=True
        )
        self.write_debug_data(both_pk_source_comments, 'both_pk_source_comments')

        pr_review_msg_ref_insert = [
            {
                'pr_review_id':  comment['pr_review_id'],
                'msg_id': comment['msg_id'], #msg_id turned up null when I removed the cast to int .. 
                'pr_review_msg_url': comment['url'],
                'pr_review_src_id': int(comment['pull_request_review_id']),
                'pr_review_msg_src_id': int(comment['id']),
                'pr_review_msg_node_id': comment['node_id'],
                'pr_review_msg_diff_hunk': comment['diff_hunk'],
                'pr_review_msg_path': comment['path'],
                'pr_review_msg_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['position'] #12/6/2021 - removed casting from value check
                ) else comment['position'],
                'pr_review_msg_original_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['original_position'] #12/6/2021 - removed casting from value check
                ) else comment['original_position'],
                'pr_review_msg_commit_id': str(comment['commit_id']),
                'pr_review_msg_original_commit_id': str(comment['original_commit_id']),
                'pr_review_msg_updated_at': comment['updated_at'],
                'pr_review_msg_html_url': comment['html_url'],
                'pr_url': comment['pull_request_url'],
                'pr_review_msg_author_association': comment['author_association'],
                'pr_review_msg_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['start_line'] #12/6/2021 - removed casting from value check
                ) else comment['start_line'],
                'pr_review_msg_original_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['original_start_line']  #12/6/2021 - removed casting from value check
                ) else int(comment['original_start_line']),
                'pr_review_msg_start_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    str(comment['start_side'])
                ) else str(comment['start_side']),
                'pr_review_msg_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['line']  #12/6/2021 - removed casting from value check
                ) else int(comment['line']),
                'pr_review_msg_original_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    comment['original_line']  #12/6/2021 - removed casting from value check
                ) else int(comment['original_line']),
                'pr_review_msg_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
                    str(comment['side'])
                ) else str(comment['side']),
                'tool_source': 'pull_request_reviews model',
                'tool_version': self.tool_version + "_reviews",
                'data_source': self.data_source,
                'repo_id': self.repo_id
            } for comment in both_pk_source_comments
        ]

        try: 

            self.bulk_insert(
                self.pull_request_review_message_ref_table,
                insert=pr_review_msg_ref_insert, unique_columns = review_msg_ref_action_map['insert']['augur']
            )
        except Exception as e:
            self.print_traceback("bulk insert for review message ref", e, True)