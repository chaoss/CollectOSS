import json
import pandas as pd
from sqlalchemy as s
import httpx
from augur.application.db.engine import engine
from augur.application.config import ReadAugurConfig
from augur.application.db import DatabaseSession
from augur.tasks.init.redis_connection import redis_connection as redis

class ApiKeyHandler():

    def __init__(self):

        session = DatabaseSession()
        config = ReadAugurConfig(session)
        api_key = config.get_value("Keys", "github_api_key")

        self.github_api_keys = self.get_github_api_keys_from_db(api_key)

    def get_github_api_keys(self):
        return self.github_api_keys

    def get_github_api_keys_from_redis():

        key_list_length = redis.llen("oauth_keys_list") 

        if key_list_length == 0:
            return []
        
        keys = [redis.lindex("oauth_keys_list", i) for i in range(0, key_list_length)]

        return keys

    def get_github_api_keys_from_db(self, config_key: str) ->[str]:

        keys = get_github_api_keys_from_redis()

        if len(keys) > 0:
            return keys

        
        
        oauthSQL = s.sql.text(f"""
                SELECT access_token FROM augur_operations.worker_oauth WHERE access_token <> '{config_key}' and platform = 'github'
                """)

        oauth_keys_list = [{'access_token': config_key}] + json.loads(
            pd.read_sql(oauthSQL, engine, params={}).to_json(orient="records"))

        key_list = [x["access_token"] for x in oauth_keys_list]

        with httpx.Client() as client:

            # loop throuh each key in the list and get the rate_limit and seconds_to_reset
            # then add them either the fresh keys or depleted keys based on the rate_limit
            for key in key_list:

                # this makes sure that keys with bad credentials are not used
                if self.is_bad_github_api_key(client, key):
                    key_list.remove(key)                    

        for key in key_list:
            # just in case the mulitprocessing adds extra values to the list.
            # we are clearing it before we push the values we got
            for i in range(0, redis.llen("oauth_keys_list")):
                redis.lpop("oauth_keys_list")

            redis.lpush("oauth_keys_list", key)

        return key_list


    def is_bad_github_api_key(self, client: httpx.Client, oauth_key: str) -> None or True:

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