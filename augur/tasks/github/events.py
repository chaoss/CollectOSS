import logging
import traceback
import sqlalchemy as s
from sqlalchemy.sql import text

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_data_access import GithubDataAccess
from augur.tasks.github.util.github_random_key_auth import GithubRandomKeyAuth
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.application.db.models import PullRequestEvent, IssueEvent, Contributor, CollectionStatus
from augur.application.db.lib import get_repo_by_repo_git, bulk_insert_dicts, get_issues_by_repo_id, get_pull_requests_by_repo_id, update_issue_closed_cntrbs_by_repo_id, get_session, get_engine


platform_id = 1

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_events(repo_git: str):

    logger = logging.getLogger(collect_events.__name__)

    repo_obj = get_repo_by_repo_git(repo_git)
    repo_id = repo_obj.repo_id

    owner, repo = get_owner_repo(repo_git)

    logger.debug(f"Collecting Github events for {owner}/{repo}")

    key_auth = GithubRandomKeyAuth(logger)

    if bulk_events_collection_endpoint_contains_all_data(key_auth, logger, owner, repo):
        event_generator = bulk_collect_pr_and_issue_events(repo_git, logger, key_auth)
    else:
        event_generator = collect_pr_and_issues_events_by_number(repo_id, repo_git, logger, key_auth, f"{owner}/{repo}: Event task")

    events = []
    for event in event_generator:
        events.append(event)

        # making this a decent size since process_events retrieves all the issues and prs each time
        if len(events) >= 500:
            process_events(events, f"{owner}/{repo}: Event task", repo_id, logger)
            events.clear()

    if events:
        process_events(events, f"{owner}/{repo}: Event task", repo_id, logger)


def bulk_events_collection_endpoint_contains_all_data(key_auth, logger, owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"

    github_data_access = GithubDataAccess(key_auth, logger)

    page_count = github_data_access.get_resource_page_count(url)

    if page_count > 300:
        raise Exception(f"Either github raised the paginator page limit for things like events and messages, or is_pagination_limited_by_max_github_pages is being used on a resource that does not have a page limit. Url: {url}")

    return page_count != 300


def bulk_collect_pr_and_issue_events(repo_git: str, logger, key_auth):

    owner, repo = get_owner_repo(repo_git)

    logger.debug(f"Collecting Github events for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
        
    github_data_access = GithubDataAccess(key_auth, logger)

    return github_data_access.paginate_resource(url)


def collect_pr_and_issues_events_by_number(repo_id, repo_git: str, logger, key_auth, task_name) -> None:

    owner, repo = get_owner_repo(repo_git)

    # define logger for task
    logger.debug(f"Collecting github events for {owner}/{repo}")

    engine = get_engine()

    with engine.connect() as connection:

        query = text(f"""
            (select pr_src_number as number from pull_requests WHERE repo_id={repo_id} order by pr_created_at desc)
            UNION
            (select gh_issues_number as number from issues WHERE repo_id={repo_id} order by created_at desc);
        """)

        result = connection.execute(query).fetchall()
    numbers = [x[0] for x in result]

    github_data_access = GithubDataAccess(key_auth, logger)
    for number in numbers:

        event_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}/events"
        
        yield from github_data_access.paginate_resource(event_url)

def process_events(events, task_name, repo_id, logger):
    
    tool_source = "Github events task"
    tool_version = "2.0"
    data_source = "Github API"
   
    pr_event_dicts = []
    issue_event_dicts = []
    contributors = []


    # create mapping from issue url to issue id of current issues
    issue_url_to_id_map = {}
    issues = get_issues_by_repo_id(repo_id)
    for issue in issues:
        issue_url_to_id_map[issue.issue_url] = issue.issue_id

    # create mapping from pr url to pr id of current pull requests
    pr_url_to_id_map = {}
    prs = get_pull_requests_by_repo_id(repo_id)
    for pr in prs:
        pr_url_to_id_map[pr.pr_url] = pr.pull_request_id

    not_mapable_event_count = 0
    event_len = len(events)
    for event in events:

        event, contributor = process_github_event_contributors(logger, event, tool_source, tool_version, data_source)

        # event_mapping_data is the pr or issue data needed to relate the event to an issue or pr
        event_mapping_data = event["issue"]

        if event_mapping_data is None:
            not_mapable_event_count += 1
            continue

        pull_request = event_mapping_data.get('pull_request', None)
        if pull_request:
            pr_url = pull_request["url"]

            try:
                pull_request_id = pr_url_to_id_map[pr_url]

                # query = augur_db.session.query(PullRequest).filter(PullRequest.pr_url == pr_url)
                # related_pr = execute_session_query(query, 'one')
            except KeyError:
                logger.warning(f"{task_name}: Could not find related pr. We were searching for: {pr_url}")
                continue

            pr_event_dicts.append(
                extract_pr_event_data(event, pull_request_id, platform_id, repo_id,
                                    tool_source, tool_version, data_source)
            )

        else:
            issue_url = event_mapping_data["url"]

            try:
                issue_id = issue_url_to_id_map[issue_url]
                # query = augur_db.session.query(Issue).filter(Issue.issue_url == issue_url)
                # related_issue = execute_session_query(query, 'one')
            except KeyError:
                logger.warning(f"{task_name}: Could not find related issue. We were searching for: {issue_url}")
                continue

            issue_event_dicts.append(
                extract_issue_event_data(event, issue_id, platform_id, repo_id,
                                        tool_source, tool_version, data_source)
            )
        
        # add contributor to list after porcessing the event, 
        # so if it fails processing for some reason the contributor is not inserted
        # NOTE: contributor is none when there is no contributor data on the event
        if contributor:
            contributors.append(contributor)

    # remove contributors that were found in the data more than once
    contributors = remove_duplicate_dicts(contributors)

    bulk_insert_dicts(logger, contributors, Contributor, ["cntrb_id"])

    issue_events_len = len(issue_event_dicts)
    pr_events_len = len(pr_event_dicts)
    if event_len != (issue_events_len + pr_events_len):

        unassigned_events = event_len - issue_events_len - pr_events_len

        logger.error(f"{task_name}: {event_len} events were processed, but {pr_events_len} pr events were found and related to a pr, and {issue_events_len} issue events were found and related to an issue. {not_mapable_event_count} events were not related to a pr or issue due to the api returning insufficient data. For some reason {unassigned_events} events were not able to be processed even when the api returned sufficient data. This is usually because pull requests or issues have not been collected, and the events are skipped because they cannot be related to a pr or issue")

    logger.info(f"{task_name}: Inserting {len(pr_event_dicts)} pr events and {len(issue_event_dicts)} issue events")

    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["node_id"]
    bulk_insert_dicts(logger, pr_event_dicts, PullRequestEvent, pr_event_natural_keys)

    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    bulk_insert_dicts(logger, issue_event_dicts, IssueEvent, issue_event_natural_keys)

    update_issue_closed_cntrbs_by_repo_id(repo_id)

# TODO: Should we skip an event if there is no contributor to resolve it o
def process_github_event_contributors(logger, event, tool_source, tool_version, data_source):

    if event["actor"]:

        event_cntrb = extract_needed_contributor_data(event["actor"], tool_source, tool_version, data_source)
        event["cntrb_id"] = event_cntrb["cntrb_id"]

    else:
        event["cntrb_id"] = None
        return event, None
    
    return event, event_cntrb

