
import os
from sqlalchemy.dialects import postgresql as pg
import sqlalchemy as s
import pandas as pd
import json
import httpx
from sqlalchemy.inspection import inspect
import re
import time
import sys

sys.path.append("..")
from sqlalchemy.event import listen
from sqlalchemy.event import listens_for

from util.random_key_auth import RandomKeyAuth
from tasks.redis_init import redis_connection as redis
from augur_config import AugurConfig
# import psycopg2 
from augur_db.engine import engine

from augur_db.models import Platform
sys.path.pop()
#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: Test sql methods
class TaskSession(s.orm.Session):

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, logger):
        
        self.logger = logger
        self.engine = engine

        super().__init__(self.engine)
    
    def execute_sql(self, sql_text):
        connection = self.engine.connect()

        return connection.execute(sql_text)

    #TODO: Bulk upsert
    
    def insert_data(self, data: [dict], table, natural_keys: [str], return_columns: [str] = []) -> None:

        # print(f"Return columns: {return_columns}")
        
        if type(data) != list:
            
            # if a dict is passed to data then 
            # convert it to a list with one value
            if type(data) == dict:
                data = [data]
            
            else:
                self.logger.info("Data must be a list or a dict")
                return

        if len(data) == 0:
            # self.logger.info("Gave no data to insert, returning...")
            return

        if type(data[0]) != dict:
            self.logger.info("Must be list of dicts")
            return

        # creates list of arguments to tell sqlalchemy what columns to return after the data is inserted
        returning_args = []
        for column in return_columns:
            argument = getattr(table, column)
            returning_args.append(argument)

        # creates insert on table
        # that returns cols specificed in returning_args
        # and inserts the data specified in data
        # NOTE: if return_columns does not have an values this still works
        stmnt = pg.insert(table).returning(*returning_args).values(data)

        # create a dict that the on_conflict_do_update method requires to be able to map updates whenever there is a conflict. See sqlalchemy docs for more explanation and examples: https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#updating-using-the-excluded-insert-values
        setDict = {}
        for key in data[0].keys():
                setDict[key] = getattr(stmnt.excluded, key)
            
        stmnt = stmnt.on_conflict_do_update(
            #This might need to change
            index_elements=natural_keys,
            
            #Columns to be updated
            set_ = setDict
        )

        with self.engine.connect() as connection:

            # print(str(stmnt.compile(dialect=pg.dialect())))
            
                # if there is no data to return then it executes the insert the returns nothing
            if len(return_columns) == 0:

                # try:
                connection.execute(stmnt)
                return

                # except Exception as e:
                        
                #         def split_list(a_list):
                #             half = len(a_list)//2
                #             return a_list[:half], a_list[half:]

                #         # pr_url_list = []
                #         # for value in data:
                #         #     pr_url_list.append(value["pr_url"])

                #         # duplicates = set([x for x in pr_url_list if pr_url_list.count(x) > 1])
                        
                #         # print(f"DUPLICATES: {duplicates}. ERROR: {e}")
                #         # return_data_set = set()
                #         print("Error splitting the data into two pieces")
                #         print(f"Data length: {len(data)}")
                #         list_1, list_2 = split_list(data)
                #         self.insert_data(list_1, table, natural_keys, return_columns)
                #         self.insert_data(list_2, table, natural_keys, return_columns)
            
            # else it get the requested return columns and returns them as a list of dicts
            else:
                try:
                    return_data_tuples = connection.execute(stmnt).fetchall()
                     # converts the return data to a list of dicts
                    return_data = []
                    for data in return_data_tuples:
                        return_data.append(dict(data))

                    return return_data

                except ValueError as e:
                    print(f"ERROR: {e}")
                    data_keys = list(data[0].keys())

                    string_data_list = []
                    # loop through data with potential errors
                    for value in data:

                        string_data = {}
                        # find the fields that are strings for that data
                        for key in data_keys:

                            if type(value[key]) == str:
                                string_data[field] = value[field]

                        string_data_list.append(string_data)

                    for data in string_data_list:
                        print(f"Data: {data}\n\n")

                # except Exception as e:

                #     print(f"Exception is: {e}")
                    
                #     def split_list(a_list):
                #         half = len(a_list)//2
                #         return a_list[:half], a_list[half:]

                #     # pr_url_list = []
                #     # for value in data:
                #     #     pr_url_list.append(value["pr_url"])

                #     # duplicates = set([x for x in pr_url_list if pr_url_list.count(x) > 1])
                    
                #     # print(f"DUPLICATES: {duplicates}. ERROR: {e}")
                #     # return_data_set = set()
                #     self.logger.info("Error splitting the data into two pieces")
                #     self.logger.info(f"Data length: {len(data)}")
                #     list_1, list_2 = split_list(data)
                #     self.insert_data(list_1, table, natural_keys, return_columns)
                #     self.insert_data(list_2, table, natural_keys, return_columns)
                #         # return_data_set.add(return_column_data)

                #     # return_data_tuples = list(return_data_set)

                return_data = []
                for data in return_data_tuples:
                    return_data.append(dict(data))

                return return_data


                   

               

#TODO: Test sql methods
class GithubTaskSession(TaskSession):

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, logger, platform: str ='GitHub'):

        super().__init__(logger)

        config = AugurConfig(self)

        api_key = config.get_value("Keys", "github_api_key")

        keys = self.get_list_of_oauth_keys_from_db(self.engine, config.get_value("Keys", "github_api_key"))

        self.oauths = RandomKeyAuth(keys)

        self.platform_id = 1
        

    def get_list_of_oauth_keys_from_db(self, db_engine: s.engine.base.Engine, config_key: str) ->[str]:

        key_list_length = redis.llen("oauth_keys_list")

        if key_list_length > 0:
            keys = []
            for i in range(0, key_list_length):
                keys.append(redis.lindex("oauth_keys_list",i))
            return keys
        
        oauthSQL = s.sql.text(f"""
                SELECT access_token FROM augur_operations.worker_oauth WHERE access_token <> '{config_key}' and platform = 'github'
                """)

        oauth_keys_list = [{'access_token': config_key}] + json.loads(
            pd.read_sql(oauthSQL, db_engine, params={}).to_json(orient="records"))

        key_list = [x["access_token"] for x in oauth_keys_list]

        with httpx.Client() as client:

            # loop throuh each key in the list and get the rate_limit and seconds_to_reset
            # then add them either the fresh keys or depleted keys based on the rate_limit
            for key in key_list:

                key_data = self.get_oauth_key_data(client, key)

                # this makes sure that keys with bad credentials are not used
                if key_data is None:
                    key_list.remove(key)

        for key in key_list:
            # just in case the mulitprocessing adds extra values to the list.
            # we are clearing it before we push the values we got
            for i in range(0, redis.llen("oauth_keys_list")):
                redis.lpop("oauth_keys_list")

            redis.lpush("oauth_keys_list", key)

        return key_list


    def get_oauth_key_data(self, client: httpx.Client, oauth_key: str) -> None or True:

        # this endpoint allows us to check the rate limit, but it does not use one of our 5000 requests
        url = "https://api.github.com/rate_limit"

        headers = {'Authorization': f'token {oauth_key}'}

        response = client.request(
            method="GET", url=url, headers=headers, timeout=180)

        data = response.json()

        try:
            if data["message"] == "Bad credentials":
                return None
        except KeyError:
            pass

        return True
