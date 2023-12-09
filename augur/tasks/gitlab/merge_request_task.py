import logging

from augur.tasks.init.celery_app import celery_app as celery
from augur.tasks.init.celery_app import AugurCoreRepoCollectionTask
from augur.tasks.gitlab.gitlab_api_handler import GitlabApiHandler
from augur.tasks.gitlab.gitlab_task_session import GitlabTaskManifest
from augur.application.db.data_parse import extract_needed_pr_data_from_gitlab_merge_request, extract_needed_merge_request_assignee_data, extract_needed_mr_label_data
from augur.tasks.github.util.util import get_owner_repo, add_key_value_pair_to_dicts
from augur.application.db.models import PullRequest, PullRequestAssignee, PullRequestLabel, Repo


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_gitlab_merge_requests(repo_git: str) -> int:


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
    mr_assignee_natural_keys = ['pr_assignee_src_id', 'pull_request_id']
    augur_db.insert_data(mr_assignee_dicts, PullRequestAssignee, mr_assignee_natural_keys)

    pr_label_natural_keys = ['pr_src_id', 'pull_request_id']
    pr_label_string_fields = ["pr_src_description"]
    augur_db.insert_data(mr_label_dicts, PullRequestLabel, pr_label_natural_keys, string_fields=pr_label_string_fields)

    return mr_ids



@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_comments(mr_ids, repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_comments.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/notes".format(owner=owner, repo=repo, id="{id}")
        comments = retrieve_merge_request_data(mr_ids, url, "comments", owner, repo, manifest.key_auth, logger, response_type="list")

        if comments:
            logger.info(f"Length of merge request comments: {len(comments)}")
            logger.info(f"Mr comment: {comments[0]}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request comments")



@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_events(repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    url = f"https://gitlab.com/api/v4/projects/{owner}%2f{repo}/events?target_type=merge_request"
    #print("Collect merge request events")
    # print(f"Repo git: {repo_git}. Len ids: {mr_ids}")


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_metadata(mr_ids, repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_metadata.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}".format(owner=owner, repo=repo, id="{id}")
        metadata_list = retrieve_merge_request_data(mr_ids, url, "metadata", owner, repo, manifest.key_auth, logger, response_type="dict")

        if metadata_list:
            logger.info(f"Length of merge request metadata: {len(metadata_list)}")
            logger.info(f"Mr metadata: {metadata_list[0]}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request metadata")
    


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_reviewers(mr_ids, repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_reviewers.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/approvals".format(owner=owner, repo=repo, id="{id}")
        reviewers = retrieve_merge_request_data(mr_ids, url, "reviewers", owner, repo, manifest.key_auth, logger, response_type="dict")

        if reviewers:
            logger.info(f"Length of merge request reviewers: {len(reviewers)}")
            logger.info(f"Mr reviewer: {reviewers[0]}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request reviewers")
    

@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_commits(mr_ids, repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_comments.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/commits".format(owner=owner, repo=repo, id="{id}")
        commits = retrieve_merge_request_data(mr_ids, url, "commits", owner, repo, manifest.key_auth, logger, response_type="list")

        if commits:
            logger.info(f"Length of merge request commits: {len(commits)}")
            logger.info(f"Mr commit: {commits[0]}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request commits")


@celery.task(base=AugurCoreRepoCollectionTask)
def collect_merge_request_files(mr_ids, repo_git) -> int:

    owner, repo = get_owner_repo(repo_git)

    logger = logging.getLogger(collect_merge_request_comments.__name__) 
    with GitlabTaskManifest(logger) as manifest:

        url = "https://gitlab.com/api/v4/projects/{owner}%2f{repo}/merge_requests/{id}/changes".format(owner=owner, repo=repo, id="{id}")
        files = retrieve_merge_request_data(mr_ids, url, "files", owner, repo, manifest.key_auth, logger, response_type="dict")

        if files:
            logger.info(f"Length of merge request files: {len(files)}")
            logger.info(f"Mr file: {files[0]}")
            #issue_ids = process_issues(issue_data, f"{owner}/{repo}: Gitlab Issue task", repo_id, logger, augur_db)
        else:
            logger.info(f"{owner}/{repo} has no gitlab merge request files")
    

def retrieve_merge_request_data(ids, url, name, owner, repo, key_auth, logger, response_type):

    all_data = []
    issue_count = len(ids)
    index = 1

    api_handler = GitlabApiHandler(key_auth, logger)
    for id in ids:

        if len(all_data) > 10:
            return all_data
        
        print(f"Collecting {owner}/{repo} gitlab merge request {name} for merge request {index} of {issue_count}")
        formatted_url = url.format(id=id)

        if response_type == "dict":
            page_data, _, _ = api_handler.retrieve_data(formatted_url)
            if page_data:
                all_data.append(page_data)

        elif response_type == "list":

            for page_data, _ in api_handler.iter_pages(formatted_url):

                if page_data is None or len(page_data) == 0:
                    break

                all_data += page_data

        else:
            raise Exception(f"Unexpected reponse type: {response_type}")
        
        index += 1

    return all_data
