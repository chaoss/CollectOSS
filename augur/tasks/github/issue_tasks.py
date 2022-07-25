from celery.result import allow_join_result
import time

from augur.tasks.git.facade_tasks import *
from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.data_parse import *
from augur.tasks.util.AugurUUID import AugurUUID
from augur.tasks.github.util.github_paginator import GithubPaginator, hit_api
from augur.tasks.util.task_session import GithubTaskSession
from augur.application.db.models import PullRequest, Message, PullRequestReview, PullRequestLabel, PullRequestReviewer, PullRequestEvent, PullRequestMeta, PullRequestAssignee, PullRequestReviewMessageRef, Issue, IssueEvent, IssueLabel, IssueAssignee, PullRequestMessageRef, IssueMessageRef, Contributor, Repo

# creates a class that is sub class of the sqlalchemy.orm.Session class that additional methods and fields added to it. 

#NOTICE: A pull request is a type of issue as per Github.
#So this file contains functionality for both prs and issues


@celery.task
def collect_issues(repo_git: str) -> None:

    logger = logging.getLogger(collect_issues.__name__)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

    owner, repo = get_owner_repo(repo_git)

    repo_id = session.query(Repo).filter(Repo.repo_git == repo_git).one().repo_id

    logger.info(f"Collecting issues for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"

    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    # Reference the code documenation for GithubPaginator for more details
    issues = GithubPaginator(url, session.oauths, logger)

    # this is defined so we can decrement it each time 
    # we come across a pr, so at the end we can log how 
    # many issues were collected
    # loop through the issues 
    num_pages = issues.get_num_pages()
    
    for page_data, page in issues.iter_pages():

        logger.info(f"{repo.capitalize()} Issues Page {page} of {num_pages}")

        process_issues.s(page_data, f"{repo.capitalize()} Issues Page {page} Task", repo_id).apply_async()
        

@celery.task
def process_issues(issues, task_name, repo_id) -> None:

    logger = logging.getLogger(process_issues.__name__)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

    # get repo_id or have it passed
    tool_source = "Issue Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"

    issue_dicts = []
    issue_mapping_data = {}
    issue_total = len(issues)
    contributors = []
    for index, issue in enumerate(issues):

        # calls is_valid_pr_block to see if the data is a pr.
        # if it is a pr we skip it because we don't need prs 
        # in the issues table
        if is_valid_pr_block(issue) is True:
            issue_total-=1
            continue

        issue, contributor_data = process_issue_contributors(issue, platform_id, tool_source, tool_version, data_source)

        contributors += contributor_data

        # create list of issue_dicts to bulk insert later
        issue_dicts.append(
            # get only the needed data for the issues table
            extract_needed_issue_data(issue, repo_id, tool_source, tool_version, data_source)
        )

         # get only the needed data for the issue_labels table
        issue_labels = extract_needed_issue_label_data(issue["labels"], repo_id,
                                                       tool_source, tool_version, data_source)

        # get only the needed data for the issue_assignees table
        issue_assignees = extract_needed_issue_assignee_data(issue["assignees"], repo_id,
                                                             tool_source, tool_version, data_source)


        mapping_data_key = issue["url"]
        issue_mapping_data[mapping_data_key] = {
                                            "labels": issue_labels,
                                            "assignees": issue_assignees,
                                            }     

    if len(issue_dicts) == 0:
        print("No issues found while processing")  
        return

    # remove duplicate contributors before inserting
    contributors = remove_duplicate_dicts(contributors)

    # insert contributors from these issues
    logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
    session.insert_data(contributors, Contributor, ["cntrb_login"])
                        

    # insert the issues into the issues table. 
    # issue_urls are gloablly unique across github so we are using it to determine whether an issue we collected is already in the table
    # specified in issue_return_columns is the columns of data we want returned. This data will return in this form; {"issue_url": url, "issue_id": id}
    logger.info(f"{task_name}: Inserting {len(issue_dicts)} issues")
    issue_natural_keys = ["issue_url"]
    issue_return_columns = ["issue_url", "issue_id"]
    issue_return_data = session.insert_data(issue_dicts, Issue, issue_natural_keys, issue_return_columns)


    # loop through the issue_return_data so it can find the labels and 
    # assignees that corelate to the issue that was inserted labels 
    issue_label_dicts = []
    issue_assignee_dicts = []
    for data in issue_return_data:

        issue_url = data["issue_url"]
        issue_id = data["issue_id"]

        try:
            other_issue_data = issue_mapping_data[issue_url]
        except KeyError as e:
            logger.info(f"Cold not find other issue data. This should never happen. Error: {e}")


        # add the issue id to the lables and assignees, then add them to a list of dicts that will be inserted soon
        dict_key = "issue_id"
        issue_label_dicts += add_key_value_pair_to_list_of_dicts(other_issue_data["labels"], "issue_id", issue_id)
        issue_assignee_dicts += add_key_value_pair_to_list_of_dicts(other_issue_data["assignees"], "issue_id", issue_id)


    logger.info(f"{task_name}: Inserting other issue data of lengths: Labels: {len(issue_label_dicts)} - Assignees: {len(issue_assignee_dicts)}")

    # inserting issue labels
    # we are using label_src_id and issue_id to determine if the label is already in the database.
    issue_label_natural_keys = ['label_src_id', 'issue_id']
    session.insert_data(issue_label_dicts, IssueLabel, issue_label_natural_keys)
  
    # inserting issue assignees
    # we are using issue_assignee_src_id and issue_id to determine if the label is already in the database.
    issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
    session.insert_data(issue_assignee_dicts, IssueAssignee, issue_assignee_natural_keys)


def process_issue_contributors(issue, platform_id, tool_source, tool_version, data_source):

    contributors = []

    issue_cntrb = extract_needed_contributor_data(issue["user"], platform_id, tool_source, tool_version, data_source)
    issue["cntrb_id"] = issue_cntrb["cntrb_id"]
    contributors.append(issue_cntrb)

    for assignee in issue["assignees"]:

        issue_assignee_cntrb = extract_needed_contributor_data(issue["user"], platform_id, tool_source, tool_version, data_source)
        assignee["cntrb_id"] = issue_assignee_cntrb["cntrb_id"]
        contributors.append(issue_assignee_cntrb)

    return issue, contributors


# TODO: Rename pull_request_reviewers table to pull_request_requested_reviewers
# TODO: Fix column names in pull request labels table
@celery.task
def collect_pull_requests(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_pull_requests.__name__)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    

    # returns an iterable of all prs at this url (this essentially means you can treat the prs variable as a list of the prs)
    prs = GithubPaginator(url, session.oauths, logger)

    num_pages = prs.get_num_pages()
    
    for page_data, page in prs.iter_pages():

        logger.info(f"Prs Page {page} of {num_pages}")

        process_pull_requests.s(page_data, f"Pr Page {page} Task").apply_async()


@celery.task
def process_pull_requests(pull_requests, task_name):

    logger = logging.getLogger(process_pull_requests.__name__)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

     # get repo_id or have it passed
    repo_id = 1
    tool_source = "Pr Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"

    pr_dicts = []
    pr_mapping_data = {}
    pr_numbers = []
    contributors = []

    for index, pr in enumerate(pull_requests):

        # adds cntrb_id to reference the contributors table to the 
        # prs, assignees, reviewers, and metadata
        pr, contributor_data = process_pull_request_contributors(pr, platform_id, tool_source, tool_version, data_source)

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
def process_pull_request_contributors(pr, platform_id, tool_source, tool_version, data_source):

    contributors = []

    # get contributor data and set pr cntrb_id
    pr_cntrb = extract_needed_contributor_data(pr["user"], platform_id, tool_source, tool_version, data_source)
    pr["cntrb_id"] = pr_cntrb["cntrb_id"]

    contributors.append(pr_cntrb)


    if pr["base"]["user"]:

        # get contributor data and set pr metadat cntrb_id
        pr_meta_base_cntrb = extract_needed_contributor_data(pr["base"]["user"], platform_id, tool_source, tool_version, data_source)
        pr["base"]["cntrb_id"] = pr_meta_base_cntrb["cntrb_id"]

        contributors.append(pr_meta_base_cntrb)

    if pr["head"]["user"]:

        pr_meta_head_cntrb = extract_needed_contributor_data(pr["head"]["user"], platform_id, tool_source, tool_version, data_source)
        pr["head"]["cntrb_id"] = pr_meta_head_cntrb["cntrb_id"]

        contributors.append(pr_meta_head_cntrb)

    contributors += [pr_cntrb]

    # set cntrb_id for assignees
    for assignee in pr["assignees"]:

        pr_asignee_cntrb = extract_needed_contributor_data(assignee, platform_id, tool_source, tool_version, data_source)
        assignee["cntrb_id"] = pr_asignee_cntrb["cntrb_id"]

        contributors.append(pr_asignee_cntrb)


    # set cntrb_id for reviewers
    for reviewer in pr["requested_reviewers"]:

        pr_reviwer_cntrb = extract_needed_contributor_data(reviewer, platform_id, tool_source, tool_version, data_source)
        reviewer["cntrb_id"] = pr_reviwer_cntrb["cntrb_id"]

        contributors.append(pr_reviwer_cntrb)

    return pr, contributors


@celery.task
def collect_events(repo_git: str):

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_events.__name__)

    logger.info(f"Collecting pull request events for {owner}/{repo}")
    
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    events = GithubPaginator(url, session.oauths, logger)

    index = 0

    num_pages = events.get_num_pages()
    
    for page_data, page in events.iter_pages():

        logger.info(f"Events Page {page} of {num_pages}")

        process_events.s(page_data, f"Events Page {page} Task").apply_async()
        
    logger.info("Completed events")

@celery.task
def process_events(events, task_name):

    logger = logging.getLogger(process_events.__name__)
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

    # get repo_id
    repo_id = 1
    platform_id = 25150
    tool_source = "Pr event task"
    tool_version = "2.0"
    data_source = "Github API"
   
    pr_event_dicts = []
    issue_event_dicts = []
    contributors = []

    event_len = len(events)
    for index, event in enumerate(events):

        event, contributor = process_github_event_contributors(event, platform_id, tool_source, tool_version, data_source)

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

        if contributor:
            contributors.append(contributor)
        
        if type(contributor) == list:
            print(f"Event: {event}")
            print(f"Contributor: {contributor}")

    # remove contributors that were found in the data more than once
    contributors = remove_duplicate_dicts(contributors)

    session.insert_data(contributors, Contributor, ["cntrb_login"])

    logger.info(f"{task_name}: Inserting {len(pr_event_dicts)} pr events and {len(issue_event_dicts)} issue events")

    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["node_id"]
    session.insert_data(pr_event_dicts, PullRequestEvent, pr_event_natural_keys)

    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    session.insert_data(issue_event_dicts, IssueEvent, issue_event_natural_keys)


# TODO: Should we skip an event if there is no contributor to resolve it o
def process_github_event_contributors(event, platform_id, tool_source, tool_version, data_source):

    if event["actor"]:

        event_cntrb = extract_needed_contributor_data(event["actor"], platform_id, tool_source, tool_version, data_source)
        event["cntrb_id"] = event_cntrb["cntrb_id"]

    else:
        return event, None
    
    return event, event_cntrb

@celery.task
def collect_issue_and_pr_comments(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    # define logger for task
    logger = logging.getLogger(collect_issue_and_pr_comments.__name__)
    logger.info(f"Collecting github comments for {owner}/{repo}")
    
    # define database task session, that also holds autentication keys the GithubPaginator needs
    session = GithubTaskSession(logger)
    
    # url to get issue and pull request comments
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments"
    
    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    messages = GithubPaginator(url, session.oauths, logger)

    num_pages = messages.get_num_pages()
    
    for page_data, page in messages.iter_pages():

        logger.info(f"Github Messages Page {page} of {num_pages}")

        process_messages.s(page_data, f"Github Messages Page {page} Task").apply_async()
        
    logger.info("Completed messages")

@celery.task
def process_messages(messages, task_name):

    # define logger for task
    logger = logging.getLogger(process_messages.__name__)
    
    # define database task session, that also holds autentication keys the GithubPaginator needs
    session = GithubTaskSession(logger)

    repo_id = 1
    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"

    message_dicts = []
    message_ref_mapping_data = []
    contributors = []

    if messages is None:
        logger.debug(f"{task_name}: Messages was Nonetype...exiting")
        return

    if len(messages) == 0:
        logger.info(f"{task_name}: No messages to process")

    for index, message in enumerate(messages):

        related_pr_of_issue_found = False

        # this adds the cntrb_id to the message data
        # the returned contributor will be added to the contributors list later, if the related issue or pr are found
        # this logic is used so we don't insert a contributor when the related message isn't inserted
        message, contributor = process_github_comment_contributors(message, platform_id, tool_source, tool_version, data_source)

        if is_issue_message(message["html_url"]):

            try:
                related_issue = session.query(Issue).filter(Issue.issue_url == message["issue_url"]).one()
                related_pr_of_issue_found = True

            except s.orm.exc.NoResultFound:
                logger.info("Could not find related pr")
                logger.info(f"We were searching for: {message['id']}")
                logger.info("Skipping")
                continue

            issue_id = related_issue.issue_id

            issue_message_ref_data = extract_needed_issue_message_ref_data(message, issue_id, repo_id, tool_source, tool_version, data_source)

            message_ref_mapping_data.append(
                {
                    "platform_msg_id": message["id"],
                    "msg_ref_data": issue_message_ref_data,
                    "is_issue": True
                }
            )

        else:

            try:
                related_pr = session.query(PullRequest).filter(PullRequest.pr_issue_url == message["issue_url"]).one()
                related_pr_of_issue_found = True

            except s.orm.exc.NoResultFound:
                logger.info("Could not find related pr")
                logger.info(f"We were searching for: {message['issue_url']}")
                logger.info("Skipping")
                continue

            pull_request_id = related_pr.pull_request_id

            pr_message_ref_data = extract_needed_pr_message_ref_data(message, pull_request_id, repo_id, tool_source, tool_version, data_source)

            message_ref_mapping_data.append(
                {
                    "platform_msg_id": message["id"],
                    "msg_ref_data": pr_message_ref_data,
                    "is_issue": False
                }
            )
        
        if related_pr_of_issue_found:

            message_dicts.append(
                            extract_needed_message_data(message, platform_id, repo_id, tool_source, tool_version, data_source)
            )

            contributors.append(contributor)

    contributors = remove_duplicate_dicts(contributors)

    logger.info(f"Inserting {len(contributors)} contributors")

    session.insert_data(contributors, Contributor, ["cntrb_login"])

    
    logger.info(f"Inserting {len(message_dicts)} messages")
    message_natural_keys = ["platform_msg_id"]
    message_return_columns = ["msg_id", "platform_msg_id"]
    message_return_data = session.insert_data(message_dicts, Message, message_natural_keys, message_return_columns)

    pr_message_ref_dicts = []
    issue_message_ref_dicts = []
    for mapping_data in message_ref_mapping_data:

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

        if mapping_data["is_issue"] is True:
            issue_message_ref_dicts.append(message_ref_data)
        else:
            pr_message_ref_dicts.append(message_ref_data)

    pr_message_ref_natural_keys = ["pull_request_id", "pr_message_ref_src_comment_id"]
    session.insert_data(pr_message_ref_dicts, PullRequestMessageRef, pr_message_ref_natural_keys)

    issue_message_ref_natural_keys = ["issue_id", "issue_msg_ref_src_comment_id"]
    session.insert_data(issue_message_ref_dicts, IssueMessageRef, issue_message_ref_natural_keys)

    logger.info(f"{task_name}: Inserted {len(message_dicts)} messages. {len(issue_message_ref_dicts)} from issues and {len(pr_message_ref_dicts)} from prs")



def is_issue_message(html_url):

    return 'pull' not in html_url


def process_github_comment_contributors(message, platform_id, tool_source, tool_version, data_source):

    message_cntrb = extract_needed_contributor_data(message["user"], platform_id, tool_source, tool_version, data_source)
    message["cntrb_id"] = message_cntrb["cntrb_id"]

    return message, message_cntrb

        
@celery.task
def pull_request_review_comments(repo_git: str) -> None:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(pull_request_review_comments.__name__)
    
    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

    logger.info(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    pr_review_comments = GithubPaginator(url, session.oauths, logger)

    # get repo_id
    repo_id = 1

    platform_id = 25150
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

    owner, repo = get_owner_repo(repo_git)

    pr_number_list = sorted(pr_number_list, reverse=False) 

    repo_id = 1
    platform_id = 25150
    tool_version = "2.0"
    data_source = "Github API"

    logger = logging.getLogger(pull_request_reviews.__name__)
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger)

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



"""
Notes

Date needed to process contributor: src_id and login

Data must already be inserted into src_table before running the task 
the issue is that most of the time we filter out needed

[
    {
        "table": Pulls,
        "pk": "pull_request_id",
        "data": data
    }
]

"""

# for this task to work well universally we need all tables to name cntrb_id
# @celery.task
# def process_issue_contributors(contributors):

#     logger = get_task_logger(process_issue_contributors.name)
#     process_contributors(contributors, table=Issues, logger=logger, unique_keys=["issue_url"], pk_name="issue_id")

# @celery.task
# def process_issue_assignee_contributors(contributors):

#     logger = get_task_logger(process_issue_assignee_contributors.name)
#     # process_contributors(contributors, table=IssueAssignees, logger=logger, pk_name="issue_assignee_id")

@celery.task
def process_contributors():

    logger = logging.getLogger(process_contributors.__name__)
    session = GithubTaskSession(logger)

    platform = 1
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"

    contributors = session.query(Contributor).filter(Contributor.data_source == data_source, Contributor.cntrb_created_at == None, Contributor.cntrb_last_used == None).all()

    contributors_len = len(contributors)

    if contributors_len == 0:
        print("No contributors to enrich...returning...")
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
    session.insert_data(enriched_contributors, Contributor, ["cntrb_login"])













    # update_dicts = []
    # contributor_dicts = []
    # index = 1
    # total_all_time =  0
    # start_time = time.time()
    # for contributor in contributors:

    #     # get the primary key for the table that needs update with a cntrb_id
    #     # primary_key = contributor[pk_name]
    #     # del contributor[pk_name]

    #     # create uuid from gh contributor id and platform id
    #     uuid_cntrb_id = AugurUUID(platform, contributor["id"]).to_UUID()

    #     # get the needed data from the gh api respones
    #     contributor_data = extract_needed_contributor_data(contributor, uuid_cntrb_id, tool_source, tool_version, data_source)

    #     # insert the contributor into the table

    #     contributor_dicts.append(contributor_data)
    #     # session.insert_data(contributor_data, Contributor, ["cntrb_id"])

    #     # create list of dicts to update the table with the cntrb_ids
    #     update_row = {}
    #     update_row[cntrb_id_name] = uuid_cntrb_id

    #     for field in unique_keys:
    #         update_row[field] = contributor[field]
    #     # update_row[pk_name] = primary_key

    #     update_dicts.append(update_row)

    # s = time.time()

    # contrib_len = len(contributor_dicts)

    # print(f"Length of contributors: {contrib_len}")

    # unique_contrbs_logins = []
    # unique_contrbs = []
    # for contrb in contributor_dicts:

    #     if contrb["cntrb_login"] not in unique_contrbs_logins:
    #         unique_contrbs.append(contrb)
    #         unique_contrbs_logins.append(contrb["cntrb_login"])

        


    # contributor_dicts = [dict(y) for y in set(tuple(x.items()) for x in contributor_dicts)]

    # e = time.time() - s

    # print(f"Length of contributors: {len(unique_contrbs)}. Time to remove {contrib_len - len(unique_contrbs)}: {e} seconds")

    # session.insert_data(unique_contrbs, Contributor, ["cntrb_id"])    

    # total_time = time.time() - start_time

    # print(f"Seconds to proccess {len(update_dicts)} contributors: {total_time}")

    # # update table with cntrb_ids
    # start = time.time()
    # session.insert_data(update_dicts, table, unique_keys)
    # # session.bulk_update_mappings(table, update_dicts)
    # # session.commit()
    # total = time.time() - start

    # print(f"Seconds to update {len(update_dicts)} rows: {total}")


def is_valid_pr_block(issue):
    return (
        'pull_request' in issue and issue['pull_request']
        and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
    )

def remove_duplicate_dicts(data_list):

    return [dict(y) for y in set(tuple(x.items()) for x in data_list)]


# This function adds a key value pair to a list of dicts and returns the modified list of dicts back
def add_key_value_pair_to_list_of_dicts(data_list, key, value):

    for data in data_list:

        data[key] = value

    return data_list

# this function finds a dict in a list of dicts. 
# This is done by searching all the dicts for the given key that has the specified value
def find_dict_in_list_of_dicts(data, key, value):

    return next((item for item in data if item[key] == value), None)


def retrieve_dict_data(url: str, session):

    num_attempts = 0
    while num_attempts <= 10:

        response = hit_api(session, url)

        # increment attempts
        if response is None:
            num_attempts += 1
            continue
        # update rate limit here

        page_data = response.json()

        if "message" in page_data:

            if page_data['message'] == "Not Found":
                logger.info(
                    "Github repo was not found or does not exist for endpoint: "
                    f"{response.url}\n"
                )
                break

            elif "You have exceeded a secondary rate limit. Please wait a few minutes before you try again" in page_data['message']:
                logger.info('\n\n\n\nSleeping for 100 seconds due to secondary rate limit issue.\n\n\n\n')
                time.sleep(100)
                continue

            elif "You have triggered an abuse detection mechanism." in page_data['message']:
                #self.update_rate_limit(response, temporarily_disable=True,platform=platform)
                continue
        else:
            return page_data


    return None




# start("grafana", "oncall")



def get_owner_repo(git_url):
    """ Gets the owner and repository names of a repository from a git url

    :param git_url: String, the git url of a repository
    :return: Tuple, includes the owner and repository names in that order
    """
    split = git_url.split('/')

    owner = split[-2]
    repo = split[-1]

    if '.git' == repo[-4:]:
        repo = repo[:-4]

    return owner, repo