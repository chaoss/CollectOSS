import logging
import os
import datetime

import joblib
import pandas as pd
import sqlalchemy as s

from augur.tasks.data_analysis.message_insights.message_sentiment import get_senti_score

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo, PullRequestAnalysis
from augur.application.db.engine import create_database_engine
from augur.application.db.util import execute_session_query

# from sklearn.metrics import (confusion_matrix, f1_score, precision_score, recall_score)
# from sklearn.preprocessing import LabelEncoder, MinMaxScaler
# from xgboost import XGBClassifier

ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

@celery.task
def pull_request_analysis_model(repo_git: str) -> None:

    logger = logging.getLogger(pull_request_analysis_model.__name__)

    tool_source = 'Pull Request Analysis Worker'
    tool_version = '0.0.0'
    data_source = 'Non-existent API'

    insight_days = 200

    with DatabaseSession(logger) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

        senti_models_dir = os.path.join(ROOT_AUGUR_DIRECTORY, "tasks", "data_analysis", "message_insights", session.config.get_value("Message_Insights", 'models_dir'))

        logger.info(f'Sentiment model dir located - {senti_models_dir}')

    # Any initial database instructions, like finding the last tuple inserted or generate the next ID value

    # Collection and insertion of data happens here
    begin_date = datetime.datetime.now() - datetime.timedelta(days=insight_days)

    logger.info(f'Fetching open PRs of repo: {repo_id}')

    # Fetch open PRs of repo and associated commits
    pr_SQL = s.sql.text("""
        select pull_requests.pull_request_id, 
        pr_created_at, pr_src_state, 
        pr_closed_at, pr_merged_at, 
        pull_request_commits.pr_cmt_id, 
        pr_augur_contributor_id, 
        pr_src_author_association 
        from augur_data.pull_requests
        INNER JOIN augur_data.pull_request_commits on pull_requests.pull_request_id = pull_request_commits.pull_request_id 
        where pr_created_at > :begin_date 
        and pull_requests.repo_id = :repo_id 
        and pr_src_state like 'open' 
    """)

    df_pr = pd.read_sql_query(pr_SQL, create_database_engine(), params={'begin_date': begin_date, 'repo_id': repo_id})

    logger.info(f'PR Dataframe dim: {df_pr.shape}\n')

    # DEBUG:
    # df_pr.to_csv(f'PRA.csv',index=False)

    if df_pr.empty:
        logger.warning('No new open PRs in tables to analyze!\n')
        return

    logger.info(f'Getting count of commits associated with every PR')

    # Get count of commits associated with every PR
    df_pr['commit_counts'] = df_pr.groupby(['pull_request_id'])['pr_cmt_id'].transform('count')
    df_pr = df_pr.drop(['pr_cmt_id'], axis=1)

    # Find length of PR in days upto now
    df_pr['pr_length'] = (datetime.datetime.now() - df_pr['pr_created_at']).dt.days

    logger.info(f'Fetching messages relating to PR')

    # Get sentiment score of all messages relating to the PR
    messages_SQL = s.sql.text("""
            select message.msg_id, msg_timestamp,  msg_text, message.cntrb_id from augur_data.message
            left outer join augur_data.pull_request_message_ref on message.msg_id = pull_request_message_ref.msg_id 
            left outer join augur_data.pull_requests on pull_request_message_ref.pull_request_id = pull_requests.pull_request_id where pull_request_message_ref.repo_id = :repo_id
            UNION
            select message.msg_id, msg_timestamp, msg_text, message.cntrb_id from augur_data.message
            left outer join augur_data.issue_message_ref on message.msg_id = issue_message_ref.msg_id 
            left outer join augur_data.issues on issue_message_ref.issue_id = issues.issue_id where issue_message_ref.repo_id = :repo_id""")

    df_message = pd.read_sql_query(messages_SQL, create_database_engine(), params={'repo_id': repo_id})

    logger.info(f'Mapping messages to PR, find comment & participants counts')

    # Map PR to its corresponding messages
    pr_ref_sql = s.sql.text("select * from augur_data.pull_request_message_ref")
    df_pr_ref = pd.read_sql_query(pr_ref_sql, create_database_engine())
    df_merge = pd.merge(df_pr, df_pr_ref, on='pull_request_id', how='left')
    df_merge = pd.merge(df_merge, df_message, on='msg_id', how='left')
    df_merge = df_merge.dropna(subset=['msg_id'], axis=0)

    if df_merge.empty:
        logger.warning('Not enough data to analyze!\n')
        return

    logger.info(f'cols: {df_merge.columns}')

    df_merge['senti_score'] = get_senti_score(df_merge, 'msg_text', senti_models_dir, label=False,
                                              logger=logger)

    logger.info(f'Calculated sentiment scores!')

    # Get count of associated comments
    df_merge['comment_counts'] = df_merge.groupby(['pull_request_id'])['msg_id'].transform('count')

    # Get participants count
    participants = pd.DataFrame(df_merge.groupby(['pull_request_id'])['cntrb_id'].nunique())
    participants = participants.reset_index()
    participants = participants.rename(columns={"cntrb_id": "usr_counts"})
    df_merge = pd.merge(df_merge, participants, on='pull_request_id', how='left')

    df_fin = df_merge[
        ['pull_request_id', 'pr_created_at', 'pr_closed_at', 'pr_merged_at', 'commit_counts', 'comment_counts',
         'pr_length', 'senti_score', 'pr_augur_contributor_id', 'pr_src_author_association', 'usr_counts']]

    # Find the mean of sentiment scores
    df_fin['comment_senti_score'] = df_fin.groupby(['pull_request_id'])['senti_score'].transform('mean')
    df_fin = df_fin.drop(['senti_score'], axis=1)
    df_fin = df_fin.drop_duplicates()

    '''
    # Get cntrb info from API
    cntrb_sql = 'SELECT cntrb_id, gh_login FROM augur_data.contributors'
    df_ctrb = pd.read_sql_query(cntrb_SQL, create_database_engine())
    df_fin1 = pd.merge(df_fin,df_ctrb,left_on='pr_augur_contributor_id', right_on='cntrb_id', how='left')
    df_fin1 = df_fin1.drop(['cntrb_id'],axis=1)
    # Dict for persisting user data & fast lookups
    user_info = {}
    df_fin1['usr_past_pr_accept'] = df_fin1['gh_login'].apply(self.fetch_user_info)
    df_fin = df_fin1
    '''

    logger.info(f'Fetching repo statistics')

    # Get repo info
    repo_sql = s.sql.text("""
            SELECT repo_id, pull_requests_merged, pull_request_count,watchers_count, last_updated FROM 
            augur_data.repo_info where repo_id = :repo_id
            """)
    df_repo = pd.read_sql_query(repo_sql, create_database_engine(), params={'repo_id': repo_id})

    df_repo = df_repo.loc[df_repo.groupby('repo_id').last_updated.idxmax(), :]
    df_repo = df_repo.drop(['last_updated'], axis=1)

    # Calculate acceptance ration of repo
    df_repo['pr_accept_ratio'] = df_repo['pull_requests_merged'] / df_repo['pull_request_count']
    df_repo = df_repo.drop(['pull_requests_merged', 'pull_request_count'], axis=1)

    df = pd.concat([df_fin, df_repo], axis=1)
    df = df.drop_duplicates()

    df = df.drop(['pr_created_at', 'pr_closed_at', 'pr_merged_at', 'pr_augur_contributor_id'], axis=1)

    logger.info(f'Process fetched features')

    # Label encode association levels of users
    df['assc_level'] = df['pr_src_author_association'].apply(encoder)
    df = df.drop(['pr_src_author_association'], axis=1)

    # Collect features
    features = df[
        ['commit_counts', 'comment_counts', 'pr_length', 'assc_level', 'comment_senti_score', 'watchers_count',
         'pr_accept_ratio']]

    logger.info(f'All features collected!')

    logger.info(f'Load pretrained model')

    # Load trained model
    model = joblib.load('trained_pr_model.pkl')
    merge_prob = model.predict_proba(features)

    df['merge_prob'] = [item[1] for item in merge_prob]

    logger.info(f'Analysis done!')

    # DEBUG:
    # df.to_csv(f'PRA_{repo_id}.csv',index=False)

    # Insertion of merge probability to pull_request_analysis table

    logger.info('Begin PR_analysis data insertion...')
    logger.info(f'{df.shape[0]} data records to be inserted')

    with DatabaseSession(logger) as session:
        for row in df.itertuples(index=False):
            try:
                msg = {
                    "pull_request_id": row.pull_request_id,
                    "merge_probability": row.merge_prob,
                    "mechanism": 'XGB-C',
                    "tool_source": tool_source,
                    "tool_version": tool_version,
                    "data_source": data_source,
                }

                pull_request_analysis_obj = PullRequestAnalysis(**msg)
                session.add(pull_request_analysis_obj)
                session.commit()

                # result = db.execute(pull_request_analysis_table.insert().values(msg))
                logger.info(
                    f'Primary key inserted into the pull_request_analysis table: {pull_request_analysis_obj.pull_request_analysis_id}')
                # results_counter += 1
                # logger.info(f'Inserted data point {results_counter} with pr_id {row.pull_request_id}')
            except Exception as e:
                logger.error(f'Error occurred while storing datapoint {repr(e)}')
                logger.error(f'{repr(row.merge_prob)}')
                break

    logger.info('Data insertion completed\n')

'''
Function to fetch GH user info from GitHub APIs: Needs API rate limit
def fetch_user_info(self,uname):
    print(uname)
    if uname in user_info:
        return user_info[uname]['merged']/user_info[uname]['total']

    url = f"https://api.github.com/search/issues?q=is:pr+author:{uname}+is:merged"
    # make the request and return the json
    user_data = requests.get(url).json()
    merged = user_data['total_count']

    url = f"https://api.github.com/search/issues?q=is:pr+author:{uname}"
    # make the request and return the json
    user_data = requests.get(url).json()
    total = user_data['total_count']

    user_info['uname'] = {"merged": merged, "total": total}
    return merged/total
'''

def encoder(x):
    if x == 'NONE':
        return 0
    if x == 'CONTRIBUTOR':
        return 1
    if x == 'COLLABORATOR':
        return 2
    if x == 'MEMBER':
        return 3
