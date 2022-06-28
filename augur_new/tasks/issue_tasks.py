from .facade_tasks import *

from augur_new.db.objects.pull_request import PrObject
from augur_new.db.objects.issue import IssueObject
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
    session = GithubTaskSession(logger, config)

    print(f"Collecting issues for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Issue Task"
    tool_version = "2.0"
    # platform_id = 25150
    data_source = "Github API"

    issue_natural_keys = ["issue_url"]

    # returns an iterable of all prs at this url
    issues = GithubPaginator(url, session.oauths, logger)

    issue_label_dicts = []
    issue_assignee_dicts = []
 

    # creating a list, because we would like to bulk insert in the future
    len_issues = len(issues)
    issue_total = len_issues
    print(f"Length of issues: {len_issues}")
    for index, issue in enumerate(issues):

        print(f"Inserting issue {index + 1} of {len_issues}")

        if is_valid_pr_block(issue) is True:
            issue_total-=1
            continue

        issue_object = IssueObject(issue, repo_id, tool_source, tool_version, data_source)

        # when the object gets inserted the db_row is added to the object which is a PullRequests orm object (so it contains all the column values)
        session.insert_data([issue_object], Issues, issue_natural_keys)

        issue_label_dicts += extract_needed_issue_label_data(issue_object.labels, issue_object.db_row.issue_id, repo_id,
                                                       tool_source, tool_version, data_source)

        issue_assignee_dicts += extract_needed_issue_assignee_data(issue_object.assignees, issue_object.db_row.issue_id, repo_id,
                                                             tool_source, tool_version, data_source)


    logger.info(f"Inserting issue labels of length: {len(issue_label_dicts)}")
    issue_label_natural_keys = ['label_src_id', 'issue_id']
    session.insert_data(issue_label_dicts, IssueLabels, issue_label_natural_keys)
  

    logger.info(f"Inserting issue assignees of length: {len(issue_assignee_dicts)}")
    issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
    session.insert_data(issue_assignee_dicts, IssueAssignees, issue_assignee_natural_keys)

    print(f"{issue_total} issues inserted")


@celery.task
def pull_requests(owner: str, repo: str) -> None:

    logger = get_task_logger(pull_requests.name)
    session = GithubTaskSession(logger, config)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&direction=desc"
    

    # get repo_id or have it passed
    repo_id = 1
    tool_source = "Pr Task"
    tool_version = "2.0"
    platform_id = 25150
    data_source = "Github API"



    # returns an iterable of all prs at this url
    prs = GithubPaginator(url, session.oauths, logger)

    # logger.info(f"Pages collected: length: {len(prs)}")

    pr_dicts = []
    pr_other_data = []
    repo_pr_numbers = []

    len_prs = len(prs)
    for index, pr in enumerate(prs):

        pr['head'].update(
            {'pr_head_or_base': 'head'}
        )
        pr['base'].update(
            {'pr_head_or_base': 'base'}
        )

        logger.info(f"Inserting pr {index + 1} of {len_prs}")

        pr_dicts.append(
                    extract_needed_pr_data(pr, repo_id, tool_source,tool_version)
        )

        pr_labels = extract_needed_pr_label_data(pr["labels"],  platform_id, repo_id,
                                                       tool_source, tool_version, data_source)

        pr_assignees = extract_needed_pr_assignee_data(pr["assignees"], platform_id, repo_id,
                                                             tool_source, tool_version, data_source)


        pr_reviewers = extract_needed_pr_reviewer_data(pr["requested_reviewers"], platform_id, repo_id,
                                                             tool_source, tool_version, data_source)

        pr_metadata = extract_needed_pr_metadata([pr["head"], pr["base"]], platform_id, repo_id,
                                                        tool_source, tool_version, data_source)                                                             
                                                        
        pr_other_data.append(
            {
                "pr_url": pr["url"],
                "labels": pr_labels,
                "assignees": pr_assignees,
                "reviewers": pr_reviewers,
                "metadata": pr_metadata,
            }
        )

        # get a list of pr numbers to pass for the pr reviews task
        repo_pr_numbers.append(pr["number"]) 


    logger.info(f"Inserting prs of length: {len(pr_dicts)}")
    pr_natural_keys = ["pr_url"]
    pr_return_columns = ["pull_request_id", "pr_url"]
    pr_return_data = session.insert_data(pr_dicts, PullRequests, pr_natural_keys, return_columns=pr_return_columns)

    pr_label_dicts = []
    pr_assignee_dicts = []
    pr_reviewer_dicts = []
    pr_metadata_dicts = []

    for data in pr_other_data:

        pr_url = data["pr_url"]
        key = "pr_url"

        pull_request = next((item for item in pr_return_data if item[key] == pr_url), None)

        if pull_request:

            pull_request_id = pull_request["pull_request_id"]
        else:
            print("Count not find pull_request")

        pr_label_dicts += add_pull_request_id_to_list_of_dicts(data["labels"], pull_request_id)
        
        pr_assignee_dicts += add_pull_request_id_to_list_of_dicts(data["assignees"], pull_request_id)
        
        pr_reviewer_dicts += add_pull_request_id_to_list_of_dicts(data["reviewers"], pull_request_id)
        
        pr_metadata_dicts += add_pull_request_id_to_list_of_dicts(data["metadata"], pull_request_id)
        

    # start task()
    logger.info(f"Inserting pr labels of length: {len(pr_label_dicts)}")
    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    session.insert_data(pr_label_dicts, PullRequestLabels, pr_label_natural_keys)
  
    # start task()
    logger.info(f"Inserting pr assignees of length: {len(pr_assignee_dicts)}")
    pr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    session.insert_data(pr_assignee_dicts, PullRequestAssignees, pr_assignee_natural_keys)
 

    logger.info(f"Inserting pr reviewers of length: {len(pr_reviewer_dicts)}")
    pr_reviewer_natural_keys = ["pull_request_id", "pr_reviewer_src_id"]
    session.insert_data(pr_reviewer_dicts, PullRequestReviewers, pr_reviewer_natural_keys)
    

    start_time = time.time()
    logger.info(f"Inserting pr metadata of length: {len(pr_metadata_dicts)}")
    pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
    session.insert_data(pr_metadata_dicts, PullRequestMeta, pr_metadata_natural_keys)


def add_pull_request_id_to_list_of_dicts(data, pull_request_id):

    for value in data:

        value["pull_request_id"] = pull_request_id

    return data
    


# TODO: Why do I need self?
@celery.task
def github_events(self, owner: str, repo: str):

    logger = get_task_logger(github_events.name)
    logger.info(f"Collecting pull request events for {owner}/{repo}")
    
    session = GithubTaskSession(logger, config)
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/events"
    
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

    
    task_list = [process_events.s(data) for data in chunked_data]

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
def process_events(events):

    logger = get_task_logger(process_events.name)
    session = GithubTaskSession(logger, config)

    logger.info(f"Len of events: {len(events)}")
    logger.info(f"Type of events: {type(events)}")

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    # TODO: Could replace this with "id" but it isn't stored on the table for some reason
    pr_event_natural_keys = ["platform_id", "node_id"]
    issue_event_natural_keys = ["issue_id", "issue_event_src_id"]
    pr_event_dicts = []
    issue_event_dicts = []

    for index, event in enumerate(events):
        
        logger.info(f"Proccessing event {index + 1} of {len(events)}")

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

    logger.info("Inserting all pr events")
    session.insert_data(pr_event_dicts, PullRequestEvents, pr_event_natural_keys)

    logger.info("Inserting all issue events")
    session.insert_data(issue_event_dicts, IssueEvents, issue_event_natural_keys)


@celery.task
def github_comments(owner: str, repo: str) -> None:

    # define logger for task
    logger = get_task_logger(github_comments.name)
    logger.info(f"Collecting github comments for {owner}/{repo}")
    
    # define database task session, that also holds autentication keys the GithubPaginator needs
    session = GithubTaskSession(logger, config)
    
    # url to get issue and pull request comments
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/comments"
    
    # GithubPaginator creates and iterable of pr_events
    messages = GithubPaginator(url, session.oauths, logger)


    repo_id = 1
    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"

    # TODO: Remove tool_source
    message_natural_keys = ["platform_msg_id", "tool_source"]
    pr_message_ref_natural_keys = ["pull_request_id", "pr_message_ref_src_comment_id"]
    issue_message_ref_natural_keys = ["issue_id", "issue_msg_ref_src_comment_id"]

    pr_message_ref_dicts = []
    issue_message_ref_dicts = []


    # SELECT pr_src_number FROM augur_data.pull_requests where repo_id= 25961
    # SELECT pr_src_number FROM augur_data.pull_requests where repo_id= 25961



    for message in messages:

        message_object = MessageObject(message, platform_id, repo_id, tool_source, tool_version, data_source)

        # when the object gets inserted the db_row is added to the object which is a PullRequests orm object (so it contains all the column values)
        session.insert_data([message_object], Message, message_natural_keys)

        if is_issue_message(message["html_url"]):

            issue_message_ref_dicts += extract_needed_issue_message_ref_data(messages, issue_id, message_object.db_row.msg_id, repo_id, tool_source, tool_version, data_source)

        else:

            pr_message_ref_dicts += extract_needed_pr_message_ref_data(messages, pull_request_id, message_object.db_row.msg_id, platform_id, repo_id, tool_source, tool_version, data_source)



    logger.info(f"Issue message count: {len(issue_message_ref_dicts)}")
    logger.info(f"Pr message count: {len(pr_message_ref_dicts)}")

    logger.info("Inserting all pr messages")
    session.insert_data(pr_message_ref_dicts, PullRequestMessageRef, pr_message_ref_natural_keys)

    logger.info("Inserting all issue messages")
    session.insert_data(issue_message_ref_dicts, IssueMessageRef, issue_message_ref_natural_keys)



def is_issue_message(html_url):

    return 'pull' not in html_url



        
@celery.task
def pull_request_review_comments(owner: str, repo: str) -> None:

    logger = get_task_logger(pull_request_review_comments.name)
    session = GithubTaskSession(logger, config)

    logger.info(f"Collecting pull request comments for {owner}/{repo}")

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/comments"

    pr_comments = GithubPaginator(url, session.oauths)

    # get repo_id
    repo_id = 1

    platform_id = 25150
    tool_source = "Pr comment task"
    tool_version = "2.0"
    data_source = "Github API"
    pr_comment_natural_keys = ["platform_msg_id"]
    pr_comment_ref_natural_keys = ["pr_review_msg_src_id"]

    pr_comment_ref_dicts = []

    pr_comment_len = len(pr_comments)

    logger.info(f"Pr comments len: {pr_comment_len}")
    for index, comment in enumerate(pr_comments):

        # pr url associated with this comment
        comment_pr_url = comment["pull_request_url"]

        related_pr = PullRequests.query.filter_by(pr_url=comment_pr_url).one()

        if not related_pr:
            logger.info(
                f"Error can't find pr for pr comment with id: {comment['id']}")
            continue

        pr_id = related_pr.pull_request_id

        pr_comment_object = PrCommentObject(comment, platform_id, repo_id, tool_source, tool_version, data_source)

        logger.info(f"Inserting pr review comment {index + 1} of {pr_comment_len}")
        session.insert_data([pr_comment_object], Message, pr_comment_natural_keys)

        msg_id = pr_comment_object.db_row.msg_id

        pr_comment_ref = extract_pr_review_message_ref_data(
            comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source)

        logger.info(pr_comment_ref)

        pr_comment_ref_dicts.append(
            pr_comment_ref
        )

        # pr_comment_ref_dicts.append(
        #     extract_pr_comment_ref_data(comment, pr_id, msg_id, repo_id, tool_source, tool_version, data_source)
        # )

    logger.info(f"Insert pr comment refs")
    session.insert_data(pr_comment_ref_dicts, PullRequestReviewMessageRef, pr_comment_ref_natural_keys)


# do this task after others because we need to add the multi threading like we did it before
@celery.task
def pull_request_reviews(owner: str, repo: str, pr_number_list: [int]) -> None:

    logger = get_task_logger(pull_request_reviews.name)
    session = GithubTaskSession(logger, config)

    logger.info(f"Collecting pull request reviews for {owner}/{repo}")

    # for pr_number in pr_number_list:

    #     url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/reviews"

        # add pr review




def is_valid_pr_block(issue):
    return (
        'pull_request' in issue and issue['pull_request']
        and isinstance(issue['pull_request'], dict) and 'url' in issue['pull_request']
    )




# start("grafana", "oncall")



