import os
import json
from sqlalchemy import create_engine, event

augur_db_environment_var = os.getenv("AUGUR_DB")
db_json_exists = os.path.exists("db.json")

if not augur_db_environment_var and not db_json_exists:
    raise Exception("AUGUR_DB environment variable is not set, please set with command below\n\t  export AUGUR_DB=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db_name>")

# if db.json exists it creates the engine from it, if it doesn't exist it creates it from the environment variable
if db_json_exists:
    with open("db.json", 'r') as f:
        db_config = json.load(f)

        db_conn_string = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database_name']}"
        engine = create_engine(db_conn_string)

elif augur_db_environment_var:
    engine = create_engine(augur_db_environment_var)

@event.listens_for(engine, "connect", insert=True)
def set_search_path(dbapi_connection, connection_record):
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
    cursor.close()
    dbapi_connection.autocommit = existing_autocommit

