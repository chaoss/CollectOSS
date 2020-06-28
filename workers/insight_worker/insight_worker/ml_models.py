
import pandas as pd
import requests
import datetime
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler

import logging



def next_ml_model(self,entry_info,repo_id,df):
    logging.info("Pratik its working")
    '''outliers_fraction = 0.01
    df_repo = df.copy()
    model =  IsolationForest(contamination=outliers_fraction)
    model.fit(df)

    df_repo['anomaly'] = pd.Series(model.predict(df))#adding new column with anomaly values to main dataframe
    
    anomaly_df = df_repo.loc[df_repo['anomaly'] == -1]


    insight_count = 0
    next_recent_anomaly_date = anomaly_df.idxmax()
    logging.info("Next most recent date: \n{}\n".format(next_recent_anomaly_date))
    next_recent_anomaly = anomaly_df.loc[anomaly_df.index == next_recent_anomaly_date]
    logging.info("Next most recent anomaly: \n{}\n{}\n".format(next_recent_anomaly.columns.values, 
            next_recent_anomaly.values))

    if insight_count == 0:
        most_recent_anomaly_date = next_recent_anomaly_date
        most_recent_anomaly = next_recent_anomaly

    split = df.columns.split(" - ")

    for tuple in anomaly_df.itertuples():
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
                'ri_score': most_recent_anomaly.iloc[0]['anomaly'],
                'ri_detection_method': 'isolation_forest_pratik',
                "tool_source": self.tool_source,
                "tool_version": self.tool_version,
                "data_source": self.data_source
            }
            result = self.db.execute(self.repo_insights_table.insert().values(data_point))
            logging.info("Primary key inserted into the repo_insights table: {}\n".format(
                result.inserted_primary_key))

            logging.info("Inserted data point for metric: {}, date: {}, value: {}\n".format(self.metric, ts, tuple._3))
        except Exception as e:
            logging.info("error occurred while storing datapoint: {}\n".format(repr(e)))
            break

        

    data_point = {
            'repo_id': repo_id,
            'ri_metric': 'issues-new',
            'ri_field': 'issues',
            'ri_value': 1,
            'ri_date': datetime.datetime.now(),
            'ri_fresh': 0,
            'ri_score': 2,
            'ri_detection_method': 'isolation_forest_pratik',
            "tool_source": self.tool_source,
            "tool_version": self.tool_version,
            "data_source": self.data_source
        }
    result = self.db.execute(self.repo_insights_table.insert().values(data_point))
    logging.info("Primary key inserted into the repo_insights table: {}\n".format(
        result.inserted_primary_key))

    '''
    logging.info(df)
    