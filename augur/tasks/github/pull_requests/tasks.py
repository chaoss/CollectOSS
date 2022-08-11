import time
import logging

from augur import queue_name
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.data_parse import *
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.tasks.util.worker_util import wait_child_tasks
from augur.tasks.github.util.util import remove_duplicate_dicts, add_key_value_pair_to_list_of_dicts, get_owner_repo
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo

platform_id = 1

# TODO: Rename pull_request_reviewers table to pull_request_requested_reviewers
# TODO: Fix column names in pull request labels table
@celery.task
def collect_pull_requests(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_pull_requests.__name__)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"

    # define GithubTaskSession to handle insertions, and store oauth keys 
    with GithubTaskSession(logger) as session:

        repo_id = session.query(Repo).filter(Repo.repo_git == repo_git).one().repo_id

        # returns an iterable of all prs at this url (this essentially means you can treat the prs variable as a list of the prs)
        prs = GithubPaginator(url, session.oauths, logger)

    num_pages = prs.get_num_pages()
    ids = []
    for page_data, page in prs.iter_pages():

        if page_data == None:
            return

        elif len(page_data) == 0:
            logger.debug(f"{repo.capitalize()} Prs Page {page} contains no data...returning")
            logger.info(f"{repo.capitalize()} Prs Page {page} of {num_pages}")
            return

    
        process_pr_task = process_pull_requests.s(page_data, f"{repo.capitalize()} Pr Page {page} Task", repo_id).apply_async()
        ids.append(process_pr_task.id)

    wait_child_tasks(ids)

@celery.task
def process_pull_requests(pull_requests, task_name, repo_id):

    logger = logging.getLogger(process_pull_requests.__name__)

     # get repo_id or have it passed
    tool_source = "Pr Task"
    tool_version = "2.0"
    data_source = "Github API"

    pr_dicts = []
    pr_mapping_data = {}
    pr_numbers = []
    contributors = []

    for index, pr in enumerate(pull_requests):

        # adds cntrb_id to reference the contributors table to the 
        # prs, assignees, reviewers, and metadata
        pr, contributor_data = process_pull_request_contributors(pr, tool_source, tool_version, data_source)

        contributors += contributor_data

        # add a field called pr_head_or_base to the head and base field of the pr
        # this is done so we can insert them both into the pr metadata table
        # and still determine whether it is a head or base
        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )

        # add metadata field to pr
        pr.update(
            {"metadata": [pr["head"], pr["base"]]}
        )

        # create list of pr_dicts to bulk insert later
        pr_dicts.append(
                    # get only the needed data for the pull_requests table
                    extract_needed_pr_data(pr, repo_id, tool_source,tool_version)
        )

        # get only the needed data for the pull_request_labels table
        pr_labels = extract_needed_pr_label_data(pr["labels"],  platform_id, repo_id,
                                                       tool_source, tool_version, data_source)

        # get only the needed data for the pull_request_assignees table
        pr_assignees = extract_needed_pr_assignee_data(pr["assignees"], platform_id, repo_id,
                                                             tool_source, tool_version, data_source)

        # get only the needed data for the pull_request_reviewers table
        pr_reviewers = extract_needed_pr_reviewer_data(pr["requested_reviewers"], platform_id, repo_id,
                                                             tool_source, tool_version, data_source)

        # get only the needed data for the pull_request_meta table
        pr_metadata = extract_needed_pr_metadata(pr["metadata"], platform_id, repo_id,
                                                        tool_source, tool_version, data_source)                                                             

                               

        mapping_data_key = pr["url"]
        pr_mapping_data[mapping_data_key] = {
                                            "labels": pr_labels,
                                            "assignees": pr_assignees,
                                            "reviewers": pr_reviewers,
                                            "metadata": pr_metadata,
                                            "contributor": pr["user"]
                                            }          
       

        # create a list of pr numbers to pass for the pr reviews task
        pr_numbers.append(pr["number"]) 

    with GithubTaskSession(logger) as session:

        # remove duplicate contributors before inserting
        contributors = remove_duplicate_dicts(contributors)

        # insert contributors from these issues
        logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
        session.insert_data(contributors, Contributor, ["cntrb_login"])


        # insert the prs into the pull_requests table. 
        # pr_urls are gloablly unique across github so we are using it to determine whether a pull_request we collected is already in the table
        # specified in pr_return_columns is the columns of data we want returned. This data will return in this form; {"pr_url": url, "pull_request_id": id}
        logger.info(f"{task_name}: Inserting prs of length: {len(pr_dicts)}")
        pr_natural_keys = ["pr_url"]
        pr_return_columns = ["pull_request_id", "pr_url"]
        pr_return_data = session.insert_data(pr_dicts, PullRequest, pr_natural_keys, return_columns=pr_return_columns)

        if pr_return_data is None:
            return


        # loop through the pr_return_data (which is a list of pr_urls 
        # and pull_request_id in dicts) so we can find the labels, 
        # assignees, reviewers, and assignees that match the pr
        pr_label_dicts = []
        pr_assignee_dicts = []
        pr_reviewer_dicts = []
        pr_metadata_dicts = []
        pr_contributors = []
        for data in pr_return_data:

            pr_url = data["pr_url"]
            pull_request_id = data["pull_request_id"]

            try:
                other_pr_data = pr_mapping_data[pr_url]
            except KeyError as e:
                logger.info(f"Cold not find other pr data. This should never happen. Error: {e}")


            # add the pull_request_id to the labels, assignees, reviewers, or metadata then add them to a list of dicts that will be inserted soon
            dict_key = "pull_request_id"
            pr_label_dicts += add_key_value_pair_to_list_of_dicts(other_pr_data["labels"], dict_key, pull_request_id)
            pr_assignee_dicts += add_key_value_pair_to_list_of_dicts(other_pr_data["assignees"], dict_key, pull_request_id)
            pr_reviewer_dicts += add_key_value_pair_to_list_of_dicts(other_pr_data["reviewers"], dict_key, pull_request_id)
            pr_metadata_dicts += add_key_value_pair_to_list_of_dicts(other_pr_data["metadata"], dict_key, pull_request_id)

            pr_contributors.append(
                {
                "pull_request_id": pull_request_id,
                "contributor": other_pr_data["contributor"]
                }
            )

        # starting task to process pr contributors
        # process_contributors.s(pr_contributors, PullRequests).apply_async()
            

        logger.info(f"{task_name}: Inserting other pr data of lengths: Labels: {len(pr_label_dicts)} - Assignees: {len(pr_assignee_dicts)} - Reviewers: {len(pr_reviewer_dicts)} - Metadata: {len(pr_metadata_dicts)}")

        # inserting pr labels
        # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
        pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
        session.insert_data(pr_label_dicts, PullRequestLabel, pr_label_natural_keys)
    
        # inserting pr assignees
        # we are using pr_assignee_src_id and pull_request_id to determine if the label is already in the database.
        pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
        session.insert_data(pr_assignee_dicts, PullRequestAssignee, pr_assignee_natural_keys)

    
        # inserting pr assignees
        # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
        pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
        session.insert_data(pr_reviewer_dicts, PullRequestReviewer, pr_reviewer_natural_keys)
        
        # inserting pr metadata
        # we are using pull_request_id, pr_head_or_base, and pr_sha to determine if the label is already in the database.
        pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
        session.insert_data(pr_metadata_dicts, PullRequestMeta, pr_metadata_natural_keys)



# TODO: Should we insert metadata without user relation?
# NOTE: For contributor related operations: extract_needed_contributor_data takes a piece of github contributor data
# and creates a cntrb_id (primary key for the contributors table) and gets the data needed for the table
def process_pull_request_contributors(pr, tool_source, tool_version, data_source):

    contributors = []

    # get contributor data and set pr cntrb_id
    pr_cntrb = extract_needed_contributor_data(pr["user"], tool_source, tool_version, data_source)
    pr["cntrb_id"] = pr_cntrb["cntrb_id"]

    contributors.append(pr_cntrb)


    if pr["base"]["user"]:

        # get contributor data and set pr metadat cntrb_id
        pr_meta_base_cntrb = extract_needed_contributor_data(pr["base"]["user"], tool_source, tool_version, data_source)
        pr["base"]["cntrb_id"] = pr_meta_base_cntrb["cntrb_id"]

        contributors.append(pr_meta_base_cntrb)

    if pr["head"]["user"]:

        pr_meta_head_cntrb = extract_needed_contributor_data(pr["head"]["user"], tool_source, tool_version, data_source)
        pr["head"]["cntrb_id"] = pr_meta_head_cntrb["cntrb_id"]

        contributors.append(pr_meta_head_cntrb)

    contributors += [pr_cntrb]

    # set cntrb_id for assignees
    for assignee in pr["assignees"]:

        pr_asignee_cntrb = extract_needed_contributor_data(assignee, tool_source, tool_version, data_source)
        assignee["cntrb_id"] = pr_asignee_cntrb["cntrb_id"]

        contributors.append(pr_asignee_cntrb)


    # set cntrb_id for reviewers
    for reviewer in pr["requested_reviewers"]:

        pr_reviwer_cntrb = extract_needed_contributor_data(reviewer, tool_source, tool_version, data_source)
        reviewer["cntrb_id"] = pr_reviwer_cntrb["cntrb_id"]

        contributors.append(pr_reviwer_cntrb)

    return pr, contributors







































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
    with GithubTaskSession(logger) as session:

        # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
        pr_review_comments = GithubPaginator(url, session.oauths, logger)

        # get repo_id
        repo_id = session.query(Repo).filter(Repo.repo_git == repo_git).one().repo_id


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
                related_pr_review = PullRequestReviews.query.filter_by(pr_review_src_id=pr_review_id).one()

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

            pr_comment_ref = extract_pr_review_message_ref_data(comment, pr_review_id, repo_id, tool_source, tool_version, data_source)

            pr_review_msg_mapping_data.append(
                {
                    "platform_msg_id": message["id"],
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

    with GithubTaskSession(logger) as session:

        repo_id = session.query(Repo).filter(Repo.repo_git == repo_git).one().repo_id

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