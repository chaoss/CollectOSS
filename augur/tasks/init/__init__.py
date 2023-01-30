import logging

from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
from augur.application.config import AugurConfig

def get_redis_conn_values():

    logger = logging.getLogger(__name__)

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        config = AugurConfig(logger, session)

    redis_db_number = config.get_value("Redis", "cache_group") * 3
    redis_conn_string = config.get_value("Redis", "connection_string")

    if redis_conn_string[-1] != "/":
        redis_conn_string += "/"

    return redis_db_number, redis_conn_string

def get_rabbitmq_conn_string():
    logger = logging.getLogger(__name__)

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:
        config = AugurConfig(logger, session)
    
        rabbbitmq_conn_string = config.get_value("RabbitMQ", "connection_string")

    return rabbbitmq_conn_string
