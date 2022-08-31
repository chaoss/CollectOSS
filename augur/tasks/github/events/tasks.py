import time
import logging


from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import wait_child_tasks
from augur.tasks.github.util.util import remove_duplicate_dicts, get_owner_repo
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo

platform_id = 1

@celery.task
def collect_events(repo_id: int):

    logger = logging.getLogger(collect_events.__name__)
    
        # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger) as session:

        repo_obj = session.query(Repo).filter(Repo.repo_id == repo_id).one()
        repo_id = repo_obj.repo_id
        repo_git = repo_obj.repo_git
        owner, repo = get_owner_repo(repo_git)

        logger.info(f"Collecting Github events for {owner}/{repo}")

        url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
        # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
        events = GithubPaginator(url, session.oauths, logger)

    index = 0

    num_pages = events.get_num_pages()
    ids = []
    for page_data, page in events.iter_pages():

        if page_data is None:
            return
            
        elif len(page_data) == 0:
            logger.debug(f"{repo.capitalize()} Events Page {page} contains no data...returning")
            logger.info(f"Events Page {page} of {num_pages}")
            return

        process_events_task = process_events.s(page_data, f"{repo.capitalize()} Events Page {page} Task", repo_id).apply_async()
        ids.append(process_events_task.id)

    wait_child_tasks(ids)
        

@celery.task
def process_events(events, task_name, repo_id):

    logger = logging.getLogger(process_events.__name__)
    
    tool_source = "Github events task"
    tool_version = "2.0"
    data_source = "Github API"
   
    pr_event_dicts = []
    issue_event_dicts = []
    contributors = []

    with GithubTaskSession(logger) as session:

        event_len = len(events)
        for index, event in enumerate(events):

            event, contributor = process_github_event_contributors(logger, event, tool_source, tool_version, data_source)

            if 'pull_request' in list(event["issue"].keys()):
                pr_url = event["issue"]["pull_request"]["url"]

                try:
                    start_time = time.time()
                    related_pr = session.query(PullRequest).filter(PullRequest.pr_url == pr_url).one()
                except s.orm.exc.NoResultFound:
                    logger.info("Could not find related pr")
                    logger.info(f"We were searching for: {pr_url}")
                    # TODO: Add table to log all errors
                    logger.info("Skipping")
                    continue

                pr_event_dicts.append(
                    extract_pr_event_data(event, related_pr.pull_request_id, platform_id, repo_id,
                                        tool_source, tool_version, data_source)
                )

            else:
                issue_url = event["issue"]["url"]

                try:
                    start_time = time.time()
                    related_issue = session.query(Issue).filter(Issue.issue_url == issue_url).one()
                except s.orm.exc.NoResultFound:
                    logger.info("Could not find related pr")
                    logger.info(f"We were searching for: {issue_url}")
                    # TODO: Add table to log all errors
                    logger.info("Skipping")
                    continue

                issue_event_dicts.append(
                    extract_issue_event_data(event, related_issue.issue_id, platform_id, repo_id,
                                            tool_source, tool_version, data_source)
                )
            
            # add contributor to list after porcessing the event, 
            # so if it fails processing for some reason the contributor is not inserted
            # NOTE: contributor is none when there is no contributor data on the event
            if contributor:
                contributors.append(contributor)

        # remove contributors that were found in the data more than once
        contributors = remove_duplicate_dicts(contributors)

        session.insert_data(contributors, Contributor, ["cntrb_login"])

        issue_events_len = len(issue_event_dicts)
        pr_events_len = len(pr_event_dicts)
        if event_len != (issue_events_len + pr_events_len):

            unassigned_events = event_len - issue_events_len - pr_events_len

            logger.error(f"{task_name}: {event_len} events were processed, but {pr_events_len} pr events were found and related to a pr, and {issue_events_len} issue events were found and related to an issue. For some reason {unassigned_events} events were not able to be processed. This is usually because pull requests or issues have not been collected, and the events are skipped because they cannot be related to a pr or issue")

        logger.info(f"{task_name}: Inserting {len(pr_event_dicts)} pr events and {len(issue_event_dicts)} issue events")

        # TODO: Could replace this with "id" but it isn't stored on the table for some reason
        pr_event_natural_keys = ["node_id"]
        session.insert_data(pr_event_dicts, PullRequestEvent, pr_event_natural_keys)

        issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
        session.insert_data(issue_event_dicts, IssueEvent, issue_event_natural_keys)


# TODO: Should we skip an event if there is no contributor to resolve it o
def process_github_event_contributors(logger, event, tool_source, tool_version, data_source):

    if event["actor"]:

        event_cntrb = extract_needed_contributor_data(event["actor"], tool_source, tool_version, data_source)
        event["cntrb_id"] = event_cntrb["cntrb_id"]

    else:
        event["cntrb_id"] = None
        return event, None
    
    return event, event_cntrb
