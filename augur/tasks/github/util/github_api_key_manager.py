import json

from augur.tasks.util.redis_list import RedisList

GH_KEYS_REDIS_LIST_KEY = "gh_keys"
GH_KEYS = RedisList(GH_KEYS_REDIS_LIST_KEY)

class GithubApiKeyManager:

    def __init__(self) -> None:
        self.key = self.find_best_key()

    def find_best_key(self):

        if len(GH_KEYS) == 0:
            raise Exception("No GitHub API keys found in Redis")
        
        best_key = None
        for key in GH_KEYS:

            key = json.loads(key)
            if key['rate_limit_remaining'] > best_key['rate_limit_remaining']:
                best_key = key

        return best_key["key"]

    def get_key(self):
        if not self.key:
            self.key = self.find_best_key()

        return self.key

    def invalidate_key(self):
        self.key = None