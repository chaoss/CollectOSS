from flask import Response

def create_util_routes(server):

    metrics = server._augur.metrics

    """
    @api {get} /repo-groups Repo Groups
    @apiName repo-groups
    @apiGroup Utility
    @apiDescription Get all the downloaded repo groups.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "rg_name": "Rails",
                            "rg_description": "Rails Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:25.000Z"
                        },
                        {
                            "repo_group_id": 23,
                            "rg_name": "Netflix",
                            "rg_description": "Netflix Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:36.000Z"
                        }
                    ]
    """
    @server.app.route('/{}/repo-groups'.format(server.api_version))
    def get_repo_groups(): #TODO: make this name automatic - wrapper?
        drs = server.transform(metrics.repo_groups)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=metrics.repo_groups, endpoint='/{}/repo-groups'.format(server.api_version), metric_type='git')

    """
    @api {get} /repos Repos
    @apiName repos
    @apiGroup Utility
    @apiDescription Get all the downloaded repos.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21996,
                            "repo_name": "incubator-argus",
                            "description": null,
                            "url": "github.com\/apache\/incubator-argus.git",
                            "repo_status": "Update",
                            "commits_all_time": null,
                            "issues_all_time": null,
                            "rg_name": "Apache",
                            "base64_url": "Z2l0aHViLmNvbS9hcGFjaGUvaW5jdWJhdG9yLWFyZ3VzLmdpdA=="
                        },
                        {
                            "repo_id": 21729,
                            "repo_name": "tomee-site",
                            "description": null,
                            "url": "github.com\/apache\/tomee-site.git",
                            "repo_status": "Complete",
                            "commits_all_time": 224216,
                            "issues_all_time": 2,
                            "rg_name": "Apache",
                            "base64_url": "Z2l0aHViLmNvbS9hcGFjaGUvdG9tZWUtc2l0ZS5naXQ="
                        }
                    ]
    """
    @server.app.route('/{}/repos'.format(server.api_version))
    def downloaded_repos():
        drs = server.transform(metrics.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=metrics.downloaded_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    """
    @api {get} /repo-groups/:repo_group_id/repos Repos in Repo Group
    @apiName repos-in-repo-groups
    @apiGroup Utility
    @apiDescription Get all the repos in a repo group.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "repo_name": "graphql-js",
                            "description": null,
                            "url": "https:\/\/github.com\/graphql\/graphql-js.git",
                            "repo_status": "Complete",
                            "commits_all_time": 6874,
                            "issues_all_time": 81
                        },
                        {
                            "repo_id": 21331,
                            "repo_name": "graphiql",
                            "description": null,
                            "url": "https:\/\/github.com\/graphql\/graphiql.git",
                            "repo_status": "Complete",
                            "commits_all_time": 4772,
                            "issues_all_time": 144
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.repos_in_repo_groups, 'repos')

    """
    @api {get} /owner/:owner/repo/:repo Get Repo
    @apiName get-repo
    @apiGroup Utility
    @apiDescription Get the `repo_group_id` & `repo_id` of a particular repo.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21339,
                            "repo_group_id": 23
                        },
                        {
                            "repo_id": 21000,
                            "repo_group_id": 20
                        }
                    ]
    """
    @server.app.route('/{}/owner/<owner>/name/<repo>'.format(server.api_version))
    def get_repo_by_git_name(owner, repo):
        a = [owner, repo]
        gre = server.transform(metrics.get_repo_by_git_name, args = a)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    """
    @api {get} /rg-name/:rg_name/repo-name/:repo_name Get Repo
    @apiName get-repo
    @apiGroup Utility
    @apiDescription Get the `repo_group_id` & `repo_id` of a particular repo.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_group_id": 20,
                            "repo_git":"https://github.com/rails/rails.git"
                        },
                    ]
    """
    @server.app.route('/{}/rg-name/<rg_name>/repo-name/<repo_name>'.format(server.api_version))
    def get_repo_by_name(rg_name, repo_name):
        arg = [rg_name, repo_name]
        gre = server.transform(metrics.get_repo_by_name, args=arg)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    """
    @api {get} /rg-names/:rg_name Get Repo
    @apiName get-repo
    @apiGroup Utility
    @apiDescription Get the `repo_id` of a particular repo group.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "rg_name": 'Rails'
                        },
                    ]
    """
    @server.app.route('/{}/rg-name/<rg_name>'.format(server.api_version))
    def get_group_by_name(rg_name):
        arg = [rg_name]
        res = server.transform(metrics.get_group_by_name, args=arg)
        return Response(response=res,
                        status=200,
                        mimetype="application/json")


    @server.app.route('/{}/dosocs/repos'.format(server.api_version))
    def get_repos_for_dosocs():
        res = server.transform(metrics.get_repos_for_dosocs)
        return Response(response=res,
                        status=200,
                        mimetype='application/json')

    server.addRepoGroupMetric(metrics.get_issues, 'get-issues')
    server.addRepoMetric(metrics.get_issues, 'get-issues')

    """
    @api {get} /top-insights Top Insights
    @apiName top-insights
    @apiGroup Utility
    @apiDescription Get all the downloaded repo groups.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "rg_name": "Rails",
                            "rg_description": "Rails Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:25.000Z"
                        },
                        {
                            "repo_group_id": 23,
                            "rg_name": "Netflix",
                            "rg_description": "Netflix Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:36.000Z"
                        }
                    ]
    """
    # @server.app.route('/{}/top-insights'.format(server.api_version))
    # def top_insights(): #TODO: make this name automatic - wrapper?
    #     tis = server.transform(metrics.top_insights)
    #     return Response(response=tis,
    #                     status=200,
    #                     mimetype="application/json")
    # server.updateMetricMetadata(function=metrics.top_insights, endpoint='/{}/top-insights'.format(server.api_version), metric_type='git')

    """
    @api {get} /repo-groups/:repo_group_id/aggregate-summary Aggregate Summary (Repo Group)
    @apiName aggregate-summary-repo-group
    @apiGroup Experimental
    @apiDescription Returns the current count of watchers, stars, and forks and the counts of all commits, committers, and pull requests merged between a given beginning and end date (default between now and 365 days ago).
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "watcher_count": 69106,
                            "star_count": 460447,
                            "fork_count": 226841,
                            "merged_count": 3883,
                            "committer_count": 8553,
                            "commit_count": 7890143
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.aggregate_summary, 'aggregate-summary')

    """
    @api {get} /repos/:repo_id/aggregate-summary Aggregate Summary (Repo)
    @apiName aggregate-summary-repo
    @apiGroup Experimental
    @apiDescription Returns the current count of watchers, stars, and forks and the counts of all commits, committers, and pull requests merged between a given beginning and end date (default between now and 365 days ago).
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "watcher_count": 83,
                            "star_count": 581,
                            "fork_count": 449,
                            "merged_count": 0,
                            "committer_count": 5,
                            "commit_count": 133
                        }
                    ]
    """
    server.addRepoMetric(metrics.aggregate_summary, 'aggregate-summary')