
import os
from sqlalchemy.dialects import postgresql as pg
import sqlalchemy as s
import pandas as pd
import json
import httpx
from sqlalchemy.inspection import inspect
import re

from augur_new.db import models 
from sqlalchemy.event import listen
from sqlalchemy.event import listens_for
from augur_new.augur.config import AugurConfig

from augur_new.util.random_key_auth import RandomKeyAuth
import psycopg2
# from .engine import engine

#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: Test sql methods
class TaskSession(s.orm.Session):

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, logger, config: dict = {}, platform: str ='github'):
        
        self.logger = logger
        
        current_dir = os.getcwd()

        self.root_augur_dir = ''.join(current_dir.partition("augur/")[:2])
        self.__init_config(self.root_augur_dir)
        #print(self.config)

        DB_STR = f'postgresql://{self.config["user_database"]}:{self.config["password_database"]}@{self.config["host_database"]}:{self.config["port_database"]}/{self.config["name_database"]}'



        self.config.update(config)

        
        self.platform = platform
        
        #self.logger.info(f"path = {str(ROOT_AUGUR_DIR) + "augur.config.json"}")
        

        self.engine = s.create_engine(DB_STR)
        # self.engine = engine
    

        #Derek 
        @s.event.listens_for(self.engine, "connect", insert=True)
        def set_search_path(dbapi_connection, connection_record):
            existing_autocommit = dbapi_connection.autocommit
            dbapi_connection.autocommit = True
            cursor = dbapi_connection.cursor()
            cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
            cursor.close()
            dbapi_connection.autocommit = existing_autocommit

        super().__init__(self.engine)

    def __init_config(self, root_augur_dir: str):
        #Load config.
        self.augur_config = AugurConfig(self.root_augur_dir)
        self.config = {
            'host': self.augur_config.get_value('Server', 'host')
        }
        self.config.update(self.augur_config.get_section("Logging"))

        self.config.update({
            'capture_output': False,
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password'),
            'key_database' : self.augur_config.get_value('Database', 'key')
        })
    
    def execute_sql(self, sql_text):
        connection = self.engine.connect()

        return connection.execute(sql_text)

    
    def insert_data(self, data, table, natural_keys: [str]) -> None:

        if len(data) == 0:
            return

        first_data = data[0]

        if type(first_data) == dict:
            return self.insert_dict_data(data, table, natural_keys)
        else:
            print("Error passed a github class object")
            # return self.insert_github_class_objects(data, table, natural_keys)

    def insert_dict_data(self, data: [dict], table, natural_keys: [str]) -> None:

        if type(data) != list:
            self.logger.info("Data must be a list")
            return

        if type(data[0]) != dict:
            self.logger.info("Data must be a list of dicts")
            self.logger.info("Must be list of dicts")
            return

        self.logger.info(f"Length of data to insert: {len(data)}")

        table_stmt = pg.insert(table)

        primary_keys = []

        for value in data:
            insert_stmt = table_stmt.returning(table.pull_request_id).values(value)
            insert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=natural_keys, set_=dict(value))

            try:
                connection = self.engine.connect()
                primary_key_tuple = connection.execute(insert_stmt).fetchone()
                primary_keys.append(primary_key_tuple)

            except s.exc.DatabaseError as e:
                self.logger.info(f"Error: {e}")
                continue

        return primary_keys

                

    # def insert_github_class_objects(self, objects, table, natural_keys: str) -> None:

    #     if type(objects) != list:
    #         self.logger.info("Data must be a list")
    #         return

    #     table_stmt = pg.insert(table)

    #     for obj in objects:
    #         data = obj.get_dict()
    #         insert_stmt = table_stmt.returning(table.pull_request_id).values(data)
    #         insert_stmt = insert_stmt.on_conflict_do_update(
    #             index_elements=natural_keys, set_=dict(data))

    #         try:
                
                
    #         except s.exc.DatabaseError as e:
    #             self.logger.info(f"Error: {e}")
    #             continue

    #         # the insert returns a list of tuples
    #         # since we are only inserting one it should 
    #         # primary_key = return_values[0][0]

    #         # natural_key_dict = {}
    #         # for key in natural_keys:
    #         #     natural_key_dict[key] = data[key]

    #         # rows = table.query.filter_by(**natural_key_dict).all()

    #         # if len(rows) == 0:
    #         #     self.logger.info("Error could not get associated row for inserted pr")
    #         #     continue

    #         # if len(rows) > 1:
    #         #     self.logger.info(f"Error values in table not unique on {natural_keys}")
    #         #     continue

    #         # print(return_value)
    #         # print(rows[0].pull_request_id)

    #         # obj.set_db_row(rows[0])

    #         return 



    #TODO: Bulk upsert
    
    def insert_bulk_data(self, data: [dict], table, natural_keys: [str], return_columns: [str] = []) -> None:
        self.logger.info(f"Length of data to insert: {len(data)}")

        if type(data) != list:
            self.logger.info("Data must be a list")
            return

        if len(data) < 0:
            self.logger.info("Gave no data to insert, returning...")
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

        return_data_tuples = self.execute_sql(stmnt).fetchall()

        # converts the return data to a list of dicts
        return_data = []
        for data in return_data_tuples:
            return_data.append(dict(data))

        return return_data

#TODO: Test sql methods
class GithubTaskSession(TaskSession):

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self, logger, config: dict = {}, platform: str ='github'):

        super().__init__(logger, config, platform)

        keys = self.get_list_of_oauth_keys(self.engine, self.config["key_database"])

        self.oauths = RandomKeyAuth(keys)
        

    def get_list_of_oauth_keys(self, db_engine: s.engine.base.Engine, config_key: str) ->[str]:

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
