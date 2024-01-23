import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_api_handler import GitlabApiHandler
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_pr_data_from_gitlab_merge_request, extract_needed_merge_request_assignee_data, extract_needed_mr_label_data, extract_needed_mr_reviewer_data, extract_needed_mr_commit_data, extract_needed_mr_file_data, extract_needed_mr_metadata, extract_needed_gitlab_mr_message_ref_data, extract_needed_gitlab_message_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import PullRequest, PullRequestAssignee, PullRequestLabel, PullRequestReviewer, PullRequestMeta, PullRequestCommit, PullRequestFile, PullRequestMessageRef, Repo, Message
from augur.application.db.util import execute_session_query

platform_id = 2

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_merge_requests(repo_git: str) -> int:
    """
    Retrieve and parse gitlab MRs for the desired repo

    Arguments:
        repo_git: the repo url string
    """


    logger = logging.getLogger(collect_gitlab_merge_requests.__name__)

    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        repo_id = augur_db.session.query(Repo).filter(
        Repo.repo_git == repo_git).one().repo_id

        owner, repo = get_owner_repo(repo_git)
        mr_data = retrieve_all_mr_data(repo_git, logger, manifest.key_auth)

        if mr_data:
            mr_ids = process_merge_requests(mr_data, f"{owner}/{repo}: Mr task", repo_id, logger, augur_db)

            return mr_ids
        else:
            logger.info(f"{owner}/{repo} has no merge requests")
            return []


def retrieve_all_mr_data(repo_git: str, logger, key_auth) -> None:
    """
    Retrieve only the needed data for MRs from the api response

    Arguments:
        repo_git: url of the relevant repo
        logger: loggin object
        key_auth: key auth cache and rotator object 
    """

    owner, repo = get_owner_repo(repo_git)

    logger.info(f"Collecting pull requests for {owner}/{repo}")

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests?with_labels_details=True"
    mrs = GitlabApiHandler(key_auth, logger)

    all_data = []
    num_pages = mrs.get_num_pages(url)
    for page_data, page in mrs.iter_pages(url):

        if page_data is None:
            return all_data

        if len(page_data) == 0:
            logger.debug(
                f"{owner}/{repo} Mrs Page {page} contains no data...returning")
            logger.info(f"{owner}/{repo} Mrs Page {page} of {num_pages}")
            return all_data

        logger.info(f"{owner}/{repo} Mrs Page {page} of {num_pages}")

        all_data += page_data

    return all_data


def process_merge_requests(data, task_name, repo_id, logger, augur_db):
    """
    Retrieve only the needed data for mr label data from the api response

    Arguments:
        data: collection of mr data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        augur_db: sqlalchemy db object 
    
    Returns:
        List of parsed MR ids.
    """

    tool_source = "Mr Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    merge_requests = []
    mr_ids = []
    mr_mapping_data = {}
    for mr in data:

        mr_ids.append(mr["iid"])

        merge_requests.append(extract_needed_pr_data_from_gitlab_merge_request(mr, repo_id, tool_source, tool_version))

        assignees = extract_needed_merge_request_assignee_data(mr["assignees"], repo_id, tool_source, tool_version, data_source)

        labels = extract_needed_mr_label_data(mr["labels"], repo_id, tool_source, tool_version, data_source)

        mapping_data_key = mr["id"]
        mr_mapping_data[mapping_data_key] = {
                                            "assignees": assignees,
                                            "labels": labels
                                            }          

    logger.info(f"{task_name}: Inserting mrs of length: {len(merge_requests)}")
    pr_natural_keys = ["repo_id", "pr_src_id"]
    pr_string_fields = ["pr_src_title", "pr_body"]
    pr_return_columns = ["pull_request_id", "pr_src_id"]
    pr_return_data = augur_db.insert_data(merge_requests, PullRequest, pr_natural_keys, return_columns=pr_return_columns, string_fields=pr_string_fields)


    mr_assignee_dicts = []
    mr_label_dicts = []
    for data in pr_return_data:

        mr_src_id = data["pr_src_id"]
        pull_request_id = data["pull_request_id"]

        try:
            other_mr_data = mr_mapping_data[mr_src_id]
        except KeyError as e:
            logger.info(f"Cold not find other pr data. This should never happen. Error: {e}")

        dict_key = "pull_request_id"
        mr_assignee_dicts += add_key_value_pair_to_dicts(other_mr_data["assignees"], dict_key, pull_request_id)
        mr_label_dicts += add_key_value_pair_to_dicts(other_mr_data["labels"], dict_key, pull_request_id)

    logger.info(f"{task_name}: Inserting other pr data of lengths: Labels: {len(mr_label_dicts)} - Assignees: {len(mr_assignee_dicts)}")

    # TODO: Setup unique key on asignees with a value of ('cntrb_id', 'pull_request_id') and add 'cntrb_id' to assingee data
    # mr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    # augur_db.insert_data(mr_assignee_dicts, PullRequestAssignee, mr_assignee_natural_keys)

    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    pr_label_string_fields = ["pr_src_description"]
    augur_db.insert_data(mr_label_dicts, PullRequestLabel, pr_label_natural_keys, string_fields=pr_label_string_fields)

    return mr_ids



@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_comments(mr_ids, repo_git) -> int:
    """
    Retrieve and parse gitlab events for the desired repo

    Arguments:
        mr_ids: ids of MRs to paginate comments for
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_comments.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/notes".format(owner=owner, repo=repo, id="{id}")
        comments = retrieve_merge_request_data(mr_ids, url, "comments", owner, repo, manifest.key_auth, logger, response_type="list")

        if comments:
            logger.info(f"Length of merge request comments: {len(comments)}")
            process_gitlab_mr_messages(comments, f"{owner}/{repo}: Gitlab mr messages task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request comments")


def process_gitlab_mr_messages(data, task_name, repo_id, logger, augur_db):
    """
    Retrieve only the needed data for mr label data from the api response

    Arguments:
        data: List of dictionaries of mr message data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        augur_db: sqlalchemy db object 
    """

    tool_source = "Gitlab mr comments"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    message_dicts = []
    message_ref_mapping_data = {}
    for id, messages in data.items():

        try:
                pull_request_id = mr_number_to_id_map[id]
        except KeyError:
            logger.info(f"{task_name}: Could not find related mr")
            logger.info(f"{task_name}: We were searching for mr number {id} in repo {repo_id}")
            logger.info(f"{task_name}: Skipping")
            continue

        for message in messages:

            mr_message_ref_data = extract_needed_gitlab_mr_message_ref_data(message, pull_request_id, repo_id, tool_source, tool_version, data_source)

            message_ref_mapping_data[message["id"]] = {
                "msg_ref_data": mr_message_ref_data
            }

            message_dicts.append(
                extract_needed_gitlab_message_data(message, platform_id, tool_source, tool_version, data_source)
            )


    logger.info(f"{task_name}: Inserting {len(message_dicts)} messages")
    message_natural_keys = ["platform_msg_id"]
    message_return_columns = ["msg_id", "platform_msg_id"]
    message_string_fields = ["msg_text"]
    message_return_data = augur_db.insert_data(message_dicts, Message, message_natural_keys, 
                                                return_columns=message_return_columns, string_fields=message_string_fields)
    
    mr_message_ref_dicts = []
    for data in message_return_data:

        augur_msg_id = data["msg_id"]
        platform_message_id = data["platform_msg_id"]

        ref = message_ref_mapping_data[platform_message_id]
        message_ref_data = ref["msg_ref_data"]
        message_ref_data["msg_id"] = augur_msg_id

        mr_message_ref_dicts.append(message_ref_data)

    logger.info(f"{task_name}: Inserting {len(mr_message_ref_dicts)} mr messages ref rows")
    mr_message_ref_natural_keys = ["pull_request_id", "pr_message_ref_src_comment_id"]
    augur_db.insert_data(mr_message_ref_dicts, PullRequestMessageRef, mr_message_ref_natural_keys)


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_metadata(mr_ids, repo_git) -> int:
    """
    Retrieve and parse gitlab events for the desired repo

    Arguments:
        mr_ids: list of mr ids to find metadata for
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_metadata.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}".format(owner=owner, repo=repo, id="{id}")
        metadata_list = retrieve_merge_request_data(mr_ids, url, "metadata", owner, repo, manifest.key_auth, logger, response_type="dict")

        if metadata_list:
            logger.info(f"Length of merge request metadata: {len(metadata_list)}")
            process_mr_metadata(metadata_list, f"{owner}/{repo}: Mr metadata task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request metadata")

def process_mr_metadata(data, task_name, repo_id, logger, augur_db):
    """
    Retrieve only the needed data for mr label data from the api response

    Arguments:
        data: List of dictionaries of mr metadata
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        augur_db: sqlalchemy db object 
    """

    tool_source = "Mr Metadata Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    all_metadata = []
    for id, metadata in data.items():

        pull_request_id = mr_number_to_id_map[id]

        all_metadata.extend(extract_needed_mr_metadata(metadata, repo_id, pull_request_id, tool_source, tool_version, data_source))

    logger.info(f"{task_name}: Inserting {len(all_metadata)} merge request metadata")
    pr_metadata_natural_keys = ['pull_request_id', 'pr_head_or_base', 'pr_sha']
    augur_db.insert_data(all_metadata, PullRequestMeta, pr_metadata_natural_keys)
    

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_reviewers(mr_ids, repo_git) -> int:
    """
    Retrieve and parse mr reviewers for the desired repo

    Arguments:
        mr_ids: mrs to search for reviewers for
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_reviewers.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/approvals".format(owner=owner, repo=repo, id="{id}")
        reviewers = retrieve_merge_request_data(mr_ids, url, "reviewers", owner, repo, manifest.key_auth, logger, response_type="dict")

        if reviewers:
            logger.info(f"Length of merge request reviewers: {len(reviewers)}")
            process_mr_reviewers(reviewers, f"{owner}/{repo}: Mr reviewer task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request reviewers")

def process_mr_reviewers(data, task_name, repo_id, logger, augur_db):
    """
    Retrieve only the needed data for mr reviewer data from the api response

    Arguments:
        data: List of dictionaries of mr reviewer data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        augur_db: sqlalchemy db object 
    """

    tool_source = "Mr Reviewr Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    all_reviewers = []
    for id, values in data.items():

        pull_request_id = mr_number_to_id_map[id]

        reviewers = extract_needed_mr_reviewer_data(values, pull_request_id, tool_source, tool_version, data_source)

        all_reviewers += reviewers

    # TODO: Need to add unique key with pull_request_id and cntrb_id to insert gitlab reviewers
    # pr_reviewer_natural_keys = ["pull_request_id", "cntrb_id"]
    # augur_db.insert_data(all_reviewers, PullRequestReviewer, pr_reviewer_natural_keys)



@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_commits(mr_ids, repo_git) -> int:
    """
    Retrieve and parse mr commits for the desired repo

    Arguments:
        mr_ids: ids of mrs to get commits for
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_commits.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/commits".format(owner=owner, repo=repo, id="{id}")
        commits = retrieve_merge_request_data(mr_ids, url, "commits", owner, repo, manifest.key_auth, logger, response_type="list")

        if commits:
            logger.info(f"Length of merge request commits: {len(commits)}")
            process_mr_commits(commits, f"{owner}/{repo}: Mr commit task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request commits")


def process_mr_commits(data, task_name, repo_id, logger, augur_db):
    """
    Retrieve only the needed data for mr commits from the api response

    Arguments:
        data: List of dictionaries of mr commit data
        task_name: name of the task as well as the repo being processed
        repo_id: augur id of the repo
        logger: logging object
        augur_db: sqlalchemy db object 
    """

    tool_source = "Mr Commit Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    all_commits = []
    for id, values in data.items():

        pull_request_id = mr_number_to_id_map[id]

        for commit in values:

            all_commits.append(extract_needed_mr_commit_data(commit, repo_id, pull_request_id, tool_source, tool_version, data_source))


    logger.info(f"{task_name}: Inserting {len(all_commits)} merge request commits")
    pr_commits_natural_keys = ["pull_request_id", "repo_id", "pr_cmt_sha"]
    augur_db.insert_data(all_commits,PullRequestCommit,pr_commits_natural_keys)
            


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_files(mr_ids, repo_git) -> int:
    """
    Retrieve and parse gitlab events for the desired repo

    Arguments:
        mr_ids: the ids of mrs to get files for.
        repo_git: the repo url string
    """

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_files.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        augur_db = manifest.augur_db

        query = augur_db.session.query(Repo).filter(Repo.repo_git == repo_git)
        repo_obj = execute_session_query(query, 'one')
        repo_id = repo_obj.repo_id

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/changes".format(owner=owner, repo=repo, id="{id}")
        files = retrieve_merge_request_data(mr_ids, url, "files", owner, repo, manifest.key_auth, logger, response_type="dict")

        if files:
            logger.info(f"Length of merge request files: {len(files)}")
            process_mr_files(files, f"{owner}/{repo}: Mr files task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request files")

def process_mr_files(data, task_name, repo_id, logger, augur_db):

    tool_source = "Mr files Task"
    tool_version = "2.0"
    data_source = "Gitlab API"

    # create mapping from mr number to pull request id of current mrs
    mr_number_to_id_map = {}
    mrs = augur_db.session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    for mr in mrs:
        mr_number_to_id_map[mr.pr_src_number] = mr.pull_request_id

    all_files = []
    for id, gitlab_file_data in data.items():

        pull_request_id = mr_number_to_id_map[id]

        all_files.extend(extract_needed_mr_file_data(gitlab_file_data, repo_id, pull_request_id, tool_source, tool_version, data_source))

    logger.info(f"{task_name}: Inserting {len(all_files)} merge request files")
    pr_file_natural_keys = ["pull_request_id", "repo_id", "pr_file_path"]
    augur_db.insert_data(all_files, PullRequestFile, pr_file_natural_keys)
    

def retrieve_merge_request_data(ids, url, name, owner, repo, key_auth, logger, response_type):
    """
    Retrieve specific mr data from the GitLab api.  

    Arguments:
        ids: mr ids to paginate info for
        url: endpoint to paginate or hit
        name: name of data to collect
        owner: owner of the repo
        repo: repo name
        key_auth: key auth cache and rotator object
        logger: loggin object
        response_type: type of data to get from the api 
    """

    all_data = {}
    mr_count = len(ids)
    index = 1

    api_handler = GitlabApiHandler(key_auth, logger)
    for id in ids:
        
        print(f"Collecting {owner}/{repo} gitlab merge request {name} for merge request {index} of {mr_count}")
        formatted_url = url.format(id=id)

        if response_type == "dict":
            page_data, _, _ = api_handler.retrieve_data(formatted_url)
            if page_data:
                all_data[id] = page_data

        elif response_type == "list":

            for page_data, _ in api_handler.iter_pages(formatted_url):

                if page_data is None or len(page_data) == 0:
                    break

                if id in all_data:
                    all_data[id].extend(page_data)
                else:
                    all_data[id] = page_data
        else:
            raise Exception(f"Unexpected reponse type: {response_type}")
        
        index += 1

    return all_data
