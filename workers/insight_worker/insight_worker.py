#SPDX-License-Identifier: MIT
from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests, sys
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, and_
import statistics, logging, os, json, time
import numpy as np
import scipy.stats
import datetime
from sklearn.ensemble import IsolationForest
from workers.worker_base import Worker
import warnings
warnings.filterwarnings('ignore')

class InsightWorker(Worker):
    """ Worker that detects anomalies on a select few of our metrics
    task: most recent task the broker added to the worker's queue
    child: current process of the queue being ran
    queue: queue of tasks to be fulfilled
    config: holds info like api keys, descriptions, and database connection strings
    """
    def __init__(self, config={}):

        worker_type = "insight_worker"

        given = [['git_url']]
        models = ['insights']

        data_tables = ['chaoss_metric_status', 'repo_insights', 'repo_insights_records']
        operations_tables = ['worker_history', 'worker_job']

        # Run the general worker initialization
        super().__init__(worker_type, config, given, models, data_tables, operations_tables)

        self.config.update({ 
            'api_host': self.augur_config.get_value('Server', 'host'),
            'api_port': self.augur_config.get_value('Server', 'port')
        })

        # These 3 are included in every tuple the worker inserts (data collection info)
        self.tool_source = 'Insight Worker'
        self.tool_version = '1.0.0'
        self.data_source = 'Augur API'

        self.refresh = True
        self.send_insights = True
        self.anomaly_days = self.config['anomaly_days']
        self.training_days = self.config['training_days']
        self.contamination = self.config['contamination']
        self.confidence = self.config['confidence_interval'] / 100
        self.metrics = self.config['metrics']
        
    def insights_model(self, entry_info, repo_id):

        logging.info("Discovering insights for task with entry info: {}\n".format(entry_info))

        """ Collect data """
        base_url = 'http://{}:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
            self.config['api_host'], self.config['api_port'], repo_id)
        
        # Dataframe to hold all endpoint results
        # Subtract configurable amount of time
        begin_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=self.training_days)
        index = pd.date_range(begin_date, periods=self.training_days, freq='D')
        df = pd.DataFrame(index=index)
        
        # Hit and discover insights for every endpoint we care about
        for endpoint, field in self.metrics.items():
            # Hit endpoint
            url = base_url + endpoint
            logging.info("Hitting endpoint: " + url + "\n")
            try:
                data = requests.get(url=url).json()
            except:
                data = json.loads(json.dumps(requests.get(url=url).text))

            if len(data) == 0:
                logging.info("Endpoint with url: {} returned an empty response. Moving on to next endpoint.\n".format(url))
                continue
                
            if 'date' not in data[0]:
                logging.info("Endpoint {} is not a timeseries, moving to next endpoint.\n".format(endpoint))
                continue
            
            metric_df = pd.DataFrame.from_records(data)
            metric_df.index = pd.to_datetime(metric_df['date'], utc=True).dt.date
            df = df.join(metric_df[field]).fillna(0)
            df.rename(columns={field: "{} - {}".format(endpoint, field)}, inplace=True)

        """ End collect endpoint data """

        # If none of the endpoints returned data
        if df.size == 0:
            logging.info("None of the provided endpoints provided data for this repository. Anomaly detection is 'done'.\n")
            self.register_task_completion(entry_info, repo_id, "insights")
            return

        """ Deletion of old insights """

        # Delete previous insights not in the anomaly_days param
        min_date = datetime.datetime.now() - datetime.timedelta(days=self.anomaly_days)
        logging.info("MIN DATE: {}\n".format(min_date))
        logging.info("Deleting out of date records ...\n")
        delete_record_SQL = s.sql.text("""
            DELETE 
                FROM
                    repo_insights_records
                WHERE
                    repo_id = :repo_id
                    AND ri_date < :min_date
        """)
        result = self.db.execute(delete_record_SQL, repo_id=repo_id, min_date=min_date)

        logging.info("Deleting out of date data points ...\n")
        delete_points_SQL = s.sql.text("""
            DELETE 
                FROM
                    repo_insights
                USING (
                    SELECT ri_metric, ri_field 
                    FROM (
                        SELECT * 
                        FROM repo_insights
                        WHERE ri_fresh = TRUE
                        AND repo_id = :repo_id
                        AND ri_date < :min_date
                    ) old_insights
                ) to_delete
                WHERE repo_insights.ri_metric = to_delete.ri_metric
                AND repo_insights.ri_field = to_delete.ri_field
        """)
        result = self.db.execute(delete_points_SQL, repo_id=repo_id, min_date=min_date)

        # get table values to check for dupes later on
        insight_table_values = self.get_table_values(['*'], ['repo_insights_records'], where_clause="WHERE repo_id = {}".format(repo_id))

        to_model_columns = df.columns[0:len(self.metrics)+1]

        model = IsolationForest(n_estimators=100, max_samples='auto', contamination=float(self.contamination), \
                        max_features=1.0, bootstrap=False, n_jobs=-1, random_state=32, verbose=0)
        model.fit(df[to_model_columns])

        def classify_anomalies(df,metric):
            df = df.sort_values(by='date_col', ascending=False)
            
            # Shift metric values by one date to find the percentage chage between current and previous data point
            df['shift'] = df[metric].shift(-1)
            df['percentage_change'] = ((df[metric] - df['shift']) / df[metric]) * 100
            
            # Categorise anomalies as 0 - no anomaly, 1 - low anomaly , 2 - high anomaly
            df['anomaly_class'].loc[df['anomaly_class'] == 1] = 0
            df['anomaly_class'].loc[(df['anomaly_class'] == -1) & (df[metric] != 0) & (df[metric] != 1)] = 2
            max_anomaly_score = df['score'].loc[df['anomaly_class'] == 2].max()
            medium_percentile = df['score'].quantile(0.24)
            df['anomaly_class'].loc[(df['score'] > max_anomaly_score) & (df['score'] <= medium_percentile)] = 1
            return df

        for i, metric in enumerate(to_model_columns):

            # Fit the model to the data returned from the endpoints
            model.fit(df.iloc[:,i:i+1])
            pred = model.predict(df.iloc[:,i:i+1])

            # Create df and adopt previous index from when we called the endpoints
            anomaly_df = pd.DataFrame()
            anomaly_df['date_col'] = df.index
            anomaly_df.index = df.index
            
            # Find decision function to find the score and classify anomalies
            anomaly_df['score'] = model.decision_function(df.iloc[:,i:i+1])
            anomaly_df[metric] = df.iloc[:,i:i+1]
            anomaly_df['anomaly_class'] = pred

            # Get the indexes of outliers in order to compare the metrics with use case anomalies if required
            outliers = anomaly_df.loc[anomaly_df['anomaly_class'] == -1]
            outlier_index = list(outliers.index)
            anomaly_df = classify_anomalies(anomaly_df,metric)

            # Filter the anomaly_df by days we want to detect anomalies
            begin_detection_date = datetime.datetime.now() - datetime.timedelta(days=self.anomaly_days)
            detection_tuples = anomaly_df.index > begin_detection_date
            anomaly_df = anomaly_df.loc[detection_tuples]

            # Make a copy of the df for logging of individual tuples in the repo_insights table
            anomaly_df_copy = anomaly_df.copy()

            # Calculate mean
            mean = anomaly_df[metric].mean()

            # Make columns numeric for argmax to function properly
            for col in anomaly_df.columns:
                anomaly_df[col] = pd.to_numeric(anomaly_df[col])

            # Split into endpoint and field name
            split = metric.split(" - ")

            most_recent_anomaly_date = None
            most_recent_anomaly = None

            insight_count = 0

            while True:

                if anomaly_df.loc[anomaly_df['anomaly_class'] == 2].empty:
                    logging.info("No more anomalies to be found for metric: {}\n".format(metric))
                    break

                next_recent_anomaly_date = anomaly_df.loc[anomaly_df['anomaly_class'] == 2]['anomaly_class'].idxmax()
                logging.info("Next most recent date: \n{}\n".format(next_recent_anomaly_date))
                next_recent_anomaly = anomaly_df.loc[anomaly_df.index == next_recent_anomaly_date]
                logging.info("Next most recent anomaly: \n{}\n{}\n".format(next_recent_anomaly.columns.values, 
                    next_recent_anomaly.values))

                if insight_count == 0:
                    most_recent_anomaly_date = next_recent_anomaly_date
                    most_recent_anomaly = next_recent_anomaly

                # Format numpy 64 date into timestamp
                date64 = next_recent_anomaly.index.values[0]
                ts = (date64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                ts = datetime.datetime.utcfromtimestamp(ts)

                insight_exists = ((insight_table_values['ri_date'] == ts) & \
                    (insight_table_values['ri_metric'] == split[0]) & (insight_table_values['ri_field'] == split[1])).any()

                if not insight_exists:

                    # Insert record in records table and send record to slack bot
                    record = {
                        'repo_id': repo_id,
                        'ri_metric': split[0],
                        'ri_field': split[1],
                        'ri_value': next_recent_anomaly.iloc[0][metric],
                        'ri_date': ts,
                        'ri_score': next_recent_anomaly.iloc[0]['score'],
                        'ri_detection_method': 'Isolation Forest',
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source
                    }
                    result = self.db.execute(self.repo_insights_records_table.insert().values(record))
                    logging.info("Primary key inserted into the repo_insights_records table: {}\n".format(
                        result.inserted_primary_key))
                    self.results_counter += 1

                    # Send insight to Jonah for slack bot
                    self.send_insight(record, abs(next_recent_anomaly.iloc[0][metric] - mean))

                    insight_count += 1
                else:
                    logging.info("Duplicate insight found, skipping insertion. "
                        "Continuing iteration of anomalies...\n")

                anomaly_df = anomaly_df[anomaly_df.index < next_recent_anomaly_date]


            # If no insights for this metric were found, then move onto next metric
            # (since there is no need to insert the endpoint results below)
            if insight_count == 0:
                continue

            # Begin inserting to table to build frontend charts
            for tuple in anomaly_df_copy.itertuples():
                try:
                    # Format numpy 64 date into timestamp
                    date64 = tuple.Index
                    ts = (date64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                    ts = datetime.datetime.utcfromtimestamp(ts)

                    data_point = {
                        'repo_id': repo_id,
                        'ri_metric': split[0],
                        'ri_field': split[1],
                        'ri_value': tuple._3,
                        'ri_date': ts,
                        'ri_fresh': 0 if date64 < most_recent_anomaly_date else 1,
                        'ri_score': most_recent_anomaly.iloc[0]['score'],
                        'ri_detection_method': 'Isolation Forest',
                        "tool_source": self.tool_source,
                        "tool_version": self.tool_version,
                        "data_source": self.data_source
                    }
                    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
                    logging.info("Primary key inserted into the repo_insights table: {}\n".format(
                        result.inserted_primary_key))

                    logging.info("Inserted data point for metric: {}, date: {}, value: {}\n".format(metric, ts, tuple._3))
                except Exception as e:
                    logging.info("error occurred while storing datapoint: {}\n".format(repr(e)))
                    break

        self.register_task_completion(entry_info, repo_id, "insights")
        
    def confidence_interval_insights(self, entry_info):
        """ Anomaly detection method based on confidence intervals
        """

        # Update table of endpoints before we query them all
        logging.info("Discovering insights for task with entry info: {}".format(entry_info))

        # Set the endpoints we want to discover insights for
        endpoints = [{'cm_info': "issues-new"}, {'cm_info': "code-changes"}, {'cm_info': "code-changes-lines"}, 
            {'cm_info': 'reviews'}]

        """"""

        """ For when we want all endpoints """

        # """ Query all endpoints """
        # endpointSQL = s.sql.text("""
        #     SELECT * FROM chaoss_metric_status WHERE cm_source = 'augur_db'
        #     """)
        # for endpoint in pd.read_sql(endpointSQL, self.db, params={}).to_records():
        #     endpoints.append(endpoint)

        """"""

        # If we are discovering insights for a group vs repo, the base url will change
        if 'repo_group_id' in entry_info and 'repo_id' not in entry_info:
            base_url = 'http://{}:{}/api/unstable/repo-groups/{}/'.format(
                self.config['api_host'],self.config['api_port'], entry_info['repo_group_id'])
        else:
            base_url = 'http://{}:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
                self.config['api_host'],self.config['api_port'], repo_id)

        # Hit and discover insights for every endpoint we care about
        for endpoint in endpoints:

            # Hit endpoint
            url = base_url + endpoint['cm_info']
            logging.info("Hitting endpoint: " + url + "\n")
            r = requests.get(url=url)
            data = r.json()

            def is_unique_key(key):
                """ Helper method used to find which keys we want to analyze in each data point """
                return 'date' not in key and key != 'repo_group_id' and key != 'repo_id' and (
                    key != 'repo_name') and key != 'rg_name'
            
            # Filter out keys that we do not want to analyze (e.g. repo_id)
            raw_values = {}
            unique_keys = None
            if len(data) > 0:
                try:
                    unique_keys = list(filter(is_unique_key, data[0].keys()))
                except Exception as e:
                    logging.info("Length bigger than 0 but cannot get 0th element? : {}, {}".format(data, e))
            else:
                logging.info("Endpoint with url: {} returned an empty response. Moving on to next endpoint.\n".format(url))
                continue

            # num issues, issue comments, num commits, num pr, comments pr
            logging.info("Found the following unique keys for this endpoint: {}".format(unique_keys))
            date_filtered_data = []
            i = 0
            not_timeseries = False
            begin_date = datetime.datetime.now()

            # Subtract configurable amount of time
            begin_date = begin_date - datetime.timedelta(days=self.training_days)
            begin_date = begin_date.strftime('%Y-%m-%d')
            for dict in data:
                try:
                    if dict['date'] > begin_date:
                        date_filtered_data = data[i:]
                        logging.info("data {} days ago date found: {}, {}".format(self.training_days, dict['date'], begin_date))
                        break
                except:
                    logging.info("Endpoint {} is not a timeseries, moving to next".format(endpoint))
                    not_timeseries = True
                    break
                i += 1
            if not_timeseries:
                continue

            date_found_index = None
            date_found = False
            x = 0
            
            begin_date = datetime.datetime.now() - datetime.timedelta(days=self.anomaly_days)
            for dict in date_filtered_data:
                dict_date = datetime.datetime.strptime(dict['date'], '%Y-%m-%dT%H:%M:%S.%fZ')#2018-08-20T00:00:00.000Z
                if dict_date > begin_date and not date_found:
                    date_found = True
                    date_found_index = x
                    logging.info("raw values within {} days ago date found: {}, {}".format(self.anomaly_days, dict['date'], begin_date))
                x += 1
                for key in unique_keys:
                    try:
                        trash = int(dict[key]) * 2 + 1
                        raw_values[key].append(int(dict[key]))
                    except:
                        try:
                            trash = int(dict[key]) * 2 + 1
                            raw_values[key] = [int(dict[key])]
                        except:
                            logging.info("Key: {} is non-numerical, moving to next key.".format(key))

            for key in raw_values.keys():
                if len(raw_values[key]) > 0:
                    mean, lower, upper = self.confidence_interval(raw_values[key], confidence=self.confidence)
                    logging.info("Upper: {}, middle: {}, lower: {}".format(upper, mean, lower))
                    i = 0
                    discovery_index = None
                    insight = False
                    max_difference = 0
                    score = 0

                    date_filtered_raw_values = []
                    date_filtered_raw_values = date_filtered_data[date_found_index:]
                    logging.info("Raw values: {}".format(date_filtered_raw_values))
                    for dict in date_filtered_raw_values:
                        if (dict[key] > upper and dict[key] - upper > max_difference) or (dict[key] < lower and lower - dict[key] > max_difference):
                            logging.info("Band breached at {}. Marking discovery. dict: {}, key: {}, mean: {}".format(i, dict, key, mean))
                            max_difference = max(dict[key] - upper,lower - dict[key])
                            score = abs(dict[key] - mean) / mean * 100
                            insight = True
                            discovery_index = i
                        i += 1
                    if insight and 'date' in data[0]:

                        ### INSIGHT DISCOVERED ###

                        # Check if new insight has a better score than other insights in its place, use result
                        #   to determine if we continue in the insertion process (0 for no insertion, 1 for record
                        #   insertion, 2 for record and insight data points insertion)
                        instructions = self.clear_insight(repo_id, score, endpoint['cm_info'], key)
                        # self.clear_insight(repo_id, score, endpoint['cm_info'] + ' ({})'.format(key))

                        # Use result from clearing function to determine if we need to insert the record
                        if instructions['record']:

                            # Insert record in records table and send record to slack bot
                            record = {
                                'repo_id': int(repo_id),
                                'ri_metric': endpoint['cm_info'],
                                'ri_field': key,
                                'ri_value': date_filtered_raw_values[discovery_index][key],#date_filtered_raw_values[j][key],
                                'ri_date': date_filtered_raw_values[discovery_index]['date'],#date_filtered_raw_values[j]['date'],
                                'ri_score': score,
                                'ri_detection_method': '{} confidence interval'.format(self.confidence),
                                "tool_source": self.tool_source,
                                "tool_version": self.tool_version,
                                "data_source": self.data_source
                            }
                            result = self.db.execute(self.repo_insights_records_table.insert().values(record))
                            logging.info("Primary key inserted into the repo_insights_records table: {}".format(result.inserted_primary_key))
                            self.results_counter += 1
                            # Send insight to Jonah for slack bot
                            self.send_insight(record, abs(date_filtered_raw_values[discovery_index][key] - mean))

                        # Use result from clearing function to determine if we still need to insert the insight
                        if instructions['insight']:

                            j = 0
                            logging.info("Starting j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                            for tuple in date_filtered_raw_values:
                                try:
                                    data_point = {
                                        'repo_id': int(repo_id),
                                        'ri_metric': endpoint['cm_info'],
                                        'ri_field': key,
                                        'ri_value': tuple[key],#date_filtered_raw_values[j][key],
                                        'ri_date': tuple['date'],#date_filtered_raw_values[j]['date'],
                                        'ri_fresh': 0 if j < discovery_index else 1,
                                        'ri_score': score,
                                        'ri_detection_method': '{} confidence interval'.format(self.confidence),
                                        "tool_source": self.tool_source,
                                        "tool_version": self.tool_version,
                                        "data_source": self.data_source
                                    }
                                    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
                                    logging.info("Primary key inserted into the repo_insights table: " + str(result.inserted_primary_key))

                                    logging.info("Inserted data point for endpoint: {}\n".format(endpoint['cm_info']))
                                    j += 1
                                    logging.info("incremented j: {}, discovery_index: {}, data: {}".format(j, discovery_index, date_filtered_data[j]))
                                except Exception as e:
                                    logging.info("error occurred while storing datapoint: {}".format(repr(e)))
                                    break
                else:
                    logging.info("Key: {} has empty raw_values, should not have key here".format(key))

        self.register_task_completion(entry_info, "insights")

    def send_insight(self, insight, units_from_mean):
        try:
            repoSQL = s.sql.text("""
                SELECT repo_git, rg_name 
                FROM repo, repo_groups
                WHERE repo_id = {}
            """.format(insight['repo_id']))

            repo = pd.read_sql(repoSQL, self.db, params={}).iloc[0]
            
            begin_date = datetime.datetime.now() - datetime.timedelta(days=self.anomaly_days)
            dict_date = insight['ri_date'].strftime("%Y-%m-%d %H:%M:%S")
            if insight['ri_date'] > begin_date and self.send_insights:
                logging.info("Insight less than {} days ago date found: {}\n\nSending to Jonah...".format(self.anomaly_days, insight))
                to_send = {
                    'insight': True,
                    # 'rg_name': repo['rg_name'],
                    'repo_git': repo['repo_git'],
                    'value': insight['ri_value'], # y-value of data point that is the anomaly
                    'date': dict_date, # date of data point that is the anomaly
                    'field': insight['ri_field'], # name of the field from the endpoint that the anomaly was detected on
                    'metric': insight['ri_metric'], # name of the metric the anomaly was detected on
                    'units_from_mean': units_from_mean,
                    'detection_method': insight['ri_detection_method']
                }
                requests.post('https://ejmoq97307.execute-api.us-east-1.amazonaws.com/dev/insight-event', json=to_send)
        except Exception as e:
            logging.info("sending insight to jonah failed: {}".format(e))

    def clear_insights(self, repo_id, new_endpoint, new_field):

        logging.info("Deleting all tuples in repo_insights_records table with info: "
            "repo {} endpoint {} field {}".format(repo_id, new_endpoint, new_field))
        deleteSQL = """
            DELETE 
                FROM
                    repo_insights_records I
                WHERE
                    repo_id = {}
                    AND ri_metric = '{}'
                    AND ri_field = '{}'
        """.format(repo_id, new_endpoint, new_field)
        try:
            result = self.db.execute(deleteSQL)
        except Exception as e:
            logging.info("Error occured deleting insight slot: {}".format(e))

        # Delete all insights 
        logging.info("Deleting all tuples in repo_insights table with info: "
            "repo {} endpoint {} field {}".format(repo_id, new_endpoint, new_field))        
        deleteSQL = """
            DELETE 
                FROM
                    repo_insights I
                WHERE
                    repo_id = {}
                    AND ri_metric = '{}'
                    AND ri_field = '{}'
        """.format(repo_id, new_endpoint, new_field)
        try:
            result = self.db.execute(deleteSQL)
        except Exception as e:
            logging.info("Error occured deleting insight slot: {}".format(e))

    def clear_insight(self, repo_id, new_score, new_metric, new_field):
        logging.info("Checking if insight slots filled...")

        # Dict that will be returned that instructs the rest of the worker where the insight insertion is 
        #   needed (determined by if this new insights score is higher than already stored ones)
        insertion_directions = {'record': False, 'insight': False}

        # Query current record for this
        recordSQL = s.sql.text("""
            SELECT ri_metric, repo_id, ri_score, ri_field
            FROM repo_insights_records
            WHERE repo_id = {}
            AND ri_metric = '{}'
            AND ri_field = '{}'
            ORDER BY ri_score DESC
        """.format(repo_id, new_metric, new_field))
        rec = json.loads(pd.read_sql(recordSQL, self.db, params={}).to_json(orient='records'))
        logging.info("recordsql: {}, \n{}".format(recordSQL, rec))
        # If new score is higher, continue with deletion
        if len(rec) > 0:
            if new_score > rec[0]['ri_score'] or self.refresh:
                insertion_directions['record'] = True
                for record in rec:
                    logging.info("Refresh is on or Insight record found with a greater score than current slot filled for "
                        "repo {} metric {} new score {}, old score {}".format(repo_id, record['ri_metric'], new_score, record['ri_score']))
                    deleteSQL = """
                        DELETE 
                            FROM
                                repo_insights_records I
                            WHERE
                                repo_id = {}
                                AND ri_metric = '{}'
                                AND ri_field = '{}'
                    """.format(record['repo_id'], record['ri_metric'], record['ri_field'])
                    try:
                        result = self.db.execute(deleteSQL)
                    except Exception as e:
                        logging.info("Error occured deleting insight slot: {}".format(e))
        else:
            insertion_directions['record'] = True

        # Query current insights and rank by score
        num_insights_per_repo = 2
        insightSQL = s.sql.text("""
            SELECT distinct(ri_metric),repo_id, ri_score
            FROM repo_insights
            WHERE repo_id = {}
            ORDER BY ri_score ASC
        """.format(repo_id))
        ins = json.loads(pd.read_sql(insightSQL, self.db, params={}).to_json(orient='records'))
        logging.info("This repos insights: {}".format(ins))

        # Determine if inisghts need to be deleted based on if there are more insights than we want stored,
        #   or if the current insights have a lower score
        num_insights = len(ins)
        to_delete = []
        for insight in ins:
            insight['ri_score'] = insight['ri_score'] if insight['ri_score'] else 0.0
            logging.info("{}, {}, {}, {}".format(insight['ri_metric'], new_metric, insight['ri_score'], num_insights_per_repo))
            if (insight['ri_score'] < new_score and num_insights >= num_insights_per_repo) or num_insights > num_insights_per_repo or (insight['ri_metric'] == new_metric and self.refresh):
                num_insights -= 1
                to_delete.append(insight)
                logging.info("condition met, new len: {}, insight score: {}, new_score: {}".format(num_insights,
                    insight['ri_score'], new_score))

        # After psuedo-deletion, determine if insertion of the new insight is needed
        if num_insights < num_insights_per_repo:
            insertion_directions['insight'] = True

        # Delete all insights marked for deletion
        for insight in to_delete:
            logging.info("insight found with a greater score than current slots filled for repo {} new score {}, old score {}".format(repo_id, new_score, insight['ri_score']))
            deleteSQL = """
                DELETE 
                    FROM
                        repo_insights I
                    WHERE
                        repo_id = {}
                        AND ri_metric = '{}'
            """.format(insight['repo_id'], insight['ri_metric'])
            try:
                result = self.db.execute(deleteSQL)
            except Exception as e:
                logging.info("Error occured deleting insight slot: {}".format(e))
        
        return insertion_directions


    def confidence_interval(self, data, timeperiod='week', confidence=.95):
        """ Method to find high activity issues in the past specified timeperiod """
        a = 1.0 * np.array(data)
        logging.info("np array: {}".format(a))
        n = len(a)
        m, se = np.mean(a), scipy.stats.sem(a)
        logging.info("Mean: {}, standard error: {}".format(m, se))
        h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
        logging.info("H: {}".format(h))
        return m, m-h, m+h


    def update_metrics(self):
        logging.info("Preparing to update metrics ...\n\n" + 
            "Hitting endpoint: http://{}:{}/api/unstable/metrics/status ...\n".format(
            self.config['api_host'],self.config['api_port']))
        r = requests.get(url='http://{}:{}/api/unstable/metrics/status'.format(
            self.config['api_host'],self.config['api_port']))
        data = r.json()

        active_metrics = [metric for metric in data if metric['backend_status'] == 'implemented']

        # Duplicate checking ...
        need_insertion = self.filter_duplicates({'cm_api_endpoint_repo': "endpoint"}, ['chaoss_metric_status'], active_metrics)
        logging.info("Count of contributors needing insertion: " + str(len(need_insertion)) + "\n")

        for metric in need_insertion:

            tuple = {
                "cm_group": metric['group'],
                "cm_source": metric['data_source'],
                "cm_type": metric['metric_type'],
                "cm_backend_status": metric['backend_status'],
                "cm_frontend_status": metric['frontend_status'],
                "cm_defined": True if metric['is_defined'] == 'true' else False,
                "cm_api_endpoint_repo": metric['endpoint'],
                "cm_api_endpoint_rg": None,
                "cm_info": metric['display_name'],
                "cm_working_group": metric['group'],
                "cm_info": metric['tag'],
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": metric['data_source']
            }
            # Commit metric insertion to the chaoss metrics table
            result = self.db.execute(self.chaoss_metric_status_table.insert().values(tuple))
            logging.info("Primary key inserted into the metrics table: " + str(result.inserted_primary_key))
            self.results_counter += 1

            logging.info("Inserted metric: " + metric['display_name'] + "\n")

    def filter_duplicates(self, cols, tables, og_data):
        need_insertion = []

        table_str = tables[0]
        del tables[0]
        for table in tables:
            table_str += ", " + table
        for col in cols.keys():
            colSQL = s.sql.text("""
                SELECT {} FROM {}
                """.format(col, table_str))
            values = pd.read_sql(colSQL, self.db, params={})

            for obj in og_data:
                if values.isin([obj[cols[col]]]).any().any():
                    logging.info("value of tuple exists: " + str(obj[cols[col]]) + "\n")
                elif obj not in need_insertion:
                    need_insertion.append(obj)
        logging.info("While filtering duplicates, we reduced the data size from " + str(len(og_data)) + 
            " to " + str(len(need_insertion)) + "\n")
        return need_insertion

