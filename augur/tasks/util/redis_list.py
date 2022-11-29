"""This module defines the RedisList class. 
It imports the redis_connection as redis which is a connection to a redis cahce
"""
from typing import Iterable, Any, Union

from collections.abc import MutableSequence
from augur.tasks.init.redis_connection import redis_connection as redis
from augur import instance_id
from redis import exceptions


class RedisList(MutableSequence):
    """Class to handler all operations of a redis list

    Designed so developers can interact with redis lists the same way python lists are interacted with
    
    Attributes:
        redis_list_key (str): this is the key used to store the redis list
    """

    def __init__(self, list_name: str):
        """Defines a RedisList instance and sets the class variable redis_list_key to the key that the list will be stored at

        Args:
            list_name: Key used to store the list in redis
        """

        self.redis_list_key = f"{instance_id}_{list_name}"


    def __len__(self) -> int:
        """Gets the length of the redis list with the key equal to self.redis_list_key

        Returns:
            length of redis list
        """

        return redis.llen(self.redis_list_key) 


    def __iter__(self) -> Any:
        """Generator that yields the data in the list

        Yields:
            Items in the list one at a time
        """

        for index in range(0, self.__len__()):
            item = self.__getitem__(index)

            if item is not None:
                yield item

    def __getitem__(self, index: int) -> Any:
        """Gets an item from the redis list by index

        Note:
            The index is zero based

        Args:
            index: index of desired item in list

        Returns:
            Item at requested index
        """

        item = redis.lindex(self.redis_list_key, index)
        if item is None:
            return None

        try:
            item = int(item)
            return item
        except ValueError:
            pass
        
        try:
            item = float(item)
            return item
        except ValueError:
            pass

        return item

    def __setitem__(self, index: int, data: Union[Any, Iterable[Any]]):
        """Set an item in the redis list by index

        Note:
            The index is zero based.
            This will not shift the data to right like insert does, if there is a value at the position of index it will be overwritten

        Args:
            index: index of desired item in list
            data: item to add to list
        """


        if redis.exists(self.redis_list_key):
            redis.lset(self.redis_list_key, index, data)
        else:
            redis.rpush(self.redis_list_key, data)

    
    def __delitem__(self, index: int) -> None:
        """Deletes an item from the list at a given index

        Note:
            The index is zero based.

        Args:
            index: index of desired item in list
        """

        items_before = redis.lpop(self.redis_list_key, index+1)
        items_before.pop() 
        if items_before:
            redis.lpush(self.redis_list_key, *items_before)

    # def contains(self, value: Any):
    #     """Determiens whether the paramater value is in the list

    #     Args:
    #         value: item that is searched for in the list

    #     Returns:
    #         True if item in the list. False if it is not
    #     """
    #     print(value)
    #     print(type(value))

    #     if redis.lpos(name=self.redis_list_key, value=str(value)) is None:
    #         return False

        return True

    def insert(self, index: int, value: Any):
        """Inserts the paramater value at the given index

        Note:
            This shifts all values above the index to the right, and sets value to the position of index. 

        Args:
            index: the index the item will be inserted into
            data: value that will be added
        """

        value_before = redis.lindex(self.redis_list_key, index-1)
        redis.linsert(self.redis_list_key, "after", value_before, value)

    def append(self, value):
        """Adds the paramater value to the end of the list

        Args:
            value: value that is added to end of list
        """

        redis.rpush(self.redis_list_key, value)


    def pop(self, index: int = None):
        """Removes item from list at given index. If index is None then it removes the last value in the list

        Note:
            the list is zero indexed
        
        Args:
            index: index to remove from list. Defaults to None
        """

        if index is None:

            redis.rpop(self.redis_list_key)

        else:
            # calls __delitem__
            del self[index]


    def remove(self, value):
        """Removes all items in the list that are equivalent to value

        Args:
            value: item being removed
        """

        redis.lrem(self.redis_list_key, 0, value)


    def extend(self, values: Iterable[Any]):
        """Adds values to the redis list

        Args:
            values: adds items in values to redis list
        """

        if values:
            redis.rpush(self.redis_list_key, *values)


    def clear(self):
        """Removes all items from the redis list"""

        redis.delete(self.redis_list_key)

    
    def print_values(self):
        """Prints all the values in the redis list"""

        key_list_length = redis.llen(self.redis_list_key) 

        for i in range(key_list_length):
            print(redis.lindex(self.redis_list_key, i))

if __name__ == "__main__":

    redis.flushdb()
    redis_list = RedisList("list")
    
    # redis_list.append(5)
    # redis_list.append(15)
    # redis_list.append(8)
    # redis_list.append(8)
    redis_list[0:4:2] = [0, 1]
    print("List values")
    redis_list.print_values()

    redis.delete("list")
    