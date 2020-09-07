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


#return the quarter in yearmonth form, when given a month and year
def create_routes(server):
    def new_contributor_data_collection(repo_id, num_contributions_required):



        with open("report_config.json") as config_file:
            config = json.load(config_file)

        jupyter_execution = False

        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(config['user'], config['password'], config['host'], config['port'], config['database'])


        dbschema='augur_data'
        engine = salc.create_engine(
            database_connection_string,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        rank_list = []
        for num in range(1, num_contributions_required + 1):
            rank_list.append(num)
        rank_tuple = tuple(rank_list)



        df = pd.DataFrame()


        pr_query = salc.sql.text(f"""        
        

        SELECT * FROM (
            SELECT ID AS
                cntrb_id,
                A.created_at AS created_at,
                date_part('month', A.created_at::DATE) AS month,
                date_part('year', A.created_at::DATE) AS year,
                A.repo_id,
                repo_name,
                full_name,
                login,
            ACTION,
            rank() OVER (
                    PARTITION BY id
                    ORDER BY A.created_at ASC
                )
            FROM
                (
                    (
                    SELECT
                        canonical_id AS ID,
                        created_at AS created_at,
                        repo_id,
                        'issue_opened' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        augur_data.issues
                        LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issues.reporter_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        repo_id = {repo_id}
                        AND pull_request IS NULL 
                    GROUP BY
                        canonical_id,
                        repo_id,
                        issues.created_at,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) UNION ALL
                    (
                    SELECT
                        canonical_id AS ID,
                        TO_TIMESTAMP( cmt_author_date, 'YYYY-MM-DD' ) AS created_at,
                        repo_id,
                        'commit' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        augur_data.commits
                        LEFT OUTER JOIN augur_data.contributors ON cntrb_email = cmt_author_email
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        repo_id = {repo_id} 
                    GROUP BY
                        repo_id,
                        canonical_email,
                        canonical_id,
                        commits.cmt_author_date,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) UNION ALL
                    (
                    SELECT
                        message.cntrb_id AS ID,
                        created_at AS created_at,
                        commits.repo_id,
                        'commit_comment' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login
          
                    FROM
                        augur_data.commit_comment_ref,
                        augur_data.commits,
                        augur_data.message
                        LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        commits.cmt_id = commit_comment_ref.cmt_id 
                        AND commits.repo_id = {repo_id} 
                        AND commit_comment_ref.msg_id = message.msg_id
     
                    GROUP BY
                        ID,
                        commits.repo_id,
                        commit_comment_ref.created_at,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login
                    ) UNION ALL
                    (
                    SELECT
                        issue_events.cntrb_id AS ID,
                        issue_events.created_at AS created_at,
                        repo_id,
                        'issue_closed' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        augur_data.issues,
                        augur_data.issue_events
                        LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = issue_events.cntrb_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        issues.repo_id = {repo_id} 
                        AND issues.issue_id = issue_events.issue_id 
                        AND issues.pull_request IS NULL 
                        AND issue_events.cntrb_id IS NOT NULL 
                        AND ACTION = 'closed' 
                    GROUP BY
                        issue_events.cntrb_id,
                        repo_id,
                        issue_events.created_at,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) UNION ALL
                    (
                    SELECT
                        pr_augur_contributor_id AS ID,
                        pr_created_at AS created_at,
                        repo_id,
                        'open_pull_request' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        augur_data.pull_requests
                        LEFT OUTER JOIN augur_data.contributors ON pull_requests.pr_augur_contributor_id = contributors.cntrb_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        pull_requests.repo_id = {repo_id} 
                    GROUP BY
                        pull_requests.pr_augur_contributor_id,
                        pull_requests.repo_id,
                        pull_requests.pr_created_at,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) UNION ALL
                    (
                    SELECT
                        message.cntrb_id AS ID,
                        msg_timestamp AS created_at,
                        repo_id,
                        'pull_request_comment' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        augur_data.pull_requests,
                        augur_data.pull_request_message_ref,
                        augur_data.message
                        LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        pull_requests.repo_id = {repo_id}
                        AND pull_request_message_ref.pull_request_id = pull_requests.pull_request_id 
                        AND pull_request_message_ref.msg_id = message.msg_id 
                    GROUP BY
                        message.cntrb_id,
                        pull_requests.repo_id,
                        message.msg_timestamp,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) UNION ALL
                    (
                    SELECT
                        issues.reporter_id AS ID,
                        msg_timestamp AS created_at,
                        repo_id,
                        'issue_comment' AS ACTION,
                        contributors.cntrb_full_name AS full_name,
                        contributors.cntrb_login AS login 
                    FROM
                        issues,
                        issue_message_ref,
                        message
                        LEFT OUTER JOIN augur_data.contributors ON contributors.cntrb_id = message.cntrb_id
                        LEFT OUTER JOIN ( SELECT DISTINCT ON ( cntrb_canonical ) cntrb_full_name, cntrb_canonical AS canonical_email, data_collection_date, cntrb_id AS canonical_id 
                        FROM augur_data.contributors WHERE cntrb_canonical = cntrb_email ORDER BY cntrb_canonical 
                        ) canonical_full_names ON canonical_full_names.canonical_email = contributors.cntrb_canonical 
                    WHERE
                        issues.repo_id = {repo_id}
                        AND issue_message_ref.msg_id = message.msg_id 
                        AND issues.issue_id = issue_message_ref.issue_id
                        AND issues.pull_request_id = NULL
                    GROUP BY
                        issues.reporter_id,
                        issues.repo_id,
                        message.msg_timestamp,
                        contributors.cntrb_full_name,
                        contributors.cntrb_login 
                    ) 
                ) A,
                repo 
            WHERE
            ID IS NOT NULL 
                AND A.repo_id = repo.repo_id 
            GROUP BY
                A.ID,
                A.repo_id,
                A.ACTION,
                A.created_at,
                repo.repo_name,
                A.full_name,
                A.login
            ORDER BY 
                cntrb_id
            ) b
            WHERE RANK IN {rank_tuple}

    """)
        df_first_repo = pd.read_sql(pr_query, con=engine)
        if not df.empty: 
            df = pd.concat([df, df_first_repo]) 
        else: 
            # first repo
            df = df_first_repo

        df = df.loc[~df['full_name'].str.contains('bot', na=False)]
        df = df.loc[~df['login'].str.contains('bot', na=False)]

        df = df.loc[~df['cntrb_id'].isin(df[df.duplicated(['cntrb_id', 'created_at', 'repo_id', 'rank'])]['cntrb_id'])]




        #add yearmonths to contributor
        df[['month', 'year']] = df[['month', 'year']].astype(int).astype(str)
        df['yearmonth'] = df['month'] + '/' + df['year']
        df['yearmonth'] = pd.to_datetime(df['yearmonth'])

        # add column with every value being one, so when the contributor df is concatenated with the months df, the filler months won't be counted in the sums
        df['new_contributors'] = 1

        def quarters(month, year):
            if month >= 1 and month <=3:
                return '01' + '/' + year
            elif month >=4 and month <=6:
                return '04' + '/' + year
            elif month >= 5 and month <=9:
                return '07' + '/' + year
            elif month >= 10 and month <= 12:
                return '10' + '/' + year

        #add quarters to contributor dataframe
        df['month'] = df['month'].astype(int)
        df['quarter'] = df.apply(lambda x: quarters(x['month'], x['year']), axis=1)
        df['quarter'] = pd.to_datetime(df['quarter'])

        return df

    def months_df_query(begin_date, end_date):
        months_df = pd.DataFrame()


        with open("report_config.json") as config_file:
            config = json.load(config_file)

        jupyter_execution = False

        database_connection_string = 'postgres+psycopg2://{}:{}@{}:{}/{}'.format(config['user'], config['password'], config['host'], config['port'], config['database'])

        dbschema='augur_data'
        engine = salc.create_engine(
            database_connection_string,
            connect_args={'options': '-csearch_path={}'.format(dbschema)})

        #months_query makes a df of years and months, this is used to fill the months with no data in the visualizaitons
        months_query = salc.sql.text(f"""        
          SELECT
                    *
                FROM
                (
                SELECT
                    date_part( 'year', created_month :: DATE ) AS year,
                    date_part( 'month', created_month :: DATE ) AS MONTH
                FROM
                    (SELECT * FROM ( SELECT created_month :: DATE FROM generate_series (TIMESTAMP '{begin_date}', TIMESTAMP '{end_date}', INTERVAL '1 month' ) created_month ) d ) x 
                ) y
        """)
        months_df = pd.read_sql(months_query, con=engine)


        def quarters(month, year):
            if month >= 1 and month <=3:
                return '01' + '/' + year
            elif month >=4 and month <=6:
                return '04' + '/' + year
            elif month >= 5 and month <=9:
                return '07' + '/' + year
            elif month >= 10 and month <= 12:
                return '10' + '/' + year


        #add yearmonths to months_df
        months_df[['year','month']] = months_df[['year','month']].astype(float).astype(int).astype(str)
        months_df['yearmonth'] = months_df['month'] + '/' + months_df['year']
        months_df['yearmonth'] = pd.to_datetime(months_df['yearmonth'])

        #filter months_df with begin_date and end_date, the contributor df is filtered in the visualizations
        months_df = months_df.set_index(months_df['yearmonth'])
        months_df = months_df.loc[begin_date : end_date].reset_index(drop = True)

        #add quarters to months dataframe
        months_df['month'] = months_df['month'].astype(int)
        months_df['quarter'] = months_df.apply(lambda x: quarters(x['month'], x['year']), axis=1)
        months_df['quarter'] = pd.to_datetime(months_df['quarter'])

        return months_df











