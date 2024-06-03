"""
Defines the handler logic needed to effectively fetch GitLab auth keys
from either the redis cache or the database. Follows the same patterns as
the github api key handler.
"""
import httpx
import time
import random

from typing import List

from augur.tasks.util.redis_list import RedisList
from augur.application.db.lib import get_value, get_worker_oauth_keys


class NoValidKeysError(Exception):
    """Defines an exception that is thrown when no gitlab keys are valid"""


class GitlabApiKeyHandler():
    """Handles Gitlab API key retrieval from the database and redis

    Attributes:
        logger (logging.Logger): Handles all logs
        oauth_redis_key (str): The key where the gitlab api keys are cached in redis
        redis_key_list (RedisList): Acts like a python list, and interacts directly with the redis cache
        config_key (str): The api key that is stored in the users config table
        key: (List[str]): List of keys retrieve from database or cache
    """

    def __init__(self, logger):

        self.logger = logger

        self.oauth_redis_key = "gitlab_oauth_keys_list"

        self.redis_key_list = RedisList(self.oauth_redis_key)

        self.config_key = self.get_config_key()

        self.keys = self.get_api_keys()

        self.logger.info(f"Retrieved {len(self.keys)} gitlab api keys for use")

    def get_random_key(self):
        """Retrieves a random key from the list of keys

        Returns:
            A random gitlab api key
        """

        return random.choice(self.keys)

    def get_config_key(self) -> str:
        """Retrieves the users gitlab api key from their config table

        Returns:
            Github API key from config table
        """
        return get_value("Keys", "gitlab_api_key")

    def get_api_keys_from_database(self) -> List[str]:
        """Retieves all gitlab api keys from database

        Note:
            It retrieves all the keys from the database except the one defined in the users config

        Returns:
            Github api keys that are in the database
        """
        keys = get_worker_oauth_keys('gitlab')

        filtered_keys = [item for item in keys if item != self.config_key]

        return filtered_keys


    def get_api_keys(self) -> List[str]:
        """Retrieves all valid Github API Keys

        Note:
            It checks to see if the keys are in the redis cache first.
            It removes bad keys before returning.
            If keys were taken from the database, it caches all the valid keys that were found

        Returns:
            Valid Github api keys
        """

        redis_keys = list(self.redis_key_list)

        if redis_keys:
            return redis_keys

        attempts = 0
        while attempts < 3:

            try:
                keys = self.get_api_keys_from_database()
                break
            except Exception as e:
                self.logger.error(f"Ran into issue when fetching key from database:\n {e}\n")
                self.logger.error("Sleeping for 5 seconds...")
                time.sleep(5)
                attempts += 1

        if self.config_key is not None:
            keys += [self.config_key]

        if len(keys) == 0:
            return []

        valid_keys = []
        with httpx.Client() as client:

            for key in keys:

                # removes key if it returns "Bad Credentials"
                if self.is_bad_api_key(client, key) is False:
                    valid_keys.append(key)
                else:
                    print(f"WARNING: The key '{key}' is not a valid key. Hint: If valid in past it may have expired")

        # just in case the mulitprocessing adds extra values to the list.
        # we are clearing it before we push the values we got
        self.redis_key_list.clear()

        # add all the keys to redis
        self.redis_key_list.extend(valid_keys)

        if not valid_keys:
            raise NoValidKeysError("No valid gitlab api keys found in the config or worker oauth table")


        # shuffling the keys so not all processes get the same keys in the same order
        #valid_now = valid_keys
        #try: 
            #self.logger.info(f'valid keys before shuffle: {valid_keys}')
            #valid_keys = random.sample(valid_keys, len(valid_keys))
            #self.logger.info(f'valid keys AFTER shuffle: {valid_keys}')
        #except Exception as e: 
         #   self.logger.debug(f'{e}')
         #   valid_keys = valid_now
         #   pass 

        return valid_keys

    def is_bad_api_key(self, client: httpx.Client, oauth_key: str) -> bool:
        """Determines if a Gitlab API key is bad

        Args:
            client: makes the http requests
            oauth_key: gitlab api key that is being tested

        Returns:
            True if key is bad. False if the key is good
        """

        url = "https://gitlab.com/api/v4/user"

        headers = {'Authorization': f'Bearer {oauth_key}'}

        response = client.request(method="GET", url=url, headers=headers, timeout=180)
        if response.status_code == 401:
            return True
        
        return False