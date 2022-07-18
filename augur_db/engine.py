import os
from sqlalchemy import create_engine, event

augur_db_environment_var = os.getenv("AUGUR_DB")

if augur_db_environment_var:

    engine = create_engine(augur_db_environment_var)

    @event.listens_for(engine, "connect", insert=True)
    def set_search_path(dbapi_connection, connection_record):
        existing_autocommit = dbapi_connection.autocommit
        dbapi_connection.autocommit = True
        cursor = dbapi_connection.cursor()
        cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
        cursor.close()
        dbapi_connection.autocommit = existing_autocommit

else:
    raise Exception("AUGUR_DB environment variable is not set, please set with command below\n\t  export AUGUR_DB=postgresql+psycopg2://<user>:<password>@<host>:<port>/<db_name>")