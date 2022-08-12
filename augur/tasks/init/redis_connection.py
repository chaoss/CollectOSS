import redis
from augur.tasks.init import redis_db_number

redis_connection= redis.from_url(f'redis://localhost:6379/{redis_db_number+2}', decode_responses=True)



        
