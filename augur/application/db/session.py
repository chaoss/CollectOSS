import os
import re
import time
import sys
import random
import logging
import json
import httpx
import sqlalchemy as s

from typing import Optional, List, Union
from psycopg2.errors import DeadlockDetected

from augur.tasks.util.random_key_auth import RandomKeyAuth
from augur.application.db.engine import create_database_engine
from augur.application.config import AugurConfig
from augur.application.db.models import Platform


class DatabaseSession(s.orm.Session):

    def __init__(self, logger, engine=None):
    
        self.logger = logger
        self.config = AugurConfig(logger=logger, session=self)

        self.engine = engine
        if self.engine is None:
            self.engine = create_database_engine()

        super().__init__(self.engine)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.close()
    
    def execute_sql(self, sql_text):

        with self.engine.connect():
            connection = self.engine.connect()

            return connection.execute(sql_text)


    def insert_data(self, data: Union[List[dict], dict], table, natural_keys: List[str], return_columns: Optional[List[str]] = None) -> Optional[List[dict]]:
        
        if isinstance(data, list) is False:
            
            # if a dict is passed to data then 
            # convert it to a list with one value
            if isinstance(data, dict) is True:
                data = [data]
            
            else:
                self.logger.info("Data must be a list or a dict")
                return None

        if len(data) == 0:
            # self.logger.info("Gave no data to insert, returning...")
            return None

        if isinstance(data[0], dict) is False: 
            self.logger.info("Must be list of dicts")
            return None

        # creates list of arguments to tell sqlalchemy what columns to return after the data is inserted

        returning_args = []
        if return_columns:
            for column in return_columns:
                argument = getattr(table, column)
                returning_args.append(argument)

        # creates insert on table
        # that returns cols specificed in returning_args
        # and inserts the data specified in data
        # NOTE: if return_columns does not have an values this still works
        stmnt = s.dialects.postgresql.insert(table).returning(*returning_args).values(data)

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


        # print(str(stmnt.compile(dialect=s.dialects.postgresql.dialect())))
        attempts = 0
        # creates list from 1 to 10
        sleep_time_list = list(range(1,11))
        deadlock_detected = False

        # if there is no data to return then it executes the insert then returns nothing
        if not return_columns:

            while attempts < 10:
                print("")
                try:
                    with self.engine.connect() as connection:
                        connection.execute(stmnt)
                        break
                except s.exc.OperationalError as e:
                    # print(str(e).split("Process")[1].split(";")[0])
                    if isinstance(e.orig, DeadlockDetected):
                        deadlock_detected = True
                        sleep_time = random.choice(sleep_time_list)
                        self.logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                        time.sleep(sleep_time)

                        attempts += 1
                        continue
                    
                    raise e

            else:
                self.logger.error("Unable to insert data in 10 attempts")
                return None

            if deadlock_detected is True:
                self.logger.error("Made it through even though Deadlock was detected")
                    
            return None
        

        # othewise it gets the requested return columns and returns them as a list of dicts
        while attempts < 10:
            try:
                with self.engine.connect() as connection:
                    return_data_tuples = connection.execute(stmnt).fetchall()
                    break
            except s.exc.OperationalError as e:
                if isinstance(e.orig, DeadlockDetected):
                    sleep_time = random.choice(sleep_time_list)
                    self.logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                    time.sleep(sleep_time)

                    attempts += 1
                    continue   

                raise e

        else:
            self.logger.error("Unable to insert and return data in 10 attempts")
            return None

        if deadlock_detected is True:
            self.logger.error("Made it through even though Deadlock was detected")

        return_data = []
        for data_tuple in return_data_tuples:
            return_data.append(dict(data_tuple))

        return return_data