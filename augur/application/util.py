import logging
import sys
from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
from augur.util.repo_load_controller import RepoLoadController

if sys.version_info >= (3, 13):
    from typing import deprecated
else:
    # This will be available via the dependency added above
    from typing_extensions import deprecated

logger = logging.getLogger(__name__)

def get_all_repos(page=0, page_size=25, sort="repo_id", direction="ASC", **kwargs):

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        controller = RepoLoadController(session)

        result = controller.paginate_repos("all", page, page_size, sort, direction, **kwargs)

        return result

def get_all_repos_count(**kwargs):

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        controller = RepoLoadController(session)

        result = controller.get_repo_count(source="all", **kwargs)

        return result