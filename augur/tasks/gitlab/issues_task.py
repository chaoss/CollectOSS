"""
Defines the set of tasks used to retrieve GitLab issue data.
"""
import logging
import traceback

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_api_handler import GitlabApiHandler
from augur.application.db.data_parse import extract_needed_issue_data_from_gitlab_issue, extract_needed_gitlab_issue_label_data, extract_needed_gitlab_issue_assignee_data, extract_needed_gitlab_issue_message_ref_data, extract_needed_gitlab_message_data, extract_needed_gitlab_contributor_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import Issue, IssueLabel, IssueAssignee, IssueMessageRef, Message, Contributor
from augur.tasks.util.worker_util import remove_duplicate_dicts
from augur.application.db.lib import bulk_insert_dicts, get_repo_by_repo_git, get_session
from augur.tasks.gitlab.gitlab_random_key_auth import GitlabRandomKeyAuth

platform_id = 2

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issues(repo_git : str) -> int:
    """
    Retrieve and parse gitlab issues for the desired repo

    Arguments:
        repo_git: the repo url string
    """

    logger = logging.getLogger(collect_gitlab_issues.__name__) 

    repo_id = get_repo_by_repo_git(repo_git).repo_id

    key_auth = GitlabRandomKeyAuth(logger)

    try:
        owner, repo = get_owner_repo(repo_git)
    
        issue_data = retrieve_all_gitlab_issue_data(repo_git, logger, key_auth)

        if issue_data:
            issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger)

            return issue_ids
        else:
            logger.info(f"{owner}/{repo} has no issues")
            return []
    except Exception as e:
            logger.error(f"Could not collect gitlab issues for repo {repo_git}\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
            return -1

def retrieve_all_gitlab_issue_data(repo_git, logger, key_auth) -> None:
    """
    Retrieve only the needed data for issues from the api response

    Arguments:
        repo_git: url of the relevant repo
        logger: loggin object
        key_auth: key auth cache and rotator object 
    """

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting gitlab issues for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/issues?with_labels_details=True"
    issues = GitlabApiHandler(key_auth, logger)

    all_data = []
    num_pages = issues.get_num_pages(url)
    for page_data, page in issues.iter_pages(url):

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo}: Gitlab Issues Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo}: Issues Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo}: Gitlab Issues Page {page} of {num_pages}")

        all_data += page_data

    return all_data
    
def process_issues(issues, task_name, repo_id, logger) -> None:
    """
    Retrieve only the needed data for issues from the api response

    Arguments:
        issues: List of dictionaries of issue data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        session: sqlalchemy db object 
    """

    # get repo_id or have it passed
    tool_source = "Gitlab Issue Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    issue_dicts = []
    issue_ids = []
    issue_mapping_data = {}
    contributors = []
    for issue in issues:

        issue_ids.append(issue["iid"])

        issue, contributor_data = process_issue_contributors(issue, tool_source, tool_version, data_source)

        contributors += contributor_data

        issue_dicts.append(
            extract_needed_issue_data_from_gitlab_issue(issue, repo_id, tool_source, tool_version, data_source)
        )

        issue_labels = extract_needed_gitlab_issue_label_data(issue["labels"], repo_id,
                                                       tool_source, tool_version, data_source)
        
        issue_assignees = extract_needed_gitlab_issue_assignee_data(issue["assignees"], repo_id,
                                                             tool_source, tool_version, data_source)
        
        mapping_data_key = issue["id"]
        issue_mapping_data[mapping_data_key] = {
                                            "labels": issue_labels,
                                            "assignees": issue_assignees,
                                            }    


    if len(issue_dicts) == 0:
        print("No gitlab issues found while processing")  
        return
    
    # remove duplicate contributors before inserting
    contributors = remove_duplicate_dicts(contributors)

    # insert contributors from these issues
    logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
    bulk_insert_dicts(logger, contributors, Contributor, ["cntrb_id"])
           
    logger.info(f"{task_name}: Inserting {len(issue_dicts)} gitlab issues")
    issue_natural_keys = ["repo_id", "gh_issue_id"]
    issue_string_columns = ["issue_title", "issue_body"]
    issue_return_columns = ["gh_issue_id", "issue_id"]

    issue_return_data = bulk_insert_dicts(logger, issue_dicts, Issue, issue_natural_keys, return_columns=issue_return_columns, string_fields=issue_string_columns)

    issue_label_dicts = []
    issue_assignee_dicts = []
    for data in issue_return_data:

        gh_issue_id = data["gh_issue_id"]
        issue_id = data["issue_id"]

        try:
            other_issue_data = issue_mapping_data[gh_issue_id]
        except KeyError as e:
            logger.info(f"{task_name}: Cold not find other gitlab issue data. This should never happen. Error: {e}")


        # add the issue id to the lables and assignees, then add them to a list of dicts that will be inserted soon
        dict_key = "issue_id"
        issue_label_dicts += add_key_value_pair_to_dicts(other_issue_data["labels"], dict_key, issue_id)
        issue_assignee_dicts += add_key_value_pair_to_dicts(other_issue_data["assignees"], dict_key, issue_id)


    logger.info(f"{task_name}: Inserting other gitlab issue data of lengths: Labels: {len(issue_label_dicts)} - Assignees: {len(issue_assignee_dicts)}")

    # inserting issue labels
    # we are using label_src_id and issue_id to determine if the label is already in the database.
    issue_label_natural_keys = ['label_src_id', 'issue_id']
    issue_label_string_fields = ["label_text", "label_description"]
    bulk_insert_dicts(logger, issue_label_dicts, IssueLabel,
                        issue_label_natural_keys, string_fields=issue_label_string_fields)

    # inserting issue assignees
    issue_assignee_natural_keys = ['issue_assignee_src_id', 'issue_id']
    bulk_insert_dicts(logger, issue_assignee_dicts, IssueAssignee, issue_assignee_natural_keys)

    return issue_ids

def process_issue_contributors(issue, tool_source, tool_version, data_source):

    contributors = []

    issue_cntrb = extract_needed_gitlab_contributor_data(issue["author"], tool_source, tool_version, data_source)
    issue["cntrb_id"] = issue_cntrb["cntrb_id"]
    contributors.append(issue_cntrb)

    for assignee in issue["assignees"]:

        issue_assignee_cntrb = extract_needed_gitlab_contributor_data(assignee, tool_source, tool_version, data_source)
        assignee["cntrb_id"] = issue_assignee_cntrb["cntrb_id"]
        contributors.append(issue_assignee_cntrb)

    return issue, contributors

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_issue_comments(issue_ids, repo_git) -> int:
    """
    Retrieve and parse gitlab events for the desired repo

    Arguments:
        issue_ids: Set of issue ids to collect coments for
        repo_git: repo url
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_gitlab_issues.__name__) 

    repo_id = get_repo_by_repo_git(repo_git).repo_id

    key_auth = GitlabRandomKeyAuth(logger)

    comments = retrieve_all_gitlab_issue_comments(key_auth, logger, issue_ids, repo_git)

    with get_session() as session:

        if comments:
            logger.info(f"Length of comments: {len(comments)}")
            process_gitlab_issue_messages(comments, f"{owner}/{repo}: Gitlab issue messages task", repo_id, logger, session)
        else:
            logger.info(f"{owner}/{repo} has no gitlab issue comments")
           

def retrieve_all_gitlab_issue_comments(key_auth, logger, issue_ids, repo_git):
    """
    Retrieve only the needed data for issue comments

    Arguments:
        key_auth: key auth cache and rotator object
        logger: loggin object
        issue_ids: ids of issues to find comements for
        repo_git: repo url
    """

    owner, repo = get_owner_repo(repo_git)

    all_comments = {}
    issue_count = len(issue_ids)
    index = 1

    comments = GitlabApiHandler(key_auth, logger)

    for id in issue_ids:

        logger.info(f"Collecting {owner}/{repo} gitlab issue comments for issue {index} of {issue_count}")

        url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/issues/{id}/notes"
        
        for page_data, _ in comments.iter_pages(url):

            if page_data is None or len(page_data) == 0:
                break

            if id in all_comments:
                all_comments[id].extend(page_data)
            else:
                all_comments[id] = page_data
        
        index += 1

    return all_comments


def process_gitlab_issue_messages(data, task_name, repo_id, logger, session):
    """
    Retrieve only the needed data for issue messages from the api response

    Arguments:
        data: List of dictionaries of issue event data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        session: sqlalchemy db object 
    """

    tool_source = "Gitlab issue comments"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    issue_number_to_id_map = {}
    issues = session.session.query(Issue).filter(Issue.repo_id == repo_id).all()
    for issue in issues:
        issue_number_to_id_map[issue.gh_issue_number] = issue.issue_id

    message_dicts = []
    contributors = []
    message_ref_mapping_data = {}
    for id, messages in data.items():

        try:
                issue_id = issue_number_to_id_map[id]
        except KeyError:
            logger.info(f"{task_name}: Could not find related issue")
            logger.info(f"{task_name}: We were searching for issue number {id} in repo {repo_id}")
            logger.info(f"{task_name}: Skipping")
            continue

        for message in messages:

            message, contributor = process_gitlab_issue_comment_contributors(message, tool_source, tool_version, data_source)

            if contributor:
                contributors.append(contributor)

            issue_message_ref_data = extract_needed_gitlab_issue_message_ref_data(message, issue_id, repo_id, tool_source, tool_version, data_source)

            message_ref_mapping_data[message["id"]] = {
                "msg_ref_data": issue_message_ref_data
            }

            message_dicts.append(
                extract_needed_gitlab_message_data(message, platform_id, tool_source, tool_version, data_source)
            )

    contributors = remove_duplicate_dicts(contributors)

    logger.info(f"{task_name}: Inserting {len(contributors)} contributors")
    bulk_insert_dicts(logger, contributors, Contributor, ["cntrb_id"])

    logger.info(f"{task_name}: Inserting {len(message_dicts)} messages")
    message_natural_keys = ["platform_msg_id", "pltfrm_id"]
    message_return_columns = ["msg_id", "platform_msg_id"]
    message_string_fields = ["msg_text"]
    message_return_data = bulk_insert_dicts(logger, message_dicts, Message, message_natural_keys, 
                                                return_columns=message_return_columns, string_fields=message_string_fields)
    
    issue_message_ref_dicts = []
    for data in message_return_data:

        augur_msg_id = data["msg_id"]
        platform_message_id = data["platform_msg_id"]

        ref = message_ref_mapping_data[platform_message_id]
        message_ref_data = ref["msg_ref_data"]
        message_ref_data["msg_id"] = augur_msg_id

        issue_message_ref_dicts.append(message_ref_data)

    logger.info(f"{task_name}: Inserting {len(issue_message_ref_dicts)} gitlab issue messages ref rows")
    issue_message_ref_natural_keys = ["issue_id", "issue_msg_ref_src_comment_id"]
    bulk_insert_dicts(logger, issue_message_ref_dicts, IssueMessageRef, issue_message_ref_natural_keys)


def process_gitlab_issue_comment_contributors(message, tool_source, tool_version, data_source):

    contributor = extract_needed_gitlab_contributor_data(message["author"], tool_source, tool_version, data_source)
    if contributor:
        message["cntrb_id"] = contributor["cntrb_id"]
    else:
        message["cntrb_id"] = None

    return message, contributor