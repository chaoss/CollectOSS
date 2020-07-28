from multiprocessing import Process, Queue
from urllib.parse import urlparse
import requests, sys
import pandas as pd
import sqlalchemy as s
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData, and_
import statistics, logging, os, json, time
import numpy as np
import datetime
from sklearn.ensemble import IsolationForest
from workers.worker_base import Worker
import warnings
import logging

import scipy
from scipy import stats
import pickle
from joblib import dump, load
import random
from functools import reduce
from keras.models import load_model
from keras.models import Sequential
from keras.layers import LSTM,Bidirectional,Activation
from keras import optimizers
from keras.layers import Dense,Dropout
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.cluster import AgglomerativeClustering,KMeans
from statsmodels.tsa.seasonal import STL



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

        data_tables = ['chaoss_metric_status', 'repo_insights', 'repo_insights_records','lstm_anomaly_models','lstm_anomaly_results']
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
        
    def IsolationForest_model(self, entry_info, repo_id):

        self.logger.info("Discovering insights for task with entry info: {}\n".format(entry_info))
        
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

    def insights_model(self, entry_info, repo_id):



        def lstm_selection(self,entry_info,repo_id,df):

            """ Selects window_size or time_steps by checking sparsity and
                coefficient of variation in data and pass into lstm_keras method
            """

            #Each column or field in metrics are passed for individual analysis
            for i in range(1,df.columns.shape[0]): 
                ddt = df.iloc[:,i][ (df.iloc[:,i]<np.percentile(df.iloc[:,i], 90))]
                ddt.dropna(axis=0,inplace=True)

                window_size=0
                if np.isnan(np.std(ddt)) or np.isnan(np.mean(ddt)) or np.mean(ddt)<0.01 or np.std(ddt)<0.01:
                    window_size = 3
                    
                else: 
                    # parameters defined in a way such that window size varies between 3-36 for better results
                    param = int(self.training_days/36)
                    non_zero_day = self.training_days- np.sum(df.iloc[:,4]==0)
                    window_size = int( (non_zero_day/param) - 3*(np.std(ddt)/np.mean(ddt)) )
                        

                if window_size<3:
                    window_size = 3

                lstm_keras(self,entry_info,repo_id,pd.DataFrame(df.iloc[:,[0,i]]),window_size)

        
        def preprocess_data(data,tr_days,lback_days,n_features,n_predays):
            
            """ Arrange training_data according to different parameters passed by lstm_keras method
            """
            
            train_data = data.values

            features_set = [] #For x values or time_step
            labels = [] # For y values or next_step
            for i in range(lback_days, tr_days+1):
                features_set.append(train_data[i-lback_days:i,0])
                labels.append(train_data[i:i+n_predays, 0])

            features_set = np.array(features_set)
            labels = np.array(labels)

            features_set = np.reshape(features_set, (features_set.shape[0], features_set.shape[1], n_features))

            
            return features_set,labels


        def model_lstm(features_set,n_predays,n_features):

            # Optimal model configuration to acheive best possible results for all kind of metrics

            model = Sequential()
            model.add(Bidirectional(LSTM(90, activation='linear',return_sequences=True, input_shape=(features_set.shape[1], n_features))))
            model.add(Dropout(0.2))
            model.add(Bidirectional(LSTM(90, activation='linear',return_sequences=True)))
            model.add(Dropout(0.2))
            model.add(Bidirectional(LSTM(90, activation='linear')))
            model.add(Dense(1))
            model.add(Activation('linear'))
            model.compile(optimizer='adam', loss='mae')
            return model
        


        def lstm_keras(self,entry_info,repo_id,df,window_size):

            """ Training and prediction of data, classification of anomalies,
                insertion of lstm_models and their results into the database table.
            """
            
            # Standard scaling of data
            scaler = StandardScaler()
            data = pd.DataFrame(df.iloc[:,1])
            data = pd.DataFrame(scaler.fit_transform(data.values))



            #tr_days : number of training days
            #lback_days : number of days to lookback for next prediction
            #n_features : number of features of columns in dataframe for training
            #n_predays : next number of days to predict
            
            lback_days = window_size
            tr_days = self.training_days -lback_days
            n_features = 1
            n_predays = 1

            # Training model with defined parameters
            features_set,labels = preprocess_data(data,tr_days,lback_days,n_features,n_predays)
            model = model_lstm(features_set,n_predays,n_features)
            history = model.fit(features_set, labels, epochs = 50, batch_size = lback_days,validation_split=0.1,verbose=0).history
            
            
            # Arranging data for predictions
            test_inputs = data[ :len(df.iloc[:,1])].values
            test_inputs = test_inputs.reshape(-1,n_features)
            test_features = []
            for i in range(lback_days, len(df.iloc[:,1])):
                test_features.append(test_inputs[i-lback_days:i, 0])

            test_features = np.array(test_features)
            test_features = np.reshape(test_features, (test_features.shape[0], test_features.shape[1], n_features))
            predictions = model.predict(test_features)
            predictions = scaler.inverse_transform(predictions)
            
            
            #Calculating error
            test_data = df.iloc[lback_days:,1]
            error = np.array(test_data[:]- predictions[:,0])            
            df['score'] = 0
            df.iloc[:lback_days,2] = df.iloc[:lback_days,1] - np.mean(df.iloc[:lback_days,1])
            df.iloc[lback_days:,2] = error
            
            # Classifying outliers
            df['anomaly_class'] = 0
            filt = df.iloc[:lback_days,2]>2*np.mean(df.iloc[:lback_days,2])
            df.iloc[:lback_days,:].loc[filt,'anomaly_class']=1
            
            
            # Classifying local outliers with value 1 using std and mean
            for i in range(lback_days,len(error)):
                filt = df.iloc[i-lback_days:i,3]==0
                std_error = np.std(abs(error[i-lback_days:i][filt]))
                mean = np.mean(abs(error[i-lback_days:i][filt]))

                if ((error[i]>3*std_error + mean) | (error[i]<-3*std_error - mean)):
                    df.iloc[i,3]=1

            # Classifying global outliers with value 2
            mean = np.mean(abs(df.iloc[:,2]))
            std_error = np.std(abs(df.iloc[:,2]))
            filt = (df.iloc[:,2]>3*std_error + mean) | (df.iloc[:,2]<-3*std_error - mean)
            df.iloc[:,3][filt] = 2

            # Defining anomaly dataframe for insetion into repo_insights,repo_insights_records table
            filt = df['anomaly_class']!=0
            begin_detection_date = datetime.datetime.now() - datetime.timedelta(days=self.anomaly_days)
            df['date'] = pd.to_datetime(df['date'])
            detection_tuples = df.date > begin_detection_date
            anomaly_df = df[filt].loc[detection_tuples]



            # Insertion of current model with selected parameters 
            # if already not present in the lstm_anomaly_models table
            model_name = 'BiLSTM'
            model_description = '3_layer_BiLSTM_90_units,linear_activation,mae_loss,adam_optimizer'
            look_back_days = lback_days
            training_days = self.training_days
            batch_size = lback_days
            model_table_values = self.get_table_values(['*'], ['lstm_anomaly_models'], where_clause="WHERE model_name = '{}'".format(model_name))
            model_exists =  ((model_table_values['model_name'] == '{}'.format(model_name)) & \
                (model_table_values['model_description'] == '{}'.format(model_description)) & \
                (model_table_values['look_back_days'] == lback_days) & (model_table_values['batch_size'] == lback_days)).any()
                            
            
            if not model_exists:
                self.logger.info("entered if")
                data_point = {
                    'model_name': '{}'.format(model_name),
                    'model_description': '{}'.format(model_description),
                    'look_back_days': lback_days,
                    'training_days': self.training_days,
                    'batch_size': batch_size,
                    'tool_source': self.tool_source,
                    'tool_version': self.tool_version,
                    'data_source': self.data_source
                }
                result = self.db.execute(self.lstm_anomaly_models_table.insert().values(data_point))
                self.logger.info("Primary key inserted into the lstm_anomaly_models table: {}\n".format(
                    result.inserted_primary_key))
                
            
            # query model_id of the current model to insert 
            # summary of results into the lstm_anomaly_results table
            query_text = s.sql.text("""
                SELECT model_id 
                FROM lstm_anomaly_models 
                WHERE model_name = '{}' 
                AND model_description = '{}'
                AND look_back_days = {} 
                AND batch_size = {}
                """.format(model_name,model_description,lback_days,lback_days))
            
            pri_key = pd.read_sql(query_text,self.db)#params={model_name = model_name , model_description = model_description,lback_days = lback_days,batch_size = batch_size}).iloc[0]  
            model_id = int(pri_key['model_id'].values)
            

            # defining prediction column into the dataframe 
            df['predictions'] = df.iloc[:,1] - df.iloc[:,2]
            metric = df.columns[1]
            split = metric.split(" _ ")
                
            # Classifying repo_category based on time_step or look_back_days    
            if lback_days<=10:
                repo_category = "less_active"
            elif lback_days<=20:
                repo_category = "moderate_active"
            else:
                repo_category = "highly_active"
                
            count = np.sum(df['anomaly_class']!=0)
            filt = df['anomaly_class'] ==0

            # insertion of results_summary into the lstm_anomaly_results table
            record = {
                'repo_id': repo_id,
                'repo_category': '{}'.format(repo_category),
                'model_id': model_id,
                'metric': split[0],
                'contamination_factor': count/self.training_days,
                'mean_absolute_error':np.mean(abs(df.iloc[:,2][filt])) , 
                'remarks': "ok",
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source,
                "metric_field": split[1],
                "mean_absolute_actual_value":np.mean(abs(df.iloc[:,1][filt])) ,
                "mean_absolute_prediction_value":np.mean(abs(df.iloc[:,4][filt])),
            
            }

            result = self.db.execute(self.lstm_anomaly_results_table.insert().values(record))
            self.logger.info("Primary key inserted into lstm_anomaly_results table: {}\n".format(
                result.inserted_primary_key))

            # If anomaly deiscovered in between the anomaly_days values then nsert it into the database
            if(len(anomaly_df)!=0):

                self.logger.info("Outliers found using lstm_keras model")
                insert_data(self,entry_info,repo_id,anomaly_df,'lstm_keras')
                
            else:
                
                self.logger.info("No outliers found using lstm_keras model")
              



        def insert_data(self,entry_info,repo_id,anomaly_df,model):

            """ Inserts outliers discovered by lstm_keras method into the 
                repo_insights and repo_insights_records table
            """

            # It inserts new outliers into the repo_insights table.
            anomaly_df_copy = anomaly_df.copy()
            self.logger.info("inserting data")
            metric = anomaly_df.columns[1]
            split = metric.split(" _ ")
            most_recent_anomaly_date = None
            most_recent_anomaly = None
            insight_table_values = self.get_table_values(['*'], ['repo_insights_records'], where_clause="WHERE repo_id = {}".format(repo_id))
            insight_count = 0

            while True:

                if anomaly_df.loc[anomaly_df['anomaly_class'] !=0].empty:
                    logging.info("No more anomalies to be found for metric: {}\n".format(metric))
                    break

                next_recent_anomaly_date = anomaly_df.loc[anomaly_df['anomaly_class'] !=0]['date'].max()
                self.logger.info("Next most recent date: \n{}\n".format(next_recent_anomaly_date))
                next_recent_anomaly = anomaly_df.loc[anomaly_df.date == next_recent_anomaly_date]
                self.logger.info("Next most recent anomaly: \n{}\n{}\n".format(next_recent_anomaly.columns.values, 
                    next_recent_anomaly.values))

                if insight_count == 0:
                    most_recent_anomaly_date = next_recent_anomaly_date
                    most_recent_anomaly = next_recent_anomaly

                # Format numpy 64 date into timestamp
                date64 = next_recent_anomaly.date.values[0]
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
                    self.send_insight(record, abs(next_recent_anomaly.iloc[0]['score']))

                    insight_count += 1
                else:
                    logging.info("Duplicate insight found, skipping insertion. "
                        "Continuing iteration of anomalies...\n")

                anomaly_df = anomaly_df[anomaly_df.date < next_recent_anomaly_date]

            # insert outliers into the repo_insights table
            for tuple in anomaly_df_copy.itertuples():
                try:
                    date64 = tuple.date
                    ts = (date64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
                    ts = datetime.datetime.utcfromtimestamp(ts)
                    
                    
                    
                    data_point = {
                            'repo_id': repo_id,
                            'ri_metric': split[0],
                            'ri_field': split[1],
                            'ri_value': tuple[2],
                            'ri_date': ts,
                            'ri_fresh': 0 if date64 < most_recent_anomaly_date else 1, 
                            'ri_score': tuple.score,
                            'ri_detection_method': '{}'.format(model),
                            "tool_source": self.tool_source,
                            "tool_version": self.tool_version,
                            "data_source": self.data_source
                        }
                    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
                    self.logger.info("Primary key inserted into the repo_insights table: {}\n".format(
                        result.inserted_primary_key))

                    self.logger.info("Inserted data point for metric: {}, date: {}, value: {}\n".format(metric, ts, tuple[2]))
                except Exception as e:
                    self.logger.info("error occurred while storing datapoint: {}\n".format(repr(e)))
                    break  
                    
        def time_series_metrics(self,entry_info,repo_id):

            """ Collects data of different metrics using API enpoints 
                Preproceess data and creates a dataframe with date and each and every fields as columns
            """

            

            training_days = self.training_days 
            base_url = 'http://{}:{}/api/unstable/repo-groups/9999/repos/{}/'.format(
            self.config['api_host'], self.config['api_port'], repo_id)
        
            begin_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=training_days)
            index = pd.date_range(begin_date, periods=training_days, freq='D')
            df = pd.DataFrame(index)
            df.columns = ['date']
            df['date'] = df['date'].astype(str)

            for endpoint in time_series:
                
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
                metric_df['date'] = pd.to_datetime(metric_df['date']).dt.date
                metric_df['date'] = metric_df['date'].astype(str)
                extra=['repo','rg']
                for column in metric_df.columns:
                    if any(x in column for x in extra):
                        metric_df.drop(column,axis=1,inplace=True)
                        
                df = pd.DataFrame(pd.merge(df,metric_df.loc[:,metric_df.columns],how = 'left',on = 'date'))
                metric_df.drop('date',axis=1,inplace=True)
                df.rename(columns={i :"{} _ {}".format(endpoint, i) for i in metric_df.columns }, inplace=True)

            df = df.fillna(0)
            
            self.logger.info("Collection and preprocessing of data of repo_id_{} Completed".format(repo_id))
            lstm_selection(self,entry_info,repo_id,df)

        def cluster_approach_one(self,entry_info,repo_id,df):
            
            """ One of clustering approach that can be used to
                classify repo_categories based on their activity
                Currently not in use
            """

            # Collecting data from prestored csv files for each columns c
            # ontaining data of over 1500+ repos to train clustering algorithm
            data = pd.read_csv("../../time_series_notebook/{}.csv".format(df.columns[1]))
            data.index = data.iloc[:,0]
            data.drop(['repo_id'],axis=1,inplace=True)

            scaler = MinMaxScaler()
            data_scaled = pd.DataFrame(scaler.fit_transform(data))
            data_scaled.index = data.index

            
            # Kmeans clustering
            cluster= KMeans(n_clusters=3, random_state=0).fit(data_scaled)
            x = cluster.labels_
            unique, counts = np.unique(x, return_counts=True)
            
            df_frame = pd.DataFrame(data.sum(axis=1))
            df_frame['cluster'] = x
            df_frame.columns = ['metric','cluster']
            
            clusters_means={}
            for k in unique:
                filt = df_frame['cluster'] == k
                df_frame[filt]['metric'].mean()
                
                clusters_means[k] = df_frame[filt]['metric'].mean()
                
            clusters_means = {ke: v for ke, v in sorted(clusters_means.items(), key=lambda item: item[1])}
            xp = [t for t in clusters_means.keys()]
            df_scaled = scaler.transform(pd.DataFrame(df.iloc[-365:,1]).T)
            
            pred = cluster.predict(df_scaled)
            
            
            self.logger.info("Clustering of field {} for repo_id {} is completed and it belongs to cluster {}".format(df.columns[1],repo_id,pred))
            
            if pred == xp[0]:
                #return 'less_active'
                return stl_less_active(self,entry_info,repo_id,df)
            elif pred == xp[1]:
                #return 'moderate_active'
                return lstm_moderate_active(self,entry_info,repo_id,df)
            else:
                #return 'highly_active'
                return lstm_highly_active(self,entry_info,repo_id,df)



        def cluster_approach_two(self,entry_info,repo_id,df):

            """ One of clustering approach that can be used to
                classify repo_categories based on their activity
                Currently not in use
            """

            # query issues,pull_request and their comments count 
            query_text = """
            SELECT
            r.repo_id,
            issue_count,
            pull_request_count,
            issue_comment_count,
            pull_request_comment_count
            FROM
            augur_data.repo r left outer join 
            ( SELECT repo_id, COUNT ( * ) AS issue_count FROM augur_data.issues GROUP BY repo_id ) i on r.repo_id = i.repo_id
            FULL OUTER JOIN ( SELECT repo_id, COUNT ( * ) AS pull_request_count FROM augur_data.pull_requests GROUP BY repo_id ) pr ON i.repo_id = pr.repo_id
            FULL OUTER JOIN (
            SELECT
                repo_id,
                COUNT ( * ) AS pull_request_comment_count 
            FROM
                augur_data.message
                M LEFT OUTER JOIN augur_data.pull_request_message_ref mr ON M.msg_id = mr.msg_id
                LEFT OUTER JOIN augur_data.pull_requests pr ON mr.pull_request_id = pr.pull_request_id 
            GROUP BY
                repo_id 
            ) prc ON i.repo_id = prc.repo_id
            FULL OUTER JOIN (
            SELECT
                repo_id,
                COUNT ( * ) AS issue_comment_count 
            FROM
                augur_data.message
                M LEFT OUTER JOIN augur_data.issue_message_ref mr ON M.msg_id = mr.msg_id
                LEFT OUTER JOIN augur_data.issues i ON mr.issue_id = i.issue_id 
            WHERE
                pull_request IS NULL 
            GROUP BY
            repo_id 
            ) ic ON i.repo_id = ic.repo_id
                """

            # train model based on data and store it in joblib file 
            # for the very first time when the worker starts

            if not os.path.isfile('./kmeans_cluster.joblib'):
                
                SQL_query_text = s.sql.text(query_text)
                df_cluster = pd.read_sql(SQL_query_text, self.db)
                
                df_cluster = df_cluster.fillna(0)
                df_cluster.index = df_cluster.iloc[:,0]
                if(len(df_cluster)>3053):
                    df_cluster = df_cluster.iloc[:3053,:]
                df_cluster.drop(['repo_id'],axis=1,inplace=True)
                
                kmeans = KMeans(n_clusters=3, random_state=0).fit(df_cluster)
                
                dump(kmeans, 'kmeans_cluster.joblib') 
                
    
    
    
            # if the joblib scripts already presents then predict repo_category based on pretrained model
            clf = load('kmeans_cluster.joblib')
            query_text_repo = query_text + "WHERE r.repo_id={}".format(repo_id)
            SQL_query_text = s.sql.text(query_text_repo)

            df_repo = pd.read_sql(SQL_query_text, self.db)
            df_repo = df_repo.fillna(0)
            df_repo.index = df_repo.iloc[:,0]
            df_repo.drop(['repo_id'],axis=1,inplace=True)

            pred = clf.predict(df_repo)

            # 0:less active
            # 1:highly active
            # 2:moderate active



            if pred[0] == 0:
                
                
                for i in range(1,df.columns.shape[0]):
                  
                    self.logger.info("Collection and preprocessing of data of {} field in cluster_0 Completed".format(df.columns[i]))
                    stl_less_active(self,entry_info,repo_id,df.iloc[:,[0,i]])
                    
            elif pred[0] == 2:
                

                for i in range(1,df.columns.shape[0]):
                    
                    self.logger.info("Collection and preprocessing of data of {} field in cluster_2 Completed".format(df.columns[i]))
                    lstm_moderate_active(self,entry_info,repo_id,pd.DataFrame(df.iloc[:,[0,i]]))
            else:
                
        
                for i in range(1,df.columns.shape[0]):

                    self.logger.info("Collection and preprocessing of data of {} field in cluster_1 Completed".format(df.columns[i]))
                    lstm_highly_active(self,entry_info,repo_id,pd.DataFrame(df.iloc[:,[0,i]]))


        # Initial calling of time_series_metrics to run the whole process of outlier detection
        time_series = ['code-changes-lines','issues-new','reviews']
        time_series_metrics(self,entry_info,repo_id)

        # Register task completeion when outlier detection method carried out successfully
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

