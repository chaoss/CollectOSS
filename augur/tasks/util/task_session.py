import os
from sqlalchemy.dialects import postgresql as pg
import sqlalchemy as s
import pandas as pd
import json
import httpx
from sqlalchemy.inspection import inspect
from psycopg2.errors import DeadlockDetected
from sqlalchemy.exc import OperationalError

import re
import time
import sys
import random

sys.path.append("..")
from sqlalchemy.event import listen
from sqlalchemy.event import listens_for

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.tasks.init.redis_connection import redis_connection as redis
from augur.application.config import AugurConfig
# import psycopg2 
from augur.application.db.engine import engine

from augur.application.db.models import Platform
sys.path.pop()
#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: Test sql methods
class TaskSession(s.orm.Session):

    task_num = 0

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, logger):
        
        self.logger = logger
        self.engine = engine
        self.task_name = f"TASK {TaskSession.task_num}"

        TaskSession.task_num +=1 

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


        # print(str(stmnt.compile(dialect=pg.dialect())))
        attempts = 0
        sleep_time_list = [x for x in range(1,11)]
        sleep_time = random.sample(sleep_time_list, k=1)[0]
        deadlock_detected = False
        # if there is no data to return then it executes the insert the returns nothing
        if len(return_columns) == 0:

            while attempts < 10:
                try:
                    with self.engine.connect() as connection:
                        connection.execute(stmnt)
                except OperationalError as e:
                    # print(str(e).split("Process")[1].split(";")[0])
                    if isinstance(e.orig, DeadlockDetected):
                        deadlock_detected = True
                        self.logger.debug(f"{self.task_name}: Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                        time.sleep(sleep_time)

                        attempts += 1
                        continue
                    else:
                        raise OperationalError(f"An OperationalError other than DeadlockDetected occurred: {e}") 

            else:
                self.logger.error(f"{self.task_name}: Unable to insert data in 10 attempts")
                return

            if deadlock_detected == True:
                self.logger.error(f"{self.task_name}: Made it through even though Deadlock was detected")
                    
            return
        
        # else it get the requested return columns and returns them as a list of dicts
        else:
            while attempts < 10:
                try:
                    with self.engine.connect() as connection:
                        return_data_tuples = connection.execute(stmnt).fetchall()
                    
                except OperationalError as e:
                    print(type(e.orig))
                    if isinstance(e.orig, DeadlockDetected):
                        self.logger.debug(f"{self.task_name}: Deadlock detected on {table.__table__} table...trying again")
                        time.sleep(3)

                        attempts += 1
                        continue     
                    else:
                        raise OperationalError(f"An OperationalError other than DeadlockDetected occurred: {e}")          

            else:
                self.logger.error(f"{self.task_name}: Unable to insert and return data in 10 attempts")
                return []

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
