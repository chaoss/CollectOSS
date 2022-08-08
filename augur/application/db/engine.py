import os
import socket
import json
import sys
import logging
from sqlalchemy import create_engine, event
from augur.application.logs import initialize_stream_handler
from sqlalchemy.exc import OperationalError  
import inspect  
import traceback

logger = logging.getLogger("engine")
initialize_stream_handler(logger, logging.ERROR)


def get_database_string():

    augur_db_environment_var = os.getenv("AUGUR_DB")

    current_dir = os.getcwd()
    print(current_dir)
    db_json_file_location = current_dir + "/db.config.json"
    print(db_json_file_location)
    db_json_exists = os.path.exists(db_json_file_location)

    if not augur_db_environment_var and not db_json_exists:

        logger.error("ERROR no way to get connection to the database. \n\t\t\t\t\t\t    There is no db.config.json and the AUGUR_DB environment variable is not set\n\t\t\t\t\t\t    Please run make install or set the AUGUR_DB environment then run make install")
        sys.exit()

    if augur_db_environment_var:
        return augur_db_environment_var

    else:
        with open("db.config.json", 'r') as f:
            db_config = json.load(f)

            db_conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database_name']}"

            return db_conn_string


def create_database_engine():    

    db_conn_string = get_database_string()

    engine = create_engine(db_conn_string)

    @event.listens_for(engine, "connect", insert=True)
    def set_search_path(dbapi_connection, connection_record):
        existing_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
        cursor.close()
        dbapi_connection.autocommit = existing_autocommit

    return engine


            






