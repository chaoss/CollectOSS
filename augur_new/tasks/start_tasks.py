from .issue_tasks import *


@app.task
def start(owner: str, repo):
    
    logger = get_task_logger(start.name)
    session = TaskSession(logger, config)

    logger.info(f"Collecting data for {owner}/{repo}")
    
    result = get_repo_id.apply_async(args=(owner, repo), ignore_result=False)



    # start_task_list = []
    # start_task_list.append(pull_requests.s(owner, repo))
    # # start_task_list.append(issues.s(owner, repo))

    # start_tasks_group = group(start_task_list)


    # secondary_task_list = []
    # # task_list.append(pull_request_reviews.s(owner, repo))
    # # secondary_task_list.append(github_events.s(owner, repo))
    # # task_list.append(github_messages.s(owner, repo))
    
    # secondary_task_group = group(secondary_task_list)

    # job = chain(
    #     start_tasks_group,
    #     secondary_task_group,
    # )

    # job.apply_async()

@app.task
def get_repo_id(owner, repo):

    logger = get_task_logger(get_repo_id.name)
    session = TaskSession(logger, config)

    url = f"https://api.github.com/orgs/{owner}/repos"

    repos = GithubPaginator(url, session.oauths, logger)

    repo_data = None

    for repo_dict in repos:


        if repo_dict["name"] == repo:

            gh_repo_id = repo_dict["id"]
            gh_owner_id = repo_dict["owner"]["id"]

            augur_repo_id = str(gh_owner_id) + str(gh_repo_id)
            augur_repo_id_int = int(augur_repo_id)


            return augur_repo_id_int
            


start("chaoss", "augur")