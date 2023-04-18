import time
import logging
import traceback

from augur.tasks.github.pull_requests.core import extract_data_from_pr_list
from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask, AugurSecondaryRepoCollectionTask
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskManifest
from augur.application.db.session import DatabaseSession
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.tasks.github.util.util import add_key_value_pair_to_dicts, get_owner_repo
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, PullRequestMessageRef, Contributor, Repo
from augur.application.db.util import execute_session_query
from ..messages.tasks import process_github_comment_contributors


platform_id = 1


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_pull_requests(repo_git: str) -> int:

    logger = logging.getLogger(collect_pull_requests.__name__)

    with GithubTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        repo_id = augur_db.session.query(Repo).filter(
        Repo.repo_git == repo_git).one().repo_id

        owner, repo = get_owner_repo(repo_git)
        pr_data = retrieve_all_pr_data(repo_git, logger, manifest.key_auth)

        if pr_data:
            process_pull_requests(pr_data, f"{owner}/{repo}: Pr task", repo_id, logger, augur_db)

            return len(pr_data)
        else:
            logger.info(f"{owner}/{repo} has no pull requests")
            return 0
        
    
# TODO: Rename pull_request_reviewers table to pull_request_requested_reviewers
# TODO: Fix column names in pull request labels table
def retrieve_all_pr_data(repo_git: str, logger, key_auth) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    # returns an iterable of all prs at this url (this essentially means you can treat the prs variable as a list of the prs)
    prs = GithubPaginator(url, key_auth, logger)

    all_data = []
    num_pages = prs.get_num_pages()
    for page_data, page in prs.iter_pages():

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo} Prs Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo} Prs Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo} Prs Page {page} of {num_pages}")

        all_data += page_data

    return all_data

    
def process_pull_requests(pull_requests, task_name, repo_id, logger, augur_db):

    tool_source = "Pr Task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_dicts, pr_mapping_data, pr_numbers, contributors = extract_data_from_pr_list(pull_requests, repo_id, tool_source, tool_version, data_source)

    # remove duplicate contributors before inserting
    contributors = remove_duplicate_dicts(contributors)

    # insert contributors from these prs
    logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
    augur_db.insert_data(contributors, Contributor, ["cntrb_id"])


    # insert the prs into the pull_requests table. 
    # pr_urls are gloablly unique across github so we are using it to determine whether a pull_request we collected is already in the table
    # specified in pr_return_columns is the columns of data we want returned. This data will return in this form; {"pr_url": url, "pull_request_id": id}
    logger.info(f"{task_name}: Inserting prs of length: {len(pr_dicts)}")
    pr_natural_keys = ["repo_id", "pr_src_id"]
    pr_return_columns = ["pull_request_id", "pr_url"]
    pr_string_fields = ["pr_src_title", "pr_body"]
    pr_return_data = augur_db.insert_data(pr_dicts, PullRequest, pr_natural_keys, 
                            return_columns=pr_return_columns, string_fields=pr_string_fields)

    if pr_return_data is None:
        return


    # loop through the pr_return_data (which is a list of pr_urls 
    # and pull_request_id in dicts) so we can find the labels, 
    # assignees, reviewers, and assignees that match the pr
    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []
    for data in pr_return_data:

        pr_url = data["pr_url"]
        pull_request_id = data["pull_request_id"]

        try:
            other_pr_data = pr_mapping_data[pr_url]
        except KeyError as e:
            logger.info(f"Cold not find other pr data. This should never happen. Error: {e}")


        # add the pull_request_id to the labels, assignees, reviewers, or metadata then add them to a list of dicts that will be inserted soon
        dict_key = "pull_request_id"
        pr_label_dicts += add_key_value_pair_to_dicts(other_pr_data["labels"], dict_key, pull_request_id)
        pr_assignee_dicts += add_key_value_pair_to_dicts(other_pr_data["assignees"], dict_key, pull_request_id)
        pr_reviewer_dicts += add_key_value_pair_to_dicts(other_pr_data["reviewers"], dict_key, pull_request_id)
        pr_metadata_dicts += add_key_value_pair_to_dicts(other_pr_data["metadata"], dict_key, pull_request_id)
        

    logger.info(f"{task_name}: Inserting other pr data of lengths: Labels: {len(pr_label_dicts)} - Assignees: {len(pr_assignee_dicts)} - Reviewers: {len(pr_reviewer_dicts)} - Metadata: {len(pr_metadata_dicts)}")

    # inserting pr labels
    # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    pr_label_string_fields = ["pr_src_description"]
    augur_db.insert_data(pr_label_dicts, PullRequestLabel, pr_label_natural_keys, string_fields=pr_label_string_fields)

    # inserting pr assignees
    # we are using pr_assignee_src_id and pull_request_id to determine if the label is already in the database.
    pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    augur_db.insert_data(pr_assignee_dicts, PullRequestAssignee, pr_assignee_natural_keys)


    # inserting pr requested reviewers
    # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
    pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
    augur_db.insert_data(pr_reviewer_dicts, PullRequestReviewer, pr_reviewer_natural_keys)
    
    # inserting pr metadata
    # we are using pull_request_id, pr_head_or_base, and pr_sha to determine if the label is already in the database.
    pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
    pr_metadata_string_fields = ["pr_src_meta_label"]
    augur_db.insert_data(pr_metadata_dicts, PullRequestMeta,
                        pr_metadata_natural_keys, string_fields=pr_metadata_string_fields)





















def process_pull_request_review_contributor(pr_review: dict, tool_source: str, tool_version: str, data_source: str):

    # get contributor data and set pr cntrb_id
    user = pr_review["user"]
    if user is None:
        return None
    
    pr_review_cntrb = extract_needed_contributor_data(user, tool_source, tool_version, data_source)
    pr_review["cntrb_id"] = pr_review_cntrb["cntrb_id"]

    return pr_review_cntrb


@celery.task(base=AugurSecondaryRepoCollectionTask)
def collect_pull_request_review_comments(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    review_msg_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    logger = logging.getLogger(collect_pull_request_review_comments.__name__)
    logger.info(f"Collecting pull request review comments for {owner}/{repo}")

    # define GithubTaskSession to handle insertions, and store oauth keys
    with GithubTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        # get repo_id
        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

        query = augur_db.session.query(PullRequestReview).filter(PullRequestReview.repo_id == repo_id)
        pr_reviews = execute_session_query(query, 'all')

        # maps the github pr_review id to the auto incrementing pk that augur stores as pr_review id
        pr_review_id_mapping = {}
        for review in pr_reviews:
            pr_review_id_mapping[review.pr_review_src_id] = review.pr_review_id


        tool_source = "Pr review comment task"
        tool_version = "2.0"
        data_source = "Github API"

        pr_review_messages = GithubPaginator(review_msg_url, manifest.key_auth, logger)
        num_pages = pr_review_messages.get_num_pages()

        all_raw_pr_review_messages = []
        for page_data, page in pr_review_messages.iter_pages():

            if page_data is None:
                break

            if len(page_data) == 0:
                logger.debug(f"{owner}/{repo} Pr Review Messages Page {page} contains no data...returning")
                logger.info(f"{owner}/{repo} Pr Review Messages Page {page} of {num_pages}")
                break

            logger.info(f"{owner}/{repo} Pr Review Messages Page {page} of {num_pages}")

            all_raw_pr_review_messages += page_data

        contributors = []
        for comment in all_raw_pr_review_messages:
            
            _, contributor = process_github_comment_contributors(comment, tool_source, tool_version, data_source)
            if contributor is not None:
                contributors.append(contributor)

        logger.info(f"{owner}/{repo} Pr review messages: Inserting {len(contributors)} contributors")
        augur_db.insert_data(contributors, Contributor, ["cntrb_id"])


        pr_review_comment_dicts = []
        pr_review_msg_mapping_data = {}

        pr_review_comments_len = len(all_raw_pr_review_messages)
        logger.info(f"{owner}/{repo}: Pr review comments len: {pr_review_comments_len}")
        for index, comment in enumerate(all_raw_pr_review_messages):

            # pull_request_review_id is required to map it to the correct pr review
            if not comment["pull_request_review_id"]:
                continue

            pr_review_comment_dicts.append(
                                    extract_needed_message_data(comment, platform_id, repo_id, tool_source, tool_version, data_source)
            )

            # map github message id to the data that maps it to the pr review
            github_msg_id = comment["id"]
            pr_review_msg_mapping_data[github_msg_id] = comment



        logger.info(f"Inserting {len(pr_review_comment_dicts)} pr review comments")
        message_natural_keys = ["platform_msg_id"]
        message_return_columns = ["msg_id", "platform_msg_id"]
        message_return_data = augur_db.insert_data(pr_review_comment_dicts, Message, message_natural_keys, message_return_columns)
        if message_return_data is None:
            return


        pr_review_message_ref_insert_data = []
        for data in message_return_data:

            augur_msg_id = data["msg_id"]
            github_msg_id = data["platform_msg_id"]

            comment = pr_review_msg_mapping_data[github_msg_id]
            comment["msg_id"] = augur_msg_id

            github_pr_review_id = comment["pull_request_review_id"]

            try:
                augur_pr_review_id = pr_review_id_mapping[github_pr_review_id]
            except KeyError:
                logger.info(f"{owner}/{repo}: Could not find related pr review")
                logger.info(f"{owner}/{repo}: We were searching for pr review with id: {github_pr_review_id}")
                logger.info("Skipping")
                continue

            pr_review_message_ref = extract_pr_review_message_ref_data(comment, augur_pr_review_id, github_pr_review_id, repo_id, tool_version, data_source)
            pr_review_message_ref_insert_data.append(pr_review_message_ref)


        logger.info(f"Inserting {len(pr_review_message_ref_insert_data)} pr review refs")
        pr_comment_ref_natural_keys = ["pr_review_msg_src_id"]
        augur_db.insert_data(pr_review_message_ref_insert_data, PullRequestReviewMessageRef, pr_comment_ref_natural_keys)




@celery.task(base=AugurSecondaryRepoCollectionTask)
def collect_pull_request_reviews(repo_git: str) -> None:

    logger = logging.getLogger(collect_pull_request_reviews.__name__)

    owner, repo = get_owner_repo(repo_git)

    tool_version = "2.0"
    tool_source = "pull_request_reviews"
    data_source = "Github API"

    with GithubTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

        query = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).order_by(PullRequest.pr_src_number)
        prs = execute_session_query(query, 'all')

        pr_count = len(prs)

        all_raw_pr_reviews = []
        for index, pr in enumerate(prs):

            pr_number = pr.pr_src_number
            pull_request_id = pr.pull_request_id

            logger.info(f"{owner}/{repo} Collecting Pr Reviews for pr {index + 1} of {pr_count}")

            pr_review_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

            pr_reviews = GithubPaginator(pr_review_url, manifest.key_auth, logger)

            for page_data, page in pr_reviews.iter_pages():

                if page_data is None:
                    break

                if len(page_data) == 0:
                    break

                all_raw_pr_reviews.extend(page_data)

        if not all_raw_pr_reviews:
            logger.info(f"{owner}/{repo} No pr reviews for repo")
            return

        contributors = []
        for raw_pr_review in all_raw_pr_reviews:
            contributor = process_pull_request_review_contributor(raw_pr_review, tool_source, tool_version, data_source)
            if contributor:
                contributors.append(contributor)

        logger.info(f"{owner}/{repo} Pr reviews: Inserting {len(contributors)} contributors")
        augur_db.insert_data(contributors, Contributor, ["cntrb_id"])


        pr_reviews = []
        for raw_pr_review in all_raw_pr_reviews:

            logger.info(f"Pr review type: {type(raw_pr_review)}")
            logger.info(raw_pr_review)

            if "cntrb_id" in raw_pr_review:
                pr_reviews.append(extract_needed_pr_review_data(raw_pr_review, pull_request_id, repo_id, platform_id, tool_source, tool_version))

        logger.info(f"{owner}/{repo}: Inserting pr reviews of length: {len(pr_reviews)}")
        pr_review_natural_keys = ["pr_review_src_id",]
        augur_db.insert_data(pr_reviews, PullRequestReview, pr_review_natural_keys)


















