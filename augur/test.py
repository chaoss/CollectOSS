

import httpx
import time
import logging

from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.application.db.session import DatabaseSession

logger = logging.getLogger(__name__)

with DatabaseSession(logger) as session:

    with httpx.Client() as client:
        url = "https://api.github.com/rate_limit"

        response = client.request(method="GET", url=url, timeout=180)

        epoch_reset_time = response.headers["X-RateLimit-Reset"]
        current_epoch = time.time()

        key_reset_time = int(epoch_reset_time) - current_epoch

        print(key_reset_time/60)

