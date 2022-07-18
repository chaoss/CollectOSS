import redis
# import json

redis_connection= redis.from_url('redis://localhost:6379/2', decode_responses=True)

# class RedisHandler():

#     def __init__(self):

        
    
#     def set(self, key, value):
#         json_value = json.dumps(value)
#         self.redis_connection.set(key, json_value)
        
#     def get(self, key):
#         obj = self.redis_connection.get(key)
#         print(obj)

#         if obj is not None:
#             return json.loads(obj)

#         return None
        
