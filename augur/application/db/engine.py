import os
import socket
import json
import sys
from sqlalchemy import create_engine, event
from sqlalchemy.exc import OperationalError

def create_database_engine():

    global engine
    if "engine" in globals():
        return engine

    augur_db_environment_var = os.getenv("AUGUR_DB")

    db_json_file_location = os.getcwd() + "/db.config.json"
    db_json_exists = os.path.exists(db_json_file_location)

    if not augur_db_environment_var and not db_json_exists:

        raise Exception("Error no way to get connection to the database. There is no db.config.json and the AUGUR_DB environment variable is not set. Please run make install-dev or set the AUGUR_DB environment then run make install-dev")
        sys.exit()

    if augur_db_environment_var:
        engine = create_engine(augur_db_environment_var)

    else:
        with open("db.config.json", 'r') as f:
            db_config = json.load(f)

            db_conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database_name']}"
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




