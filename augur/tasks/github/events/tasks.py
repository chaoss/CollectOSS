import logging
import traceback
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator
from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.tasks.github.util.util import get_owner_repo
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.application.db.models import PullRequest, PullRequestEvent, Issue, IssueEvent, Contributor
from augur.application.db.lib import get_repo_by_repo_git, bulk_insert_dicts

platform_id = 1

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_events(repo_git: str):

    logger = logging.getLogger(collect_events.__name__)
    
    try:
        
        repo_obj = get_repo_by_repo_git(repo_git)
        repo_id = repo_obj.repo_id

        owner, repo = get_owner_repo(repo_git)

        logger.info(f"Collecting Github events for {owner}/{repo}")

        with GithubTaskManifest(logger) as manifest:

            event_data = retrieve_all_event_data(repo_git, logger, manifest.key_auth)

            if event_data:
                process_events(event_data, f"{owner}/{repo}: Event task", repo_id, logger, manifest.augur_db)
            else:
                logger.info(f"{owner}/{repo} has no events")

    except Exception as e:
        logger.error(f"Could not collect events for {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")


def retrieve_all_event_data(repo_git: str, logger, key_auth):

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting Github events for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
        
    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    events = GithubPaginator(url, key_auth, logger)


    num_pages = events.get_num_pages()
    all_data = []
    for page_data, page in events.iter_pages():

        if page_data is None:
            return all_data
            
        elif len(page_data) == 0:
            logger.debug(f"{repo.capitalize()} Events Page {page} contains no data...returning")
            logger.info(f"Events Page {page} of {num_pages}")
            return all_data

        logger.info(f"{repo} Events Page {page} of {num_pages}")

        all_data += page_data

    return all_data        

def process_events(events, task_name, repo_id, logger, augur_db):
    
    tool_source = "Github events task"
    tool_version = "2.0"
    data_source = "Github API"
   
    pr_event_dicts = []
    issue_event_dicts = []
    contributors = []


    # create mapping from issue url to issue id of current issues
    issue_url_to_id_map = {}
    issues = augur_db.session.query(Issue).filter(Issue.repo_id == repo_id).all()
    for issue in issues:
        issue_url_to_id_map[issue.issue_url] = issue.issue_id

    # create mapping from pr url to pr id of current pull requests
    pr_url_to_id_map = {}
    prs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
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
                logger.info(f"{task_name}: Could not find related pr")
                logger.info(f"{task_name}: We were searching for: {pr_url}")
                logger.info(f"{task_name}: Skipping")
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
                logger.info(f"{task_name}: Could not find related pr")
                logger.info(f"{task_name}: We were searching for: {issue_url}")
                logger.info(f"{task_name}: Skipping")
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

    bulk_insert_dicts(contributors, Contributor, ["cntrb_id"])

    issue_events_len = len(issue_event_dicts)
    pr_events_len = len(pr_event_dicts)
    if event_len != (issue_events_len + pr_events_len):

        unassigned_events = event_len - issue_events_len - pr_events_len

        logger.error(f"{task_name}: {event_len} events were processed, but {pr_events_len} pr events were found and related to a pr, and {issue_events_len} issue events were found and related to an issue. {not_mapable_event_count} events were not related to a pr or issue due to the api returning insufficient data. For some reason {unassigned_events} events were not able to be processed even when the api returned sufficient data. This is usually because pull requests or issues have not been collected, and the events are skipped because they cannot be related to a pr or issue")

    logger.info(f"{task_name}: Inserting {len(pr_event_dicts)} pr events and {len(issue_event_dicts)} issue events")

    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["node_id"]
    bulk_insert_dicts(pr_event_dicts, PullRequestEvent, pr_event_natural_keys)

    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    bulk_insert_dicts(issue_event_dicts, IssueEvent, issue_event_natural_keys)

    update_issue_closed_cntrbs_from_events(augur_db.engine, repo_id)

# TODO: Should we skip an event if there is no contributor to resolve it o
def process_github_event_contributors(logger, event, tool_source, tool_version, data_source):

    if event["actor"]:

        event_cntrb = extract_needed_contributor_data(event["actor"], tool_source, tool_version, data_source)
        event["cntrb_id"] = event_cntrb["cntrb_id"]

    else:
        event["cntrb_id"] = None
        return event, None
    
    return event, event_cntrb


def update_issue_closed_cntrbs_from_events(engine, repo_id):

    get_ranked_issues = s.text(f"""
        WITH RankedIssues AS (
            SELECT repo_id, issue_id, cntrb_id, 
                ROW_NUMBER() OVER(PARTITION BY issue_id ORDER BY created_at DESC) AS rn
            FROM issue_events 
            WHERE "action" = 'closed'
        )
                                            
        SELECT issue_id, cntrb_id from RankedIssues where rn=1 and repo_id={repo_id} and cntrb_id is not NULL
    """)

    with engine.connect() as conn:
        result = conn.execute(get_ranked_issues).fetchall()

    update_data = []
    for row in result:
        update_data.append(
            {
            'issue_id': row[0], 
            'cntrb_id': row[1], 
            'repo_id': repo_id
            }
        )

    if update_data:
        with engine.connect() as connection:
            update_stmt = s.text("""
                UPDATE issues
                SET cntrb_id = :cntrb_id
                WHERE issue_id = :issue_id
                AND repo_id = :repo_id
            """)
            connection.execute(update_stmt, update_data)


