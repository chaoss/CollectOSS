import httpx

from typing import Optional, List

from augur.application.db.models import WorkerOauth
from augur.tasks.util.redis_list import RedisList
from augur.application.db.session import DatabaseSession
from augur.tasks.init.celery_app import engine

class GithubApiKeyHandler():
    """Handles Github API key retrieval from the database and redis

    Attributes:
        session (DatabaseSession): Database connection
        logger (logging.Logger): Handles all logs
        oauth_redis_key (str): The key where the github api keys are cached in redis
        redis_key_list (RedisList): Acts like a python list, and interacts directly with the redis cache
        config_key (str): The api key that is stored in the users config table
        key: (List[str]): List of keys retrieve from database or cache
    """

    def __init__(self, session: DatabaseSession):

        self.session = session
        self.logger = session.logger

        self.oauth_redis_key = "oauth_keys_list"

        self.redis_key_list = RedisList(self.oauth_redis_key)

        self.config_key = self.get_config_key()

        self.keys = self.get_api_keys()

        # self.logger.debug(f"Retrieved {len(self.keys)} github api keys for use")

    def get_config_key(self) -> str:
        """Retrieves the users github api key from their config table

        Returns:
            Github API key from config table
        """

        return self.session.config.get_value("Keys", "github_api_key")

    def get_api_keys_from_database(self) -> List[str]:
        """Retieves all github api keys from database

        Note:
            It retrieves all the keys from the database except the one defined in the users config

        Returns:
            Github api keys that are in the database
        """
        select = WorkerOauth.access_token
        where = [WorkerOauth.access_token != self.config_key, WorkerOauth.platform == 'github']

        return [key_tuple[0] for key_tuple in self.session.query(select).filter(*where).all()]


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

        keys = self.get_api_keys_from_database()
    
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

        # just in case the mulitprocessing adds extra values to the list.
        # we are clearing it before we push the values we got
        self.redis_key_list.clear()

        # add all the keys to redis
        self.redis_key_list.extend(valid_keys)

        return valid_keys

    def is_bad_api_key(self, client: httpx.Client, oauth_key: str) -> bool:
        """Determines if a Github API is bad

        Args:
            client: makes the http requests
            oauth_key: github api key that is being tested

        Returns:
            True if key is bad. False if the key is good
        """

        # this endpoint allows us to check the rate limit, but it does not use one of our 5000 requests
        url = "https://api.github.com/rate_limit"

        headers = {'Authorization': f'token {oauth_key}'}

        data = client.request(method="GET", url=url, headers=headers, timeout=180).json()

        try:
            if data["message"] == "Bad credentials":
                return True
        except KeyError:
            pass

        return False