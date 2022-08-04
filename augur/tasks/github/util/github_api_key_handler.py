import httpx

from augur.application.db.models import WorkerOauth
from augur.tasks.util.redis_list import RedisList

class GithubApiKeyHandler():

    # optionally takes a session and config 
    def __init__(self, session):

        self.session = session

        self.config_key = self.get_config_key()

        self.keys = self.get_api_keys()

        self.redis_key_list = RedisList("oauth_keys_list")

    def get_config_key(self):

        return self.session.config.get_value("Keys", "github_api_key")

    def get_api_keys_from_database(self):

        select = WorkerOauth.access_token
        where = tuple(WorkerOauth.access_token != self.config_key, WorkerOauth.platform == 'github')

        return [key_tuple[0] for key_tuple in self.session.query(select).filter(where).all()]

    def get_api_keys(self) ->[str]:

        if len(self.redis_key_list) > 0:
            return list(self.redis_key_list)

        keys = self.get_api_keys_from_database() + [self.config_key]

        with httpx.Client() as client:

            for key in keys:

                # removes key if it returns "Bad Credentials"
                if self.is_bad_api_key(client, key):
                      keys.remove(key)

        # just in case the mulitprocessing adds extra values to the list.
        # we are clearing it before we push the values we got
        self.redis_key_list.clear()

        # add all the keys to redis
        self.redix_key_list.extend(keys)

        return keys

    def is_bad_api_key(self, client: httpx.Client, oauth_key: str) -> None or True:

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