"""Defines the redis connection."""
import redis
from augur.tasks.init import get_redis_conn_values

redis_db_number, redis_conn_string = get_redis_conn_values()

redis_connection= redis.from_url(f'{redis_conn_string}{redis_db_number+2}', decode_responses=True)
