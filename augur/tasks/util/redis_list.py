from collections.abc import MutableSequence
from augur.tasks.init.redis_connection import redis_connection as redis
from augur import instance_id

class RedisList(MutableSequence):

    def __init__(self, list_name):
        self.list = f"{instance_id}_{list_name}"

    def __init__(self, list_name):
        self.list = list_name

    def __len__(self):
        return redis.llen(self.list) 

    def __iter__(self):
        for index in range(0, self.__len__()):
            yield self.__getitem__(index)

    def __getitem__(self, index):

        item = redis.lindex(self.list, index)
        try:
            item = int(item)
            return item
        except ValueError as e:
            pass
        
        try:
            item = float(item)
            return item
        except ValueError as e:
            pass

        return item

    def __setitem__(self, index, data):
        redis.lset(self.list, index, data)
    
    def __delitem__(self, index):
        
        value = reids.lindex(self.list, index)
        redis.lrem(self.list, value)

    def contains(self, value):

        if redis.lpos(self.list, value) == None:
            return False

        return True

    def insert(self, index, data):

        value_before = reids.lindex(self.list, index-1)
        redix.linsert(self.list, "after", value_before, data)

    def append(self, data):
        redis.rpush(self.list, data)

    def pop(self):
        redis.rpop(self.list)

    def remove(self, value):
        redis.lrem(self.list, 0, value)

    def extend(self, data_list):

        if data_list:
            redis.rpush(self.list, *data_list)

    def clear(self):
        redis.delete(self.list)

def print_list(list):

    key_list_length = redis.llen(list) 

    for i in range(key_list_length):
        print(redis.lindex(list, i))

