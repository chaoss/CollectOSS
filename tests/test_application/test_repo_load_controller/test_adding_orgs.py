import pytest
import logging

from tests.test_application.test_repo_load_controller.helper import *
from collectoss.tasks.github.util.github_task_session import GithubTaskSession

from collectoss.util.repo_load_controller import RepoLoadController, DEFAULT_REPO_GROUP_IDS, CLI_USER_ID
from collectoss.application.db.models import UserRepo


logger = logging.getLogger(__name__)


