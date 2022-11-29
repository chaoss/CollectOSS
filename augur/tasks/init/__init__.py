import logging

from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig

def get_redis_conn_values():

    logger = logging.getLogger(__name__)

    with DatabaseSession(logger) as session:

        config = AugurConfig(logger, session)

    redis_db_number = config.get_value("Redis", "cache_group") * 3
    redis_conn_string = config.get_value("Redis", "connection_string")

    if redis_conn_string[-1] != "/":
        redis_conn_string += "/"

    return redis_db_number, redis_conn_string
