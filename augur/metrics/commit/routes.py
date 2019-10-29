from flask import Response

def create_commit_routes(server):

    metrics = server._augur.metrics

    """
    @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-new-repo-in-repo-group Annual Commit Count Ranked by New Repo in Repo Group(Repo Group)
    @apiName annual-commit-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoGroupMetric(metrics.annual_commit_count_ranked_by_new_repo_in_repo_group,'annual-commit-count-ranked-by-new-repo-in-repo-group')

    """
    @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-new-repo-in-repo-group Annual Commit Count Ranked by New Repo in Repo Group(Repo)
    @apiName annual-commit-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoMetric(metrics.annual_commit_count_ranked_by_new_repo_in_repo_group,'annual-commit-count-ranked-by-new-repo-in-repo-group')

    """
    @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-repo-in-repo-group Annual Commit Count Ranked by Repo in Repo Group(Repo Group)
    @apiName annual-commit-count-ranked-by-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "repo_name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "repo_name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoGroupMetric(metrics.annual_commit_count_ranked_by_repo_in_repo_group,'annual-commit-count-ranked-by-repo-in-repo-group')

    """
     @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-repo-in-repo-group Annual Commit Count Ranked by Repo in Repo Group(Repo)
    @apiName annual-commit-count-ranked-by-repo-in-repo-group
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoMetric(metrics.annual_commit_count_ranked_by_repo_in_repo_group,'annual-commit-count-ranked-by-repo-in-repo-group')

