#!/usr/bin/env python
# coding: utf-8

# # Pull Request Analysis

#import psycopg2
import pandas as pd 
import sqlalchemy as salc
import numpy as np
import warnings
import datetime
import json
warnings.filterwarnings('ignore')


def create_routes(server):
    def pull_request_data_collection(repo_id, begin_date, end_date, flag, slow_20):
        with open("config.json") as config_file:
            config = json.load(config_file)

        jupyter_execution = False

        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(config['user'], config['password'], config['host'], config['port'], config['database'])

        dbschema='augur_data'
        engine = salc.create_engine(
            database_connection_string,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})


        #Data query
        pr_all = pd.DataFrame()


        pr_query = salc.sql.text(f"""
                        SELECT
                            repo.repo_id AS repo_id,
                            pull_requests.pr_src_id AS pr_src_id,
                            repo.repo_name AS repo_name,
                            pr_src_author_association,
                            repo_groups.rg_name AS repo_group,
                            pull_requests.pr_src_state,
                            pull_requests.pr_merged_at,
                            pull_requests.pr_created_at AS pr_created_at,
                            pull_requests.pr_closed_at AS pr_closed_at,
                            date_part( 'year', pr_created_at :: DATE ) AS CREATED_YEAR,
                            date_part( 'month', pr_created_at :: DATE ) AS CREATED_MONTH,
                            date_part( 'year', pr_closed_at :: DATE ) AS CLOSED_YEAR,
                            date_part( 'month', pr_closed_at :: DATE ) AS CLOSED_MONTH,
                            pr_src_meta_label,
                            pr_head_or_base,
                            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_close,
                            ( EXTRACT ( EPOCH FROM pull_requests.pr_closed_at ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_close, 
                            ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_first_response,
                            ( EXTRACT ( EPOCH FROM first_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_first_response, 
                            ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 3600 AS hours_to_last_response,
                            ( EXTRACT ( EPOCH FROM last_response_time ) - EXTRACT ( EPOCH FROM pull_requests.pr_created_at ) ) / 86400 AS days_to_last_response, 
                            first_response_time,
                            last_response_time,
                            average_time_between_responses,
                            assigned_count,
                            review_requested_count,
                            labeled_count,
                            subscribed_count,
                            mentioned_count,
                            referenced_count,
                            closed_count,
                            head_ref_force_pushed_count,
                            merged_count,
                            milestoned_count,
                            unlabeled_count,
                            head_ref_deleted_count,
                            comment_count,
                            lines_added, 
                            lines_removed,
                            commit_count, 
                            file_count
                        FROM
                            repo,
                            repo_groups,
                            pull_requests LEFT OUTER JOIN ( 
                                SELECT pull_requests.pull_request_id,
                                count(*) FILTER (WHERE action = 'assigned') AS assigned_count,
                                count(*) FILTER (WHERE action = 'review_requested') AS review_requested_count,
                                count(*) FILTER (WHERE action = 'labeled') AS labeled_count,
                                count(*) FILTER (WHERE action = 'unlabeled') AS unlabeled_count,
                                count(*) FILTER (WHERE action = 'subscribed') AS subscribed_count,
                                count(*) FILTER (WHERE action = 'mentioned') AS mentioned_count,
                                count(*) FILTER (WHERE action = 'referenced') AS referenced_count,
                                count(*) FILTER (WHERE action = 'closed') AS closed_count,
                                count(*) FILTER (WHERE action = 'head_ref_force_pushed') AS head_ref_force_pushed_count,
                                count(*) FILTER (WHERE action = 'head_ref_deleted') AS head_ref_deleted_count,
                                count(*) FILTER (WHERE action = 'milestoned') AS milestoned_count,
                                count(*) FILTER (WHERE action = 'merged') AS merged_count,
                                MIN(message.msg_timestamp) AS first_response_time,
                                COUNT(DISTINCT message.msg_timestamp) AS comment_count,
                                MAX(message.msg_timestamp) AS last_response_time,
                                (MAX(message.msg_timestamp) - MIN(message.msg_timestamp)) / COUNT(DISTINCT message.msg_timestamp) AS average_time_between_responses
                                FROM pull_request_events, pull_requests, repo, pull_request_message_ref, message
                                WHERE repo.repo_id = {repo_id}
                                AND repo.repo_id = pull_requests.repo_id
                                AND pull_requests.pull_request_id = pull_request_events.pull_request_id
                                AND pull_requests.pull_request_id = pull_request_message_ref.pull_request_id
                                AND pull_request_message_ref.msg_id = message.msg_id
                                GROUP BY pull_requests.pull_request_id
                            ) response_times
                            ON pull_requests.pull_request_id = response_times.pull_request_id
                            LEFT OUTER JOIN (
                                SELECT pull_request_commits.pull_request_id, count(DISTINCT pr_cmt_sha) AS commit_count                                FROM pull_request_commits, pull_requests, pull_request_meta
                                WHERE pull_requests.pull_request_id = pull_request_commits.pull_request_id
                                AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                                AND pull_requests.repo_id = {repo_id}
                                AND pr_cmt_sha <> pull_requests.pr_merge_commit_sha
                                AND pr_cmt_sha <> pull_request_meta.pr_sha
                                GROUP BY pull_request_commits.pull_request_id
                            ) all_commit_counts
                            ON pull_requests.pull_request_id = all_commit_counts.pull_request_id
                            LEFT OUTER JOIN (
                                SELECT MAX(pr_repo_meta_id), pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                                FROM pull_requests, pull_request_meta
                                WHERE pull_requests.pull_request_id = pull_request_meta.pull_request_id
                                AND pull_requests.repo_id = {repo_id}
                                AND pr_head_or_base = 'base'
                                GROUP BY pull_request_meta.pull_request_id, pr_head_or_base, pr_src_meta_label
                            ) base_labels
                            ON base_labels.pull_request_id = all_commit_counts.pull_request_id
                            LEFT OUTER JOIN (
                                SELECT sum(cmt_added) AS lines_added, sum(cmt_removed) AS lines_removed, pull_request_commits.pull_request_id, count(DISTINCT cmt_filename) AS file_count
                                FROM pull_request_commits, commits, pull_requests, pull_request_meta
                                WHERE cmt_commit_hash = pr_cmt_sha
                                AND pull_requests.pull_request_id = pull_request_commits.pull_request_id
                                AND pull_requests.pull_request_id = pull_request_meta.pull_request_id
                                AND pull_requests.repo_id = {repo_id}
                                AND commits.repo_id = pull_requests.repo_id
                                AND commits.cmt_commit_hash <> pull_requests.pr_merge_commit_sha
                                AND commits.cmt_commit_hash <> pull_request_meta.pr_sha
                                GROUP BY pull_request_commits.pull_request_id
                            ) master_merged_counts 
                            ON base_labels.pull_request_id = master_merged_counts.pull_request_id                    
                        WHERE 
                            repo.repo_group_id = repo_groups.repo_group_id 
                            AND repo.repo_id = pull_requests.repo_id 
                            AND repo.repo_id = {repo_id} 
                        ORDER BY
                           merged_count DESC
            """)
        pr_a = pd.read_sql(pr_query, con=engine)
        if not pr_all.empty: 
            pr_all = pd.concat([pr_all, pr_a]) 
        else: 
            # first repo
            pr_all = pr_a

        if jupyter_execution == True: 
            display(pr_all.head())
            pr_all.dtypes


        # # Begin data pre-processing and adding columns

        # ### Data type changing

        # change count columns from float datatype to integer
        pr_all[['assigned_count',
                  'review_requested_count',
                  'labeled_count',
                  'subscribed_count',
                  'mentioned_count',
                  'referenced_count',
                  'closed_count',
                  'head_ref_force_pushed_count',
                  'merged_count',
                  'milestoned_count',
                  'unlabeled_count',
                  'head_ref_deleted_count',
                  'comment_count',
                'commit_count',
                'file_count',
                'lines_added',
                'lines_removed'
               ]] = pr_all[['assigned_count',
                                              'review_requested_count',
                                              'labeled_count',
                                              'subscribed_count',
                                              'mentioned_count',
                                              'referenced_count',
                                              'closed_count',
                                                'head_ref_force_pushed_count',
                                            'merged_count',
                                              'milestoned_count',          
                                              'unlabeled_count',
                                              'head_ref_deleted_count',
                                              'comment_count',
                                                'commit_count',
                                                'file_count',
                                                'lines_added',
                                                'lines_removed'
                           ]].astype(float)
        # Change years to int so that doesn't display as 2019.0 for example
        pr_all[[
                    'created_year',
                   'closed_year']] = pr_all[['created_year',
                                               'closed_year']].fillna(-1).astype(int).astype(str)



        # ### Add `average_days_between_responses` and `average_hours_between_responses` columns


        # Get days for average_time_between_responses time delta

        pr_all['average_days_between_responses'] = pr_all['average_time_between_responses'].map(lambda x: x.days).astype(float)
        pr_all['average_hours_between_responses'] = pr_all['average_time_between_responses'].map(lambda x: x.days * 24).astype(float)




        # ### Date filtering entire dataframe




        start_date = pd.to_datetime(begin_date)
        # end_date = pd.to_datetime('2020-02-01 09:00:00')
        end_date = pd.to_datetime(end_date)
        pr_all = pr_all[(pr_all['pr_created_at'] > start_date) & (pr_all['pr_closed_at'] < end_date)]

        pr_all['created_year'] = pr_all['created_year'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(int)
        pr_all['created_month'] = pr_all['created_month'].map(lambda x: '{0:0>2}'.format(x))
        pr_all['created_yearmonth'] = pd.to_datetime(pr_all['created_year'].map(str) + '-' + pr_all['created_month'].map(str) + '-01')
        pr_all.head(1)


        # ### add `days_to_close` column for pull requests that are still open (closed pull requests already have this column filled from the query)
        # 
        # Note: there will be no pull requests that are still open in the dataframe if you filtered by an end date in the above cell




        import datetime
        # getting the number of days of (today - created at) for the PRs that are still open
        # and putting this in the days_to_close column

        # get timedeltas of creation time to todays date/time
        days_to_close_open_pr = datetime.datetime.now() - pr_all.loc[pr_all['pr_src_state'] == 'open']['pr_created_at']

        # get num days from above timedelta
        days_to_close_open_pr = days_to_close_open_pr.apply(lambda x: x.days).astype(int)

        # for only OPEN pr's, set the days_to_close column equal to above dataframe
        pr_all.loc[pr_all['pr_src_state'] == 'open'] = pr_all.loc[pr_all['pr_src_state'] == 'open'].assign(days_to_close=days_to_close_open_pr)

        pr_all.loc[pr_all['pr_src_state'] == 'open'].head()


        # ### Add `closed_yearmonth` column for only CLOSED pull requests




        # initiate column by setting all null datetimes
        pr_all['closed_yearmonth'] = pd.to_datetime(np.nan)

        # Fill column with prettified string of year/month closed that looks like: 2019-07-01
        pr_all.loc[pr_all['pr_src_state'] == 'closed'] = pr_all.loc[pr_all['pr_src_state'] == 'closed'].assign(
            closed_yearmonth = pd.to_datetime(pr_all.loc[pr_all['pr_src_state'] == 'closed']['closed_year'].astype(int
                ).map(str) + '-' + pr_all.loc[pr_all['pr_src_state'] == 'closed']['closed_month'].astype(int).map(str) + '-01'))

        pr_all.loc[pr_all['pr_src_state'] == 'closed']


        # ### Add `merged_flag` column which is just prettified strings based off of if the `pr_merged_at` column is null or not

        # In[10]:


        """ Merged flag """
        if 'pr_merged_at' in pr_all.columns.values:
            pr_all['pr_merged_at'] = pr_all['pr_merged_at'].fillna(0)
            pr_all['merged_flag'] = 'Not Merged / Rejected'
            pr_all['merged_flag'].loc[pr_all['pr_merged_at'] != 0] = 'Merged / Accepted'
            pr_all['merged_flag'].loc[pr_all['pr_src_state'] == 'open'] = 'Still Open'
            del pr_all['pr_merged_at']
        pr_all['merged_flag']


        # # Split into different dataframes
        # ### All, open, closed, and slowest 20% of these 3 categories (6 dataframes total)


        # Isolate the different state PRs for now
        pr_open = pr_all.loc[pr_all['pr_src_state'] == 'open']
        pr_closed = pr_all.loc[pr_all['pr_src_state'] == 'closed']
        pr_merged = pr_all.loc[pr_all['merged_flag'] == 'Merged / Accepted']
        pr_not_merged = pr_all.loc[pr_all['merged_flag'] == 'Not Merged / Rejected']
        pr_closed['merged_flag']


        # ### Create dataframes that contain the slowest 20% pull requests of each group

        # Filtering the 80th percentile slowest PRs

        def filter_20_per_slowest(input_df):
            pr_slow20_filtered = pd.DataFrame()
            pr_slow20_x = pd.DataFrame()

            #for value in repo_set: 
                
                #if not pr_slow20_filtered.empty: 
                    #pr_slow20x = input_df.query('repo_id==@value')
                    #pr_slow20x['percentile_rank_local'] = pr_slow20x.days_to_close.rank(pct=True)
                    #pr_slow20x = pr_slow20x.query('percentile_rank_local >= .8', )
                    #pr_slow20_filtered = pd.concat([pr_slow20x, pr_slow20_filtered]) 
                    #reponame = str(value)
                    #filename = ''.join(['output/pr_slowest20pct', reponame, '.csv'])
                    #pr_slow20x.to_csv(filename)
                #else: 
                

            # first time
            pr_slow20_filtered = input_df.copy()
            pr_slow20_filtered['percentile_rank_local'] = pr_slow20_filtered.days_to_close.rank(pct=True)
            pr_slow20_filtered = pr_slow20_filtered.query('percentile_rank_local >= .8', )
        #     print(pr_slow20_filtered.describe())
            return pr_slow20_filtered

        pr_slow20_open = filter_20_per_slowest(pr_open)
        pr_slow20_closed = filter_20_per_slowest(pr_closed)
        pr_slow20_merged = filter_20_per_slowest(pr_merged)
        pr_slow20_not_merged = filter_20_per_slowest(pr_not_merged)
        pr_slow20_all = filter_20_per_slowest(pr_all)
        pr_slow20_merged#.head()


        if flag == 'all':
            if slow_20 == True:
                pr_all = filter_20_per_slowest(pr_all)

            return pr_all

        elif flag == 'closed':

            pr_closed = pr_all.loc[pr_all['pr_src_state'] == 'closed']
            if slow_20 == True:
                pr_closed = filter_20_per_slowest(pr_closed)

            return pr_closed

        elif flag == 'open':
            pr_open = pr_open = pr_all.loc[pr_all['pr_src_state'] == 'open']
            if slow_20 == True:
                pr_open = filter_20_per_slowest(pr_open)
            return pr_open

        elif flag == 'pr_merged':
            pr_merged = pr_all.loc[pr_all['merged_flag'] == 'Merged / Accepted']
            if slow_20 == True:
                pr_merged = filter_20_per_slowest(pr_merged) 
            return pr_merged

        elif flag == 'pr_not_merged':
            pr_not_merged = pr_all.loc[pr_all['merged_flag'] == 'Not Merged / Rejected']
            if slow_20 == True:
                pr_not_merged = filter_20_per_slowest(pr_not_merged)
            return pr_not_merged


