from .facade_tasks import *

from augur_new.db.data_parse import *
# creates a class that is sub class of the sqlalchemy.orm.Session class that additional methods and fields added to it. 

#NOTICE: A pull request is a type of issue as per Github.
#So this file contains functionality for both prs and issues


# import logging

# logger = logging.getLogger()

# # Initialize logging
# formatter = "%(asctime)s: %(message)s"
# logging.basicConfig(filename="augur_view.log", filemode='w', format=formatter, level=logging.INFO, datefmt="%H:%M:%S")

# logging.debug("This is a debug message")
# logging.info("This is an information message")
# logging.warn("This is a warning message")
# logging.error("This is an error message")



@celery.task
def issues(owner: str, repo: str) -> None:

    logger = get_task_logger(__name__)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)

    print(f"Collecting issues for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Issue Task"
    tool_version = "2.0"
    # platform_id = 25150
    data_source = "Github API"

    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    issues = GithubPaginator(url, session.oauths, logger)
    issues_length = len(issues)

    issue_dicts = []
    issue_mapping_data = []
 
    # this is defined so we can decrement it each time 
    # we come across a pr, so at the end we can log how 
    # many issues were collected
    issue_total = len_issues

    # loop through the issues 
    for index, issue in enumerate(issues):

        print(f"Inserting issue {index + 1} of {len_issues}")

        # calls is_valid_pr_block to see if the data is a pr.
        # if it is a pr we skip it because we don't need prs 
        # in the issues table
        if is_valid_pr_block(issue) is True:
            issue_total-=1
            continue
        
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

        
        issue_mapping_data.append(
            # store the issue_url, labels, and assignees 
            # so we can relate the lables and assigness 
            # to a specific row in the pr table after we insert the prs
            {
                "issue_url": issue["url"],
                "labels": issue_labels,
                "assignees": issue_assignees
            }
        )                                        

    # insert the issues into the issues table. 
    # issue_urls are gloablly unique across github so we are using it to determine whether an issue we collected is already in the table
    # specified in issue_return_columns is the columns of data we want returned. This data will return in this form; {"issue_url": url, "issue_id": id}
    issue_natural_keys = ["issue_url"]
    issue_return_columns = ["issue_url", "issue_id"]
    issue_return_data = session.insert_data(issue_dicts, Issues, issue_natural_keys, issue_return_columns)

    # loop through the issue mapping data so the labels 
    # and assignees and be mapped to their respective prs
    issue_label_dicts = []
    issue_assignee_dicts = []
    for data in issue_mapping_data:

        # search the list of data returned from the issues insert 
        # to find the dict that has the same url as the labels and assignees
        key = "issue_url"
        value = data[key]
        issue = find_dict_in_list_of_dicts(issue_return_data, key, value)


        if issue:
            issue_id = issue["issue_id"]
        else:
            print("Count not find issue for labels or assignees. If the insertion was successful this should never happen")
            print("Skipping because we can't map the labels or assignees without the issue_id")
            continue

        # add the issue id to the lables and assignees, then add them to a list of dicts that will be inserted soon
        dict_key = "issue_id"
        issue_label_dicts += add_key_value_pair_to_list_of_dicts(data["labels"], "issue_id", issue_id)
        issue_assignee_dicts += add_key_value_pair_to_list_of_dicts(data["assignees"], "issue_id", issue_id)

    # inserting issue labels
    # we are using label_src_id and issue_id to determine if the label is already in the database.
    logger.info(f"Inserting issue labels of length: {len(issue_label_dicts)}")
    issue_label_natural_keys = ['label_src_id', 'issue_id']
    session.insert_data(issue_label_dicts, IssueLabels, issue_label_natural_keys)
  
    # inserting issue assignees
    # we are using issue_assignee_src_id and issue_id to determine if the label is already in the database.
    logger.info(f"Inserting issue assignees of length: {len(issue_assignee_dicts)}")
    issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
    session.insert_data(issue_assignee_dicts, IssueAssignees, issue_assignee_natural_keys)

    print(f"{issue_total} issues inserted")


# TODO: Rename pull_request_reviewers table to pull_request_requested_reviewers
# TODO: Fix column names in pull request labels table
@celery.task
def pull_requests(owner: str, repo: str) -> None:

    logger = get_task_logger(pull_requests.name)

    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Pr Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"

    # returns an iterable of all prs at this url (this essentially means you can treat the prs variable as a list of the prs)
    prs = GithubPaginator(url, session.oauths, logger)
    prs_length = len(prs)

    pr_dicts = []
    pr_mapping_data = []
    pr_numbers = []

    for index, pr in enumerate(prs):

        logger.info(f"Inserting pr {index + 1} of {prs_length}")

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
                                                        
        pr_mapping_data.append(
            {
                # store the pr_url, labels, assignees, reviewers, and metadata
                # so we can relate the labels, assignees, reviewers, and metadata
                # to a specific row in the pr table after we insert the prs
                "pr_url": pr["url"],
                "labels": pr_labels,
                "assignees": pr_assignees,
                "reviewers": pr_reviewers,
                "metadata": pr_metadata,
            }
        )

        # create a list of pr numbers to pass for the pr reviews task
        pr_numbers.append(pr["number"]) 


    # insert the prs into the pull_requests table. 
    # pr_urls are gloablly unique across github so we are using it to determine whether a pull_request we collected is already in the table
    # specified in pr_return_columns is the columns of data we want returned. This data will return in this form; {"pr_url": url, "pull_request_id": id}
    logger.info(f"Inserting prs of length: {len(pr_dicts)}")
    pr_natural_keys = ["pr_url"]
    pr_return_columns = ["pull_request_id", "pr_url"]
    pr_return_data = session.insert_data(pr_dicts, PullRequests, pr_natural_keys, return_columns=pr_return_columns)


    # loop through the pr mapping data so the 
    # labels, assignees, reviewers, and assignees 
    # can be mapped to their respective prs
    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []
    for data in pr_mapping_data:

        # search the list of data returned from the pr insert 
        # to find the dict that has the same url as the labels, assignees, reviewers, and metadata
        value = data["pr_url"]
        key = "pr_url"
        pull_request = find_dict_in_list_of_dicts(pr_return_data, key, value)

        if pull_request:

            pull_request_id = pull_request["pull_request_id"]
        else:
            print("Count not find pr for labels, assignees, reviewers, or metadata. If the insertion was successful this should never happen")
            print("Skipping because we can't map the labels, assignees, reviewers, or metadata without the pull_request_id")
            continue

        # add the pull_request_id to the labels, assignees, reviewers, or metadata then add them to a list of dicts that will be inserted soon
        dict_key = "pull_request_id"
        pr_label_dicts += add_key_value_pair_to_list_of_dicts(data["labels"], dict_key, pull_request_id)
        pr_assignee_dicts += add_key_value_pair_to_list_of_dicts(data["assignees"], dict_key, pull_request_id)
        pr_reviewer_dicts += add_key_value_pair_to_list_of_dicts(data["reviewers"], dict_key, pull_request_id)
        pr_metadata_dicts += add_key_value_pair_to_list_of_dicts(data["metadata"], dict_key, pull_request_id)
        

    # inserting pr labels
    # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
    logger.info(f"Inserting pr labels of length: {len(pr_label_dicts)}")
    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    session.insert_data(pr_label_dicts, PullRequestLabels, pr_label_natural_keys)
  
    # inserting pr assignees
    # we are using pr_assignee_src_id and pull_request_id to determine if the label is already in the database.
    logger.info(f"Inserting pr assignees of length: {len(pr_assignee_dicts)}")
    pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    session.insert_data(pr_assignee_dicts, PullRequestAssignees, pr_assignee_natural_keys)
 
    # inserting pr assignees
    # we are using pr_src_id and pull_request_id to determine if the label is already in the database.
    logger.info(f"Inserting pr reviewers of length: {len(pr_reviewer_dicts)}")
    pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
    session.insert_data(pr_reviewer_dicts, PullRequestReviewers, pr_reviewer_natural_keys)
    
    # inserting pr metadata
    # we are using pull_request_id, pr_head_or_base, and pr_sha to determine if the label is already in the database.
    logger.info(f"Inserting pr metadata of length: {len(pr_metadata_dicts)}")
    pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
    session.insert_data(pr_metadata_dicts, PullRequestMeta, pr_metadata_natural_keys)

# This function adds a key value pair to a list of dicts and returns the modified list of dicts back
def add_key_value_pair_to_list_of_dicts(data_list, key, value):

    for data in data_list:

        data[key] = value

    return data_list

# this function finds a dict in a list of dicts. 
# This is done by searching all the dicts for the given key that has the specified value
def find_dict_in_list_of_dicts(data, key, value):

    return next((item for item in data if item[key] == value), None)
    


# TODO: Why do I need self?
@celery.task
def github_events(self, owner: str, repo: str):

    logger = get_task_logger(github_events.name)
    logger.info(f"Collecting pull request events for {owner}/{repo}")
    
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    pr_events = GithubPaginator(url, session.oauths, logger)

    index = 0

    data = []
    for pr_event in pr_events:

        # if index == 100:
        #     break

        data.append(pr_event)

        index+=1

    # len_pr_events = len(pr_events)

    # logger.info(f"Length of pr events: {len_pr_events}")

    # logger.info(f"Number of tasks with 500 events: {len_pr_events // 500}")

    # events_per_task = 500
    # max_tasks = 5

    # if len_pr_events > (max_tasks * 1000):
    #     events_per_task = len_pr_events // max_tasks
    #     # round up the events per task so we ensure no more than 5 tasks are spawned
    #     events_per_task += 1
    logger.info(len(data))

    min_events_per_task = 250
    max_tasks = 5

    chunked_data = chunk_data(data, min_events_per_task, max_tasks)

    
    task_list = [process_events.s(data, f"Events task {index+1}") for index, data in enumerate(chunked_data)]

    process_events_job = group(task_list)

    result = process_events_job.apply_async()


def chunk_data(data, min_events_per_task, max_tasks):

    data_length = len(data)

    events_per_task = (data_length // max_tasks) + 1

    if min_events_per_task > events_per_task:
        events_per_task = min_events_per_task

    end = 0
    index = 0
    chunked_data = []
    while(end + 1 < data_length):

        start = index * events_per_task
        end = start + events_per_task        
        list_slice = data[slice(start, end)]
        chunked_data.append(list_slice)

        index+=1

    return chunked_data

@celery.task
def process_events(events, task_name):

    logger = get_task_logger(process_events.name)
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr event task"
    tool_version = "2.0"
    data_source = "Github API"
    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["platform_id", "node_id"]
    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    pr_event_dicts = []
    issue_event_dicts = []

    event_len = len(events)
    for index, event in enumerate(events):

        if index % 100 == 0:

            event_index_start = index 
            event_index_end = index + 100

            if event_index_end > event_len:
                event_index_end = event_len

            logger.info(f"{task_name}: Proccessing event {event_index_start} to {event_index_end} of {event_len}")

        if 'pull_request' in list(event["issue"].keys()):
            pr_url = event["issue"]["pull_request"]["url"]

            try:
                related_pr = PullRequests.query.filter_by(pr_url=pr_url).one()
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
                related_issue = Issues.query.filter_by(issue_url=issue_url).one()
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

    logger.info(f"Issue event count: {len(issue_event_dicts)}")
    logger.info(f"Pr event count: {len(pr_event_dicts)}")
    logger.info(f"Total event count: {len(issue_event_dicts) + len(pr_event_dicts)}")

    logger.info("Inserting all pr events")
    session.insert_data(pr_event_dicts, PullRequestEvents, pr_event_natural_keys)

    logger.info("Inserting all issue events")
    session.insert_data(issue_event_dicts, IssueEvents, issue_event_natural_keys)


@celery.task
def github_comments(self, owner: str, repo: str) -> None:

    # define logger for task
    logger = get_task_logger(github_comments.name)
    logger.info(f"Collecting github comments for {owner}/{repo}")
    
    # define database task session, that also holds autentication keys the GithubPaginator needs
    session = GithubTaskSession(logger, config)
    
    # url to get issue and pull request comments
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments"
    
    # returns an iterable of all issues at this url (this essentially means you can treat the issues variable as a list of the issues)
    messages = GithubPaginator(url, session.oauths, logger)

    repo_id = 1
    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"

    message_dicts = []
    message_ref_mapping_data = []

    message_len = len(messages)

    total_pages = (message_len // 100) + 1
    page_index = 1

    for index, message in enumerate(messages):

        if index % 100 == 0:
            logger.info(f"Processing page {page_index} of {total_pages}")
            page_index += 1

        related_pr_of_issue_found = False

        
        if is_issue_message(message["html_url"]):

            try:
                related_issue = Issues.query.filter_by(issue_url=message["issue_url"]).one()
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
                related_pr = PullRequests.query.filter_by(pr_issue_url=message["issue_url"]).one()
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


    logger.info(f"Issue message count: {len(issue_message_ref_dicts)}")
    logger.info(f"Pr message count: {len(pr_message_ref_dicts)}")

    logger.info("Inserting all pr messages")
    pr_message_ref_natural_keys = ["pull_request_id", "pr_message_ref_src_comment_id"]
    session.insert_data(pr_message_ref_dicts, PullRequestMessageRef, pr_message_ref_natural_keys)

    logger.info("Inserting all issue messages")
    issue_message_ref_natural_keys = ["issue_id", "issue_msg_ref_src_comment_id"]
    session.insert_data(issue_message_ref_dicts, IssueMessageRef, issue_message_ref_natural_keys)



def is_issue_message(html_url):

    return 'pull' not in html_url

        
@celery.task
def pull_request_review_comments(self, owner: str, repo: str) -> None:

    logger = get_task_logger(pull_request_review_comments.name)
    
    # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)

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

        logger.info(f"Processing pr review comment {index + 1} of {pr_review_comments_len}")

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
def pull_request_reviews(self, owner: str, repo: str, pr_number_list: [int]) -> None:

    logger = get_task_logger(pull_request_reviews.name)
        # define GithubTaskSession to handle insertions, and store oauth keys 
    session = GithubTaskSession(logger, config)

    logger.info(f"Collecting pull request reviews for {owner}/{repo}")

    for pr_number in pr_number_list:

        reviews = PullRequest(session, owner, repo, pr_number).get_reviews_collection()

        for review in reviews:
            print(review)

        if len(reviews) == 0:
            print(f"No reviews for pr number: {pr_number}")



def is_valid_pr_block(issue):
    return (
        'pull_request' in issue and issue['pull_request']
        and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
    )




# start("grafana", "oncall")



