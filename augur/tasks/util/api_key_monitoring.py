import json
import logging
import httpx

from augur.tasks.util.redis_list import RedisList
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.tasks.github.util.github_task_session import GithubTaskManifest

from augur.tasks.github.util.github_api_key_manager import GH_KEYS_REDIS_LIST_KEY

GH_KEYS = RedisList(GH_KEYS_REDIS_LIST_KEY)
logger = logging.getLogger(__name__)


def find_new_github_api_keys():

    with GithubTaskManifest(logger) as manifest:

        keys = GithubApiKeyHandler(manifest.augur_db)
        keys_set = set(keys)

        reids_keys = set([json.loads(key)["key"] for key in GH_KEYS])

        new_keys = keys_set - reids_keys

        new_key_objects = [json.dumps({"key": key, "rate_limit_remaining": -1}) for key in new_keys]

        RedisList(GH_KEYS_REDIS_LIST_KEY).extend(new_key_objects)


@celery.task(autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=300, retry_jitter=True, max_retries=None)
def update_key_rate_limits():

    with GithubTaskManifest(logger) as manifest:

        with httpx.Client() as client:  
        
            for index, key in enumerate(GH_KEYS):
                github_api_key_obj = json.loads(key)
                key = github_api_key_obj["key"]

                github_api_key_obj["rate_limit_remaining"] = GithubApiKeyHandler.get_rate_limit_remaining(key)
                GH_KEYS[index] = json.dumps(github_api_key_obj)

    update_key_rate_limits.apply_async(countdown=30)

            





