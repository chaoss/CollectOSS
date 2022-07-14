import os
from sqlalchemy import create_engine, event

engine = create_engine(os.getenv("AUGUR_DB"))


@event.listens_for(engine, "connect", insert=True)
def set_search_path(dbapi_connection, connection_record):
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
    cursor.close()
    dbapi_connection.autocommit = existing_autocommit
