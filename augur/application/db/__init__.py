from sqlalchemy.pool import StaticPool

from augur.application.db.engine import create_database_engine, get_database_string

engine = None

def get_engine():
    global engine
    if engine is None:
        url = get_database_string()
        engine = create_database_engine(url=url, poolclass=StaticPool)  
    
    return engine


def dispose_database_engine():
    global engine
    if engine:
        engine.dispose()
        engine = None