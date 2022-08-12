import redis
from augur import database_three_id

redis_connection= redis.from_url(f'redis://localhost:6379/{database_three_id}', decode_responses=True)

        
