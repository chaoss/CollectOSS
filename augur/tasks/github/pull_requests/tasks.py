import time
import logging


from augur.tasks.github.pull_requests.core import extract_data_from_pr_list
from augur.tasks.init.celery_app import celery_app as celery, engine
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.tasks.github.util.util import add_key_value_pair_to_dicts, get_owner_repo
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, PullRequestMessageRef, Contributor, Repo
from augur.application.db.util import execute_session_query


platform_id = 1


@celery.task
def collect_pull_requests(repo_git: str) -> None:

    logger = logging.getLogger(collect_pull_requests.__name__)

    with GithubTaskSession(logger, engine) as session:

        repo_id = session.query(Repo).filter(
            Repo.repo_git == repo_git).one().repo_id

    owner, repo = get_owner_repo(repo_git)
    pr_data = retrieve_all_pr_data(repo_git, logger)

    if pr_data:
        process_pull_requests(pr_data, f"{owner}/{repo}: Pr task", repo_id, logger)
    else:
        logger.info(f"{owner}/{repo} has no pull requests")
    
    
# TODO: Rename pull_request_reviewers table to pull_request_requested_reviewers
# TODO: Fix column names in pull request labels table
def retrieve_all_pr_data(repo_git: str, logger) -> None:

    owner, repo = get_owner_repo(repo_git)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger, engine) as session:

        owner, repo = get_owner_repo(repo_git)

        logger.info(f"Collecting pull requests for {owner}/{repo}")

        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
        # returns an iterable of all prs at this url (this essentially means you can treat the prs variable as a list of the prs)
        prs = GithubPaginator(url, session.oauths, logger)

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

    
def process_pull_requests(pull_requests, task_name, repo_id, logger):

    tool_source = "Pr Task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_dicts, pr_mapping_data, pr_numbers, contributors = extract_data_from_pr_list(pull_requests, repo_id, tool_source, tool_version, data_source)

    with GithubTaskSession(logger, engine) as session:

        # remove duplicate contributors before inserting
        contributors = remove_duplicate_dicts(contributors)

        # insert contributors from these prs
        logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
        session.insert_data(contributors, Contributor, ["cntrb_id"])


        # insert the prs into the pull_requests table. 
        # pr_urls are gloablly unique across github so we are using it to determine whether a pull_request we collected is already in the table
        # specified in pr_return_columns is the columns of data we want returned. This data will return in this form; {"pr_url": url, "pull_request_id": id}
        logger.info(f"{task_name}: Inserting prs of length: {len(pr_dicts)}")
        pr_natural_keys = ["repo_id", "pr_src_id"]
        pr_return_columns = ["pull_request_id", "pr_url"]
        pr_string_fields = ["pr_src_title", "pr_body"]
        pr_return_data = session.insert_data(pr_dicts, PullRequest, pr_natural_keys, 
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
        session.insert_data(pr_label_dicts, PullRequestLabel, pr_label_natural_keys, string_fields=pr_label_string_fields)
    
        # inserting pr assignees
        # we are using pr_assignee_src_id and pull_request_id to determine if the label is already in the database.
        pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
        session.insert_data(pr_assignee_dicts, PullRequestAssignee, pr_assignee_natural_keys)

    
        # inserting pr requested reviewers
        # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
        pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
        session.insert_data(pr_reviewer_dicts, PullRequestReviewer, pr_reviewer_natural_keys)
        
        # inserting pr metadata
        # we are using pull_request_id, pr_head_or_base, and pr_sha to determine if the label is already in the database.
        pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
        pr_metadata_string_fields = ["pr_src_meta_label"]
        session.insert_data(pr_metadata_dicts, PullRequestMeta,
                            pr_metadata_natural_keys, string_fields=pr_metadata_string_fields)










































#*************************************************************
#*************************************************************
#*************************************************************
#*************************************************************
#*************************************************************
#*************************************************************

# IN DEVELOPMENT TASKS

@celery.task
def pull_request_review_comments(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    logger = logging.getLogger(pull_request_review_comments.__name__)
    logger.info(f"Collecting pull request comments for {owner}/{repo}")
    
    # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger, engine) as session:

        # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
        pr_review_comments = GithubPaginator(url, session.oauths, logger)

        # get repo_id
        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id


        tool_source = "Pr review comment task"
        tool_version = "2.0"
        data_source = "Github API"

        pr_review_comment_dicts = []
        pr_review_msg_mapping_data = []

        pr_review_comments_len = len(pr_review_comments)
        logger.info(f"Pr comments len: {pr_review_comments_len}")
        for index, comment in enumerate(pr_review_comments):

            pr_review_id = comment["pull_request_review_id"]

            try:
                related_pr_review = PullRequestReview.query.filter_by(pr_review_src_id=pr_review_id).one()

            # if we cannot find a pr review to relate the message to, then we skip the message and it is not inserted
            except s.orm.exc.NoResultFound:
                logger.info("Could not find related pr")
                logger.info(f"We were searching for pr review with id: {pr_review_id}")
                logger.info("Skipping")
                continue

            pr_review_comment_dicts.append(
                                    extract_needed_message_data(comment, platform_id, repo_id, tool_source, tool_version, data_source)
            )

            pr_review_id = related_pr_review.pr_review_id

            # TODO: Map this like pr labels are to prs
            pr_comment_ref = extract_pr_review_message_ref_data(comment, pr_review_id, repo_id, tool_version, data_source)

            pr_review_msg_mapping_data.append(
                {
                    "platform_msg_id": comment["id"],
                    "msg_ref_data": pr_comment_ref,
                }
            )
        
        logger.info(f"Inserting {len(pr_review_comment_dicts)} pr review comments")
        message_natural_keys = ["platform_msg_id"]
        message_return_columns = ["msg_id", "platform_msg_id"]
        message_return_data = session.insert_data(pr_review_comment_dicts, Message, message_natural_keys, message_return_columns)


        pr_review_message_ref_insert_data = []
        for mapping_data in pr_review_msg_mapping_data:

            value = mapping_data["platform_msg_id"]
            key = "platform_msg_id"

            issue_or_pr_message = find_dict_in_list_of_dicts(message_return_data, key, value)

            if issue_or_pr_message:

                msg_id = issue_or_pr_message["msg_id"]
            else:
                print("Count not find issue or pull request message to map to")
                continue

            message_ref_data = mapping_data["msg_ref_data"]
            message_ref_data["msg_id"] = msg_id 

            pr_review_message_ref_insert_data.append(message_ref_data)
        

        logger.info(f"Inserting {len(pr_review_message_ref_insert_data)} pr review refs")
        pr_comment_ref_natural_keys = ["pr_review_msg_src_id"]
        session.insert_data(pr_review_message_ref_insert_data, PullRequestReviewMessageRef, pr_comment_ref_natural_keys)


# do this task after others because we need to add the multi threading like we did it before
@celery.task
def pull_request_reviews(repo_git: str, pr_number_list: [int]) -> None:

    logger = logging.getLogger(pull_request_reviews.__name__)

    owner, repo = get_owner_repo(repo_git)

    pr_number_list = sorted(pr_number_list, reverse=False) 

    tool_version = "2.0"
    data_source = "Github API"

    with GithubTaskSession(logger, engine) as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_id = execute_session_query(query, 'one').repo_id

        # define GithubTaskSession to handle insertions, and store oauth keys 

        logger.info(f"Collecting pull request reviews for {owner}/{repo}")

        pr_review_dicts = []

        good_pr_numbers = []


        for index, pr_number in enumerate(pr_number_list):


            logger.info(f"Processing pr number: {pr_number}")

            reviews = PullRequest(session, owner, repo, pr_number).get_reviews_collection()

            review_list = list(reviews)

            for review in review_list:
                print(review["comments"])

            pr_review_dicts += extract_need_pr_review_data(reviews, platform_id, repo_id, tool_version, data_source)


        print(len(pr_review_dicts))