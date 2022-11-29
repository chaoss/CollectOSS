import datetime
import logging
import os
import numpy as np
import pandas as pd
import requests
import sqlalchemy as s
from skimage.filters import threshold_otsu
from sklearn.ensemble import IsolationForest

from augur.tasks.data_analysis.message_insights.message_novelty import novelty_analysis
from augur.tasks.data_analysis.message_insights.message_sentiment import get_senti_score

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo, MessageAnalysis, MessageAnalysisSummary
from augur.application.db.engine import create_database_engine
from augur.application.db.util import execute_session_query

#SPDX-License-Identifier: MIT

ROOT_AUGUR_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

@celery.task
def message_insight_model(repo_git: str) -> None:

    logger = logging.getLogger(message_insight_model.__name__)

    full_train = True
    begin_date = ''

    tool_source = 'Message Insights Worker'
    tool_version = '0.3.1'
    data_source = 'Non-existent API'

    now = datetime.datetime.utcnow()
    run_id = int(now.timestamp())+5

    with DatabaseSession(logger) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

        models_dir = os.path.join(ROOT_AUGUR_DIRECTORY, "tasks", "data_analysis", "message_insights", session.config.get_value("Message_Insights", 'models_dir'))
        insight_days = session.config.get_value("Message_Insights", 'insight_days')

    # Any initial database instructions, like finding the last tuple inserted or generate the next ID value

    # Check to see if repo has been analyzed previously
    repo_exists_SQL = s.sql.text("""
        SELECT exists (SELECT 1 FROM augur_data.message_analysis_summary WHERE repo_id = :repo_id LIMIT 1)""")

    df_rep = pd.read_sql_query(repo_exists_SQL, create_database_engine(), params={'repo_id': repo_id})
    #full_train = not(df_rep['exists'].iloc[0])
    logger.info(f'Full Train: {full_train}')

    # Collection and insertion of data happens here

    if not full_train:

        # Fetch the timestamp of last analyzed message for the repo
        past_SQL = s.sql.text("""
            select message_analysis.msg_id, message.msg_timestamp
            from augur_data.message_analysis 
            inner join augur_data.message on message.msg_id = message_analysis.msg_id
            inner join augur_data.pull_request_message_ref on message.msg_id = pull_request_message_ref.msg_id 
            inner join augur_data.pull_requests on pull_request_message_ref.pull_request_id = pull_requests.pull_request_id
            where message.repo_id = :repo_id
            UNION
            select message_analysis.msg_id, message.msg_timestamp
            from augur_data.message_analysis
            inner join augur_data.message on message.msg_id = message_analysis.msg_id
            inner join augur_data.issue_message_ref on message.msg_id = issue_message_ref.msg_id 
            inner join augur_data.issues on issue_message_ref.issue_id = issues.issue_id
            where message.repo_id = :repo_id
            """)

        df_past = pd.read_sql_query(past_SQL, create_database_engine(), params={'repo_id': repo_id})
        df_past['msg_timestamp'] = pd.to_datetime(df_past['msg_timestamp'])
        df_past = df_past.sort_values(by='msg_timestamp')
        logger.debug(f'{df_past} is df_past')
        begin_date = df_past['msg_timestamp'].iloc[-1]
        logger.debug(f'{begin_date}')

        # Assign new run_id for every run
        run_id = get_max_id('message_analysis', 'worker_run_id', logger)

        logger.info(f'Last analyzed msg_id of repo {repo_id} is {df_past["msg_id"].iloc[-1]}')
        logger.info(f'Fetching recent messages from {begin_date} of repo {repo_id}...\n')

        # Fetch only recent messages
        join_SQL = s.sql.text("""
            select message.msg_id, msg_timestamp,  msg_text from augur_data.message
            left outer join augur_data.pull_request_message_ref on message.msg_id = pull_request_message_ref.msg_id 
            left outer join augur_data.pull_requests on pull_request_message_ref.pull_request_id = pull_requests.pull_request_id
            where message.repo_id = :repo_id and msg_timestamp > :begin_date
            UNION
            select message.msg_id, msg_timestamp, msg_text from augur_data.message
            left outer join augur_data.issue_message_ref on message.msg_id = issue_message_ref.msg_id 
            left outer join augur_data.issues on issue_message_ref.issue_id = issues.issue_id
            where message.repo_id = :repo_id and msg_timestamp > :begin_date""")
    else:
        logger.info(f'Fetching all past messages of repo {repo_id}...')

        # Fetch all messages
        join_SQL = s.sql.text("""
            select message.msg_id, msg_timestamp,  msg_text from augur_data.message
            left outer join augur_data.pull_request_message_ref on message.msg_id = pull_request_message_ref.msg_id 
            left outer join augur_data.pull_requests on pull_request_message_ref.pull_request_id = pull_requests.pull_request_id
            where message.repo_id = :repo_id
            UNION
            select message.msg_id, msg_timestamp, msg_text from augur_data.message
            left outer join augur_data.issue_message_ref on message.msg_id = issue_message_ref.msg_id 
            left outer join augur_data.issues on issue_message_ref.issue_id = issues.issue_id
            where message.repo_id = :repo_id""")

    df_message = pd.read_sql_query(join_SQL, create_database_engine(), params={'repo_id': repo_id, 'begin_date': begin_date})

    logger.info(f'Messages dataframe dim: {df_message.shape}')
    logger.info(f'Value 1: {df_message.shape[0]}')

    if df_message.shape[0] > 10:
        # Sort the dataframe
        df_message['msg_timestamp'] = pd.to_datetime(df_message['msg_timestamp'])
        df_message = df_message.sort_values(by='msg_timestamp')

        # DEBUG:
        # df_message.to_csv(f'full_{repo_id}.csv',index=False)

        # Create the storage directory for trained models
        try:
            os.makedirs(models_dir, exist_ok=True)
            logger.info(f"Models storage directory is '{models_dir}'\n")
        except OSError:
            logger.error('Models storage directory could not be created \n')

        logger.info('Starting novelty detection...')
        threshold, df_message['rec_err'] = novelty_analysis(df_message, repo_id, models_dir, full_train)

        if not full_train:
            merge_SQL = s.sql.text("""
            select novelty_flag, reconstruction_error from augur_data.message_analysis
            left outer join augur_data.pull_request_message_ref on message_analysis.msg_id = pull_request_message_ref.msg_id 
            left outer join augur_data.pull_requests on pull_request_message_ref.pull_request_id = pull_requests.pull_request_id
            where pull_request_message_ref.repo_id = :repo_id
            UNION
            select novelty_flag, reconstruction_error from augur_data.message_analysis
            left outer join augur_data.issue_message_ref on message_analysis.msg_id = issue_message_ref.msg_id 
            left outer join augur_data.issues on issue_message_ref.issue_id = issues.issue_id
            where issue_message_ref.repo_id = :repo_id""")

            df_past = pd.read_sql_query(merge_SQL, create_database_engine(), params={'repo_id': repo_id})
            df_past = df_past.loc[df_past['novelty_flag'] == 0]
            rec_errors = df_past['reconstruction_error'].tolist()
            threshold = threshold_otsu(np.array(rec_errors))

        # Reset begin date for insight detection
        begin_date = datetime.datetime.combine(
            df_message['msg_timestamp'].iloc[-1] - datetime.timedelta(days=insight_days), datetime.time.min)
        logger.info(f'Begin date: {begin_date}\n')

        # Flagging novel messages
        logger.info(f'Threshold for novelty is: {threshold}')
        df_message['novel_label'] = df_message.apply(
            lambda x: 1 if x['rec_err'] > threshold and len(x['cleaned_msg_text']) > 10 else 0, axis=1)
        logger.info(f'Novel messages detection completed. Dataframe dim: {df_message.shape}\n')

        logger.info('Starting sentiment analysis...')
        df_message['senti_label'], df_message['sentiment_score'] = get_senti_score(df_message, 'msg_text',
                                                                                   models_dir, label=True,
                                                                                   logger=logger)
        logger.info(f'Sentiment analysis completed. Dataframe dim: {df_message.shape}\n')

        df_message = df_message[
            ['msg_id', 'msg_timestamp', 'sentiment_score', 'rec_err', 'senti_label', 'novel_label']]

        # DEBUG:
        # df_message.to_csv(f'{models_dir}/{repo_id}.csv',index=False)

        # Insertion of sentiment & uniqueness scores to message_analysis table
        logger.info('Begin message_analysis data insertion...')
        logger.info(f'{df_message.shape[0]} data records to be inserted')

        with DatabaseSession(logger) as session:

            for row in df_message.itertuples(index=False):
                try:
                    msg = {
                        "msg_id": row.msg_id,
                        "worker_run_id": run_id,
                        "sentiment_score": row.sentiment_score,
                        "reconstruction_error": row.rec_err,
                        "novelty_flag": row.novel_label,
                        "feedback_flag": None,
                        "tool_source": tool_source,
                        "tool_version": tool_version,
                        "data_source": data_source,
                    }

                    message_analysis_object = MessageAnalysis(**msg)
                    session.add(message_analysis_object)
                    session.commit()

                    # result = create_database_engine().execute(message_analysis_table.insert().values(msg))
                    logger.info(
                        f'Primary key inserted into the message_analysis table: {message_analysis_object.msg_analysis_id}')
                    # logger.info(
                    #     f'Inserted data point {results_counter} with msg_id {row.msg_id} and timestamp {row.msg_timestamp}')
                except Exception as e:
                    logger.error(f'Error occurred while storing datapoint {repr(e)}')
                    break

        logger.info('Data insertion completed\n')

        df_trend = df_message.copy()
        df_trend['date'] = pd.to_datetime(df_trend["msg_timestamp"])
        df_trend = df_trend.drop(['msg_timestamp'], axis=1)
        df_trend = df_trend.sort_values(by='date')

        logger.info('Started 1D groupings to get insights')
        # Fetch the insight values of most recent specified insight_days
        # grouping = pd.Grouper(key='date', freq='1D')
        # df_insight = df_trend.groupby(grouping)['senti_label']
        # df_insight = df_insight.value_counts()
        # df_insight = df_insight.unstack()

        df_insight = df_trend.groupby(pd.Grouper(key='date', freq='1D'))['senti_label'].apply(
            lambda x: x.value_counts()).unstack()

        # df_insight = df_trend.groupby(pd.Grouper(key='date', freq='1D'))['senti_label'].value_counts().unstack()
        df_insight = df_insight.fillna(0)
        df_insight['Total'] = df_insight.sum(axis=1)
        df_insight = df_insight[df_insight.index >= begin_date]
        df_insight = df_insight.rename(columns={-1: 'Negative', 0: 'Neutral', 1: 'Positive'})

        # sentiment insight
        sent_col = ['Positive', 'Negative', 'Neutral', 'Total']
        for col in sent_col:
            if col not in list(df_insight.columns.values):
                logger.info(f'{col} not found in datframe. Adjusting...')
                df_insight[col] = np.zeros(df_insight.shape[0])

        sentiment_insights = df_insight[list(df_insight.columns.values)].sum(axis=0).to_dict()

        df_insight = df_trend.groupby(pd.Grouper(key='date', freq='1D'))['novel_label'].apply(
            lambda x: x.value_counts()).unstack()

        # df_insight = df_trend.groupby(pd.Grouper(key='date', freq='1D'))['novel_label'].value_counts().unstack()
        df_insight = df_insight.fillna(0)
        df_insight = df_insight.rename(columns={0: 'Normal', 1: 'Novel'})
        df_insight = df_insight[df_insight.index >= begin_date]

        # novel insight
        novel_col = ['Normal', 'Novel']
        for col in novel_col:
            if col not in list(df_insight.columns.values):
                logger.info(f'{col} not found in datframe. Adjusting...')
                df_insight[col] = np.zeros(df_insight.shape[0])
        novelty_insights = df_insight[list(df_insight.columns.values)].sum(axis=0).to_dict()

        # Log the insights
        logger.info(
            f'Insights on most recent analysed period from {begin_date} among {sentiment_insights["Total"]} messages')
        logger.info(
            f'Detected {sentiment_insights["Positive"]} positive_sentiment & {sentiment_insights["Negative"]} negative_sentiment messages')
        logger.info(
            f'Positive sentiment: {sentiment_insights["Positive"] / sentiment_insights["Total"] * 100:.2f}% & Negative sentiment: {sentiment_insights["Negative"] / sentiment_insights["Total"] * 100:.2f}%')
        logger.info(f'Detected {novelty_insights["Novel"]} novel messages')
        logger.info(f'Novel messages: {novelty_insights["Novel"] / sentiment_insights["Total"] * 100:.2f}%\n')

        # Prepare data for repo level insertion
        logger.info('Started 15D groupings for summary')

        # Collecting positive and negative sentiment ratios with total messages
        df_senti = df_trend.groupby(pd.Grouper(key='date', freq='15D'))['senti_label'].apply(
            lambda x: x.value_counts()).unstack()

        # df_senti = df_trend.groupby(pd.Grouper(key='date', freq='15D'))['senti_label'].value_counts().unstack()
        df_senti = df_senti.fillna(0)
        df_senti['Total'] = df_senti.sum(axis=1)
        df_senti = df_senti.rename(columns={-1: 'Negative', 0: 'Neutral', 1: 'Positive'})
        for col in sent_col:
            if col not in list(df_senti.columns.values):
                logger.info(f'{col} not found in dataframe. Adjusting...')
                df_senti[col] = np.zeros(df_senti.shape[0])
        df_senti['PosR'] = df_senti['Positive'] / df_senti['Total']
        df_senti['NegR'] = df_senti['Negative'] / df_senti['Total']

        # Collecting novel messages
        df_uniq = df_trend.groupby(pd.Grouper(key='date', freq='15D'))['novel_label'].apply(
            lambda x: x.value_counts()).unstack()

        # df_uniq = df_trend.groupby(pd.Grouper(key='date', freq='15D'))['novel_label'].value_counts().unstack()
        df_uniq = df_uniq.fillna(0)
        df_uniq = df_uniq.rename(columns={0: 'Normal', 1: 'Novel'})
        for col in novel_col:
            if col not in list(df_uniq.columns.values):
                logger.info(f'{col} not found in dataframe. Adjusting...')
                df_uniq[col] = np.zeros(df_uniq.shape[0])

        # Merge the 2 dataframes
        df_trend = pd.merge(df_senti, df_uniq, how="inner", left_index=True, right_index=True)
        logger.info(f'Merge done. Dataframe dim: {df_trend.shape}')

        # DEBUG:
        # df_trend.to_csv('trend.csv')

        # Insertion of sentiment ratios & novel counts to repo level table
        logger.info('Begin repo wise insights insertion...')
        logger.info(f'{df_senti.shape[0]} data records to be inserted\n')
        for row in df_trend.itertuples():
            msg = {
                "repo_id": repo_id,
                "worker_run_id": run_id,
                "positive_ratio": row.PosR,
                "negative_ratio": row.NegR,
                "novel_count": row.Novel,
                "period": row.Index,
                "tool_source": tool_source,
                "tool_version": tool_version,
                "data_source": data_source
            }

            message_analysis_summary_object = MessageAnalysisSummary(**msg)
            session.add(message_analysis_summary_object)
            session.commit()

            # result = create_database_engine().execute(message_analysis_summary_table.insert().values(msg))
            logger.info(
                f'Primary key inserted into the message_analysis_summary table: {message_analysis_summary_object.msg_summary_id}')
            # logger.info(f'Inserted data point {results_counter} for insight_period {row.Index}')

        logger.info('Data insertion completed\n')

        message_analysis_query = s.sql.text("""
                                 SELECT period, positive_ratio, negative_ratio, novel_count 
                                 FROM message_analysis_summary 
                                 WHERE repo_id=:repo_id""")

        df_past = pd.read_sql_query(message_analysis_query, create_database_engine(), params={'repo_id': repo_id})

        # df_past = get_table_values(cols=['period', 'positive_ratio', 'negative_ratio', 'novel_count'],
        #                                 tables=['message_analysis_summary'],
        #                                 where_clause=f'where repo_id={repo_id}')
        df1 = df_past.copy()

        # Calculate deviation from mean for all metrics
        mean_vals = df_past[['positive_ratio', 'negative_ratio', 'novel_count']].iloc[:-1].mean(axis=0)
        # Attempted bug fix 10/28/2022
        df_past.fillna("nan")
        ##############################
        curr_pos, curr_neg, curr_novel = df_past[['positive_ratio', 'negative_ratio', 'novel_count']].iloc[-1]
        pos_shift = (curr_pos - mean_vals[0]) / mean_vals[0] * 100
        neg_shift = (curr_neg - mean_vals[1]) / mean_vals[1] * 100
        novel_shift = (curr_novel - mean_vals[2]) / mean_vals[2] * 100

        deviation_insights = {'Positive': pos_shift, 'Negative': neg_shift, 'Novel': novel_shift}

        # Log the insights
        logger.info(f'Deviation Insights for last analyzed period from {df_past["period"].iloc[-1]}')
        logger.info(f'Sentiment Insights- Positive: {pos_shift:.2f}% & Negative: {neg_shift:.2f}%')
        logger.info(f'Novelty Insights: {novel_shift:.2f}%\n')

        # Anomaly detection on sentiment ratio based on past trends
        features = ['positive_ratio', 'negative_ratio']
        logger.info('Starting Isolation Forest on sentiment trend ratios...')
        clf = IsolationForest(n_estimators=100, max_samples='auto', max_features=1.0, bootstrap=False, n_jobs=-1,
                              random_state=42, verbose=0)
        clf.fit(df1[features])
        pred = clf.predict(df1[features])
        df1['anomaly'] = pred
        anomaly_df = df1.loc[df1['anomaly'] == -1]
        anomaly_df = anomaly_df[anomaly_df['period'] >= begin_date]
        senti_anomaly_timestamps = anomaly_df['period'].to_list()

        # Log insights
        logger.info(f'Found {anomaly_df.shape[0]} anomalies from {begin_date}')
        logger.info('Displaying recent anomaly periods (if any)..')
        try:
            for i in range(len(senti_anomaly_timestamps)):
                senti_anomaly_timestamps[i] = senti_anomaly_timestamps[i].strftime("%Y-%m-%d %H:%M:%S")
                logger.info(f'Anomaly period {i + 1}: {senti_anomaly_timestamps[i]}')

        except Exception as e:
            logger.warning(e)
            logger.warning('No Anomalies detected in recent period!\n')

        insights = [sentiment_insights, novelty_insights, deviation_insights, senti_anomaly_timestamps]
        logger.info(f'Insights dict: {insights}')

        # Send insights to Auggie
        send_insight(repo_id, insights, logger)

    else:
        if df_message.empty:
            logger.warning('No new messages in tables to analyze!\n')
        else:
            logger.warning("Insufficient data to analyze")


def send_insight(repo_id, insights, logger):
    try:
        repoSQL = s.sql.text("""
            SELECT repo_git, rg_name 
            FROM repo, repo_groups
            WHERE repo_id = {}
        """.format(repo_id))

        repo = pd.read_sql(repoSQL, create_database_engine(), params={}).iloc[0]
        to_send = {
            'message_insight': True,
            'repo_git': repo['repo_git'],
            'insight_begin_date': begin_date.strftime("%Y-%m-%d %H:%M:%S"),
            # date from when insights are calculated
            'sentiment': insights[0],  # sentiment insight dict
            'novelty': insights[1],  # novelty insight dict
            'recent_deviation': insights[2],  # recent deviation insight dict
            'sentiment_anomaly_timestamps': insights[3]  # anomaly timestamps list from sentiment trend (if any)
        }
        requests.post('https://ejmoq97307.execute-api.us-east-1.amazonaws.com/dev/insight-event', json=to_send)
        logger.info("Sent insights to Auggie!\n")

    except Exception as e:
        logger.info("Sending insight to Auggie failed: {}\n".format(e))


def get_max_id(table, column, logger, default=25150):
    """ Gets the max value (usually used for id/pk's) of any Integer column
        of any table

    :param table: String, the table that consists of the column you want to
        query a max value for
    :param column: String, the column that you want to query the max value for
    :param logger: Logger, handles logging
    :param default: Integer, if there are no values in the
        specified column, the value of this parameter will be returned
    :return: Integer, the max value of the specified column/table
    """
    max_id_sql = s.sql.text("""
        SELECT max({0}.{1}) AS {1}
        FROM {0}
    """.format(table, column))
    db = create_database_engine()
    rs = pd.read_sql(max_id_sql, db, params={})
    if rs.iloc[0][column] is not None:
        max_id = int(rs.iloc[0][column]) + 1
        logger.info("Found max id for {} column in the {} table: {}\n".format(column, table, max_id))
    else:
        max_id = default
        logger.warning("Could not find max id for {} column in the {} table... " +
            "using default set to: {}\n".format(column, table, max_id))

    db.dispose()

    return max_id
