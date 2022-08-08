import os
from sqlalchemy.dialects import postgresql as pg_dialects
import sqlalchemy as s
import pandas as pd
import json
import httpx
from sqlalchemy.inspection import inspect
from psycopg2.errors import DeadlockDetected
from sqlalchemy.exc import OperationalError
import logging

import re
import time
import sys
import random

sys.path.append("..")
from sqlalchemy.event import listen
from sqlalchemy.event import listens_for

from augur.tasks.util.random_key_auth import RandomKeyAuth
# import psycopg2 
from augur.application.db.engine import create_database_engine
from augur.application.config import AugurConfig

from augur.application.db.models import Platform
sys.path.pop()
#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api

class DatabaseSession(s.orm.Session):

    def __init__(self, logger, engine=None):
    
        self.logger = logger
        self.config = AugurConfig(logger=logger, session=self)

        self.engine = engine
        if self.engine is None:
            self.engine = create_database_engine()

        super().__init__(self.engine)
    
    def execute_sql(self, sql_text):

        with self.engine.connect():
            connection = self.engine.connect()

            return connection.execute(sql_text)


    def insert_data(self, data: [dict], table, natural_keys: [str], return_columns: [str] = []) -> None:
        
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
        stmnt = pg_dialects.insert(table).returning(*returning_args).values(data)

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


        # print(str(stmnt.compile(dialect=pg_dialects.dialect())))
        attempts = 0
        sleep_time_list = [x for x in range(1,11)]
        deadlock_detected = False
        # if there is no data to return then it executes the insert the returns nothing
        if len(return_columns) == 0:

            while attempts < 10:
                print("")
                try:
                    with self.engine.connect() as connection:
                        connection.execute(stmnt)
                        break
                except OperationalError as e:
                    # print(str(e).split("Process")[1].split(";")[0])
                    if isinstance(e.orig, DeadlockDetected):
                        deadlock_detected = True
                        sleep_time = random.choice(sleep_time_list)
                        self.logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                        time.sleep(sleep_time)

                        attempts += 1
                        continue
                    else:
                        raise OperationalError(f"An OperationalError other than DeadlockDetected occurred: {e}") 

            else:
                self.logger.error(f"Unable to insert data in 10 attempts")
                return

            if deadlock_detected == True:
                self.logger.error(f"Made it through even though Deadlock was detected")
                    
            return
        
        # else it get the requested return columns and returns them as a list of dicts
        else:
            while attempts < 10:
                try:
                    with self.engine.connect() as connection:
                        return_data_tuples = connection.execute(stmnt).fetchall()
                        break
                except OperationalError as e:
                    if isinstance(e.orig, DeadlockDetected):
                        sleep_time = random.choice(sleep_time_list)
                        self.logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                        time.sleep(sleep_time)

                        attempts += 1
                        continue     
                    else:
                        raise OperationalError(f"An OperationalError other than DeadlockDetected occurred: {e}")          

            else:
                self.logger.error(f"Unable to insert and return data in 10 attempts")
                return []

            if deadlock_detected == True:
                self.logger.error(f"Made it through even though Deadlock was detected")

            return_data = []
            for data in return_data_tuples:
                return_data.append(dict(data))

            return return_data