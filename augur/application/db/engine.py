import os
import socket
import json
import sys
from sqlalchemy import create_engine, event

from sqlalchemy.exc import OperationalError 

def test_database_connection(engine):

    # chaoss.tv


    try:
        engine.connect()
    except OperationalError as e:

        # determine the location to print in error string
        if augur_db_environment_var:
            location = f"the AUGUR_DB environment variable\nAUGUR_DB={os.getenv('AUGUR_DB')}"
        else:
            with open("db.config.json", 'r') as f:
                db_config = json.load(f)
                location = f"db.config.json\nYour db.config.json is:{db_config}"
        
        incorrect_values = "host name is" 
        #  determine which value in the database string is causing the error
        if "could not translate host name" in str(e):
            incorrect_values = "host name is" 

        elif "Connection refused" in str(e):
            incorrect_values = "port is"

        elif "password authentication failed for user" in str(e):
            incorrect_values = "username or password are"
            
        elif "database" in str(e) and "does not exist" in str(e):
            incorrect_values = "database name is" 

        else:
            print(f"Database connection error: {e}")

        if incorrect_values:
            print(f"\n\nError: connecting to database, the {incorrect_values} incorrectly specified in {location}\n")
            
        sys.exit()

IPaddress=socket.gethostbyname(socket.gethostname())
if IPaddress=="127.0.0.1":
    print("You are not connect to the internet. Please connect to the internet to run Augur")
    sys.exit()

augur_db_environment_var = os.getenv("AUGUR_DB")

db_json_file_location = os.getcwd() + "/db.config.json"
db_json_exists = os.path.exists(db_json_file_location)


if not augur_db_environment_var and not db_json_exists:
    raise Exception("AUGUR_DB environment variable is not set, please set with command below\n\t  export AUGUR_DB=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db_name>")

if augur_db_environment_var:
    engine = create_engine(augur_db_environment_var)

else:
    with open("db.config.json", 'r') as f:
        db_config = json.load(f)

        db_conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database_name']}"
        engine = create_engine(db_conn_string)


test_database_connection(engine)


@event.listens_for(engine, "connect", insert=True)
def set_search_path(dbapi_connection, connection_record):
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
    cursor.close()
    dbapi_connection.autocommit = existing_autocommit




