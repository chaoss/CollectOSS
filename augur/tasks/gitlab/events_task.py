"""
Module to define the task methods to collect gitlab event data for augur
"""
import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_api_handler import GitlabApiHandler
from augur.application.db.data_parse import extract_gitlab_mr_event_data, extract_gitlab_issue_event_data
from augur.tasks.github.util.util import get_owner_repo
from augur.application.db.models import Issue, IssueEvent, PullRequest, PullRequestEvent
from augur.application.db.lib import bulk_insert_dicts, get_repo_by_repo_git, get_session
from augur.tasks.gitlab.gitlab_random_key_auth import GitlabRandomKeyAuth


platform_id = 2

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issue_events(repo_git) -> int:
    """
    Retrieve and parse gitlab events for the desired repo

    Arguments:
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_gitlab_issue_events.__name__) 

    repo_id = get_repo_by_repo_git(repo_git).repo_id

    key_auth = GitlabRandomKeyAuth(logger)

    events = retrieve_all_gitlab_event_data("issue", repo_git, logger, key_auth)

    with get_session() as session:

        if events:
            logger.info(f"Length of gitlab issue events: {len(events)}")
            process_issue_events(events, f"{owner}/{repo}: Gitlab Issue Events task", repo_id, logger, session)
        else:
            logger.info(f"{owner}/{repo} has no gitlab issue events")


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_merge_request_events(repo_git) -> int:
    """
    Retrieve and parse gitlab mrs for the desired repo

    Arguments:
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_gitlab_issue_events.__name__) 

    repo_id = get_repo_by_repo_git(repo_git).repo_id

    key_auth = GitlabRandomKeyAuth(logger)

    events = retrieve_all_gitlab_event_data("merge_request", repo_git, logger, key_auth)

    with get_session() as session:

        if events:
            logger.info(f"Length of gitlab merge request events: {len(events)}")
            process_mr_events(events, f"{owner}/{repo}: Gitlab MR Events task", repo_id, logger, session)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request events")


def retrieve_all_gitlab_event_data(gtype, repo_git, logger, key_auth) -> None:
    """
    Retrieve only the needed data for mr label data from the api response

    Arguments:
        gtype: type of event data
        repo_git: url of the relevant repo
        logger: loggin object
        key_auth: key auth cache and rotator object 
    """

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting gitlab issue events for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/events?target_type={gtype}"
    events = GitlabApiHandler(key_auth, logger)

    all_data = []
    num_pages = events.get_num_pages(url)
    for page_data, page in events.iter_pages(url):

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo}: Gitlab {gtype} Events Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo}: {gtype} Events Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo}: Gitlab {gtype} Events Page {page} of {num_pages}")

        all_data += page_data

    return all_data

def process_issue_events(events, task_name, repo_id, logger, session):
    """
    Retrieve only the needed data for mr label data from the api response

    Arguments:
        events: List of dictionaries of issue event data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        session: sqlalchemy db object 
    """

    tool_source = "Gitlab issue events task"
    tool_version = "2.0"
    data_source = "Gitlab API"
   
    issue_event_dicts = []

    # create mapping from issue number to issue id of current issues
    issue_url_to_id_map = {}
    issues = session.query(Issue).filter(Issue.repo_id == repo_id).all()
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
    bulk_insert_dicts(logger, issue_event_dicts, IssueEvent, issue_event_natural_keys)


def process_mr_events(events, task_name, repo_id, logger, session):
    """
    Retrieve only the needed data for mr events from the api response

    Arguments:
        labels: List of dictionaries of label data
        repo_id: augur id of the repository
        tool_source: The part of augur that processed the data
        tool_version: The version of the augur task that processed the data
        data_source: The source of the data 

    
    Returns:
        List of parsed label dicts
    """

    tool_source = "Gitlab mr events task"
    tool_version = "2.0"
    data_source = "Gitlab API"
   
    mr_event_dicts = []

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    for event in events:

        mr_number = event["target_iid"]

        try:
            issue_id = mr_number_to_id_map[mr_number]
        except KeyError:
            logger.info(f"{task_name}: Could not find related mr")
            logger.info(f"{task_name}: We were searching for an mr with number {mr_number} in repo {repo_id}")
            logger.info(f"{task_name}: Skipping")
            continue

        mr_event_dicts.append(
            extract_gitlab_mr_event_data(event, issue_id, platform_id, repo_id,
                                    tool_source, tool_version, data_source)
        )

    logger.info(f"{task_name}: Inserting {len(mr_event_dicts)} gitlab mr events")
    mr_event_natural_keys = ["platform_id", "node_id"]
    bulk_insert_dicts(logger, mr_event_dicts, PullRequestEvent, mr_event_natural_keys)


