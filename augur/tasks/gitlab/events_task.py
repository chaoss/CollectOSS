import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_api_handler import GitlabApiHandler
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_gitlab_mr_event_data, extract_gitlab_issue_event_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import Repo, Issue, IssueEvent, PullRequest
from augur.application.db.util import execute_session_query

platform_id = 2

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issue_events(repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_gitlab_issue_events.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        events = retrieve_all_gitlab_event_data("issue", repo_git, logger, manifest.key_auth)

        if events:
            logger.info(f"Length of gitlab issue events: {len(events)}")
            process_issue_events(events, f"{owner}/{repo}: Gitlab Issue Events task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab issue events")


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_merge_request_events(repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_gitlab_issue_events.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        events = retrieve_all_gitlab_event_data("merge_request", repo_git, logger, manifest.key_auth)

        if events:
            logger.info(f"Length of gitlab merge request events: {len(events)}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request events")


def retrieve_all_gitlab_event_data(type, repo_git, logger, key_auth) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting gitlab issue events for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/events?target_type={type}"
    events = GitlabApiHandler(key_auth, logger)

    all_data = []
    num_pages = events.get_num_pages(url)
    for page_data, page in events.iter_pages(url):

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo}: Gitlab {type} Events Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo}: {type} Events Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo}: Gitlab {type} Events Page {page} of {num_pages}")

        all_data += page_data

    return all_data

def process_issue_events(events, task_name, repo_id, logger, augur_db):
    
    tool_source = "Gitlab events task"
    tool_version = "2.0"
    data_source = "Gitlab API"
   
    issue_event_dicts = []

    # create mapping from issue number to issue id of current issues
    issue_url_to_id_map = {}
    issues = augur_db.session.query(Issue).filter(Issue.repo_id == repo_id).all()
    for issue in issues:
        issue_url_to_id_map[issue.gh_issue_number] = issue.issue_id

    for event in events:

        issue_number = event["target_iid"]

        try:
            issue_id = issue_url_to_id_map[issue_number]
        except KeyError:
            logger.info(f"{task_name}: Could not find related issue")
            logger.info(f"{task_name}: We were searching for an issue with number {issue_number} in repo {repo_id}")
            logger.info(f"{task_name}: Skipping")
            continue

        issue_event_dicts.append(
            extract_gitlab_issue_event_data(event, issue_id, platform_id, repo_id,
                                    tool_source, tool_version, data_source)
        )

    logger.info(f"{task_name}: Inserting {len(issue_event_dicts)} gitlab issue events")
    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    augur_db.insert_data(issue_event_dicts, IssueEvent, issue_event_natural_keys)


