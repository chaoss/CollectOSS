import time
import logging


from augur.tasks.init.celery_app import celery_app as celery, engine
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import wait_child_tasks
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo
from augur.application.db.util import execute_session_query


@celery.task
def process_contributors():

    logger = logging.getLogger(process_contributors.__name__)

    tool_source = "Contributors task"
    tool_version = "2.0"
    data_source = "Github API"

    with GithubTaskSession(logger, engine) as session:

        query = session.query(Contributor).filter(Contributor.data_source == data_source, Contributor.cntrb_created_at is None, Contributor.cntrb_last_used is None)
        contributors = execute_session_query(query, 'all')

        contributors_len = len(contributors)

        if contributors_len == 0:
            logger.info("No contributors to enrich...returning...")
            return

        print(f"Length of contributors to enrich: {contributors_len}")
        enriched_contributors = []
        for index, contributor in enumerate(contributors):

            logger.info(f"Contributor {index + 1} of {contributors_len}")

            contributor_dict = contributor.__dict__

            del contributor_dict["_sa_instance_state"]

            url = f"https://api.github.com/users/{contributor_dict['cntrb_login']}" 

            data = retrieve_dict_data(url, session)

            if data is None:
                print(f"Unable to get contributor data for: {contributor_dict['cntrb_login']}")
                continue

            new_contributor_data = {
                "cntrb_created_at": data["created_at"],
                "cntrb_last_used": data["updated_at"]
            }

            contributor_dict.update(new_contributor_data)

            enriched_contributors.append(contributor_dict)

        logger.info(f"Enriching {len(enriched_contributors)} contributors")
        session.insert_data(enriched_contributors, Contributor, ["cntrb_id"])



def retrieve_dict_data(url: str, session):

    num_attempts = 0
    while num_attempts <= 10:

        response = hit_api(session.oauths, url, session.logger)

        # increment attempts
        if response is None:
            num_attempts += 1
            continue
        # update rate limit here

        page_data = response.json()

        if "message" in page_data:

            if page_data['message'] == "Not Found":
                session.logger.info(
                    "Github repo was not found or does not exist for endpoint: "
                    f"{response.url}\n"
                )
                break

            elif "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in page_data['message']:
                session.logger.info('\n\n\n\nSleeping for 100 seconds due to secondary rate limit issue.\n\n\n\n')
                time.sleep(100)
                continue

            elif "You have triggered an abuse detection mechanism." in page_data['message']:
                #self.update_rate_limit(response, temporarily_disable=True,platform=platform)
                continue
        else:
            return page_data


    return None




