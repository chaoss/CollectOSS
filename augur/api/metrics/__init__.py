from augur.application.db.lib import get_repos_in_legacy_repo_group


def get_request_repo_ids(repo_id, repo_group_id):

    repo_ids = []
    if repo_id:
        repo_ids.append(repo_id)
    else:
        repo_ids.append(get_repos_in_legacy_repo_group(repo_group_id))

    return tuple(repo_ids)