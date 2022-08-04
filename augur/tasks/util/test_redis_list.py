import pytest
from augur.tasks.init.redis_connection import redis_connection as redis
from augur.tasks.util.redis_list import RedisList

list_name = "list"

@pytest.fixture()
def redis_list():

    redis_list = RedisList(list_name)

    yield redis_list

    redis.flushdb()

def test_redis_list_append(redis_list):

    string = "Hello world, how are you?"

    string_array = string.split(" ")

    for word in string_array:
        redis_list.append(word)

    for i in range(0, len(string_array)):
    
        assert redis.lindex(list_name, i) == string_array[i]

def test_redis_list_lenth(redis_list):

    redis.rpush(list_name, "hello", "world")

    assert len(redis_list) == 2

def test_redis_list_contains(redis_list):

    insert_values = [i for i in range(2, 10, 2)]

    redis.rpush(list_name, *insert_values)

    for item in insert_values:
        assert redis_list.contains(item) == True

    assert redis_list.contains(5) == False
    assert redis_list.contains(1000) == False
    assert redis_list.contains(50) == False


def test_redis_list_extend(redis_list):

    insert_values = [i for i in range(2, 10, 2)]

    redis_list.extend(insert_values)

    for i in range(0, len(insert_values)):
    
        assert int(redis.lindex(list_name, i)) == insert_values[i]
        






