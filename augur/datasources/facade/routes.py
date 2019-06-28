#SPDX-License-Identifier: MIT
"""
Creates routes for the facade data source plugin
"""

from flask import Response, request, jsonify


def create_routes(server):

    facade = server._augur['facade']()

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################

    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    #####################################
    ###            RISK               ###
    #####################################

    #####################################
    ###            VALUE              ###
    #####################################

    #####################################
    ###           ACTIVITY            ###
    #####################################

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    @server.app.route('/{}/facade/cli_add_project'.format(server.api_version), methods=['POST'])
    def cli_add_project():
        name = request.args.get('name')
        description = request.args.get('description')
        website = request.args.get('website')

        data = facade.cli_add_project(name, description, website).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/facade/cli_delete_project'.format(server.api_version), methods=['POST'])
    def cli_delete_project():
        project_id = request.args.get('project_id')

        data = facade.cli_delete_project(project_id).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/facade/cli_add_repo'.format(server.api_version), methods=['POST'])
    def cli_add_repo():
        project_id = request.args.get('project_id')
        git_repo = request.args.get('git_repo')

        data = facade.cli_add_repo(project_id, git_repo).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")


    @server.app.route('/{}/facade/cli_delete_repo'.format(server.api_version), methods=['POST'])
    def cli_delete_repo():
        git_repo = request.args.get('git_repo')

        data = facade.cli_delete_repo(git_repo).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")


    @server.app.route('/{}/facade/cli_add_alias'.format(server.api_version), methods=['POST'])
    def cli_add_alias():
        alias = request.args.get('alias')
        canonical = request.args.get('canonical')

        data = facade.cli_add_alias(alias, canonical).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/facade/cli_delete_alias'.format(server.api_version), methods=['POST'])
    def cli_delete_alias():
        alias_id = request.args.get('alias_id')

        data = facade.cli_delete_alias(alias_id).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")


    @server.app.route('/{}/facade/cli_add_affiliation'.format(server.api_version), methods=['POST'])
    def cli_add_affiliation():
        domain = request.args.get('domain')
        affiliation = request.args.get('affiliation')
        start_date = request.args.get('start_date')

        data = facade.cli_add_affiliation(domain, affiliation, start_date).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/facade/cli_delete_affiliation'.format(server.api_version), methods=['POST'])
    def cli_delete_affiliation():
        affiliation_id = request.args.get('affiliation_id')

        data = facade.cli_delete_affiliation(affiliation_id).keys()

        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    """
    @api {get} /git/repos Facade Downloaded Repos
    @apiName facade-downloaded-repos
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "url": "github.com\/twitter\/twemoji",
                                "status": "Update",
                                "project_name": "Twitter",
                                "base64_url": "Z2l0aHViLmNvbS90d2l0dGVyL3R3ZW1vamk="
                            },
                            {
                                "url": "github.com\/twitter\/hadoop-lzo.git",
                                "status": "Complete",
                                "project_name": "Twitter",
                                "base64_url": "Z2l0aHViLmNvbS90d2l0dGVyL2hhZG9vcC1sem8uZ2l0"
                            }
                        ]
    """
    @server.app.route('/{}/git/repos'.format(server.api_version))
    def facade_downloaded_repos(): #TODO: make this name automatic - wrapper?
        drs = server.transform(facade.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=facade.downloaded_repos, endpoint='/{}/git/repos'.format(server.api_version), metric_type='git')

    """
    @api {get} /git/changes_by_author Lines Changed by Author
    @apiName lines-changed-by-author
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "author_email":"s@goggins.com",
                                "author_date":"2018-05-14",
                                "affiliation": "(Unknown)",
                                "additions":2,
                                "deletions":0,
                                "whitespace": 3
                            }
                        ]
    """
    server.addGitMetric(facade.lines_changed_by_author, 'changes_by_author')

    """
    @api {get} /git/lines_changed_by_week Lines Changed by Week
    @apiName lines-changed-by-week
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2014-11-07T00:00:00.000Z",
                                "additions": 1263564,
                                "deletions": 1834,
                                "whitespace": 27375
                            }
                        ]
    """
    server.addGitMetric(facade.lines_changed_by_week, 'lines_changed_by_week')

    """
    @api {get} /git/lines_changed_by_month Lines Changed by Month
    @apiName lines-changed-by-month
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "author_email": "agiammarchi@twitter.com",
                                "affiliation": "Twitter",
                                "month": 11,
                                "year": 2014,
                                "additions": 5477,
                                "deletions": 50511,
                                "whitespace": 37
                            },
                            {
                                "author_email": "andrea.giammarchi@gmail.com",
                                "affiliation": "(Unknown)",
                                "month": 11,
                                "year": 2014,
                                "additions": 0,
                                "deletions": 0,
                                "whitespace": 0
                            }
                        ]
    """
    server.addGitMetric(facade.lines_changed_by_month, 'lines_changed_by_month')

    """
    @api {get} /git/commits_by_week Commits By Week
    @apiName commits-by-week
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "author_email": "andrea.giammarchi@gmail.com",
                                "affiliation": "(Unknown)",
                                "week": 44,
                                "year": 2014,
                                "patches": 1
                            },
                            {
                                "author_email": "caniszczyk@gmail.com",
                                "affiliation": "(Unknown)",
                                "week": 44,
                                "year": 2014,
                                "patches": 5
                            }
                        ]
    """
    server.addGitMetric(facade.commits_by_week, 'commits_by_week')

    """
    @api {get} /git/facade_project Facade Project
    @apiName facade-project
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "name": "Twitter"
                            }
                        ]
    """
    server.addGitMetric(facade.facade_project, 'facade_project')

    """
    @api {get} /git/annual_lines_of_code_count_ranked_by_repo_in_repo_group Annual Lines of Code Count Ranked by Repo in Repo Group
    @apiName annual-lines-of-code-count-ranked-by-repo-in-repo-group
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "name": "twemoji",
                                "net": 2479124.0,
                                "patches": 1
                            },
                            {
                                "repos_id": 63,
                                "name": "twemoji-1",
                                "net": 2477911.0,
                                "patches": 1
                            }
                        ]
    """
    @server.app.route('/{}/git/annual_lines_of_code_count_ranked_by_repo_in_repo_group'.format(server.api_version))
    def annual_lines_of_code_count_ranked_by_repo_in_repo_group():

        repo_url_base = request.args.get('repo_url_base')

        timeframe = request.args.get('timeframe')
        repo_group = request.args.get('repo_group')

        data = server.transform(facade.annual_lines_of_code_count_ranked_by_repo_in_repo_group, args=([]), repo_url_base=repo_url_base, kwargs=({'timeframe': timeframe, 'repo_group': repo_group}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/annual_commit_count_ranked_by_repo_in_repo_group Annual Commit Count Ranked by Repo in Repo Group
    @apiName annual-commit-count-ranked-by-repo-in-repo-group
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "name": "twemoji",
                                "net": 2479124.0,
                                "patches": 1
                            },
                            {
                                "repos_id": 63,
                                "name": "twemoji-1",
                                "net": 2477911.0,
                                "patches": 1
                            }
                        ]
    """
    # server.addGitMetric(facade.top_repos_commits, 'top_repos_commits')
    @server.app.route('/{}/git/annual_commit_count_ranked_by_repo_in_repo_group'.format(server.api_version))
    def annual_commit_count_ranked_by_repo_in_repo_group():

        repo_url_base = request.args.get('repo_url_base')

        timeframe = request.args.get('timeframe')
        repo_group = request.args.get('repo_group')

        data = server.transform(facade.annual_commit_count_ranked_by_repo_in_repo_group, args=([]), repo_url_base=repo_url_base, kwargs=({'timeframe': timeframe, 'repo_group': repo_group}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/annual_lines_of_code_count_ranked_by_new_repo_in_repo_group Annual Lines of Code Count Ranked by New Repo in Repo Group
    @apiName annual-lines-of-code-count-ranked-by-new-repo-in-repo-group
    @apiGroup Facade (Legacy)
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
    @server.app.route('/{}/git/annual_lines_of_code_count_ranked_by_new_repo_in_repo_group'.format(server.api_version))
    def annual_lines_of_code_count_ranked_by_new_repo_in_repo_group():

        repo_url_base = request.args.get('repo_url_base')

        calendar_year = request.args.get('calendar_year')
        repo_group = request.args.get('repo_group')

        data = server.transform(facade.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group, args=([]), repo_url_base=repo_url_base, kwargs=({'calendar_year': calendar_year, 'repo_group': repo_group}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/annual_commit_count_ranked_by_new_repo_in_repo_group Annual Commit Count Ranked by New Repo in Repo Group
    @apiName annual-commit-count-ranked-by-new-repo-in-repo-group
    @apiGroup Facade (Legacy)
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
    # server.addGitMetric(facade.annual_commit_count_ranked_by_new_repo_in_repo_group, 'top_new_repos_commits')
    @server.app.route('/{}/git/annual_commit_count_ranked_by_new_repo_in_repo_group'.format(server.api_version))
    def annual_commit_count_ranked_by_new_repo_in_repo_group():

        repo_url_base = request.args.get('repo_url_base')

        calendar_year = request.args.get('calendar_year')
        repo_group = request.args.get('repo_group')

        data = server.transform(facade.annual_commit_count_ranked_by_new_repo_in_repo_group, args=([]), repo_url_base=repo_url_base, kwargs=({'calendar_year': calendar_year, 'repo_group': repo_group}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/lines_of_code_commit_counts_by_calendar_year_grouped Lines of Code Commit Counts by Calendar Year Grouped
    @apiName lines-of-code-commit-counts-by-calendar-year-grouped
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "net_lines_minus_whitespace": 0,
                                "added": 0,
                                "removed": 0,
                                "whitespace": 0,
                                "commits": 0,
                                "month": 1,
                                "year": 2018
                            },
                            {
                                "net_lines_minus_whitespace": -11489,
                                "added": 1046479,
                                "removed": 1051389,
                                "whitespace": 6579,
                                "commits": 4,
                                "month": 2,
                                "year": 2018
                            }
                        ]
    """
    @server.app.route('/{}/git/lines_of_code_commit_counts_by_calendar_year_grouped'.format(server.api_version))
    def lines_of_code_commit_counts_by_calendar_year_grouped():

        repo_url_base = request.args.get('repo_url_base')

        calendar_year = request.args.get('calendar_year')
        interval = request.args.get('interval')
        # repo_group = request.args.get('repo_group')

        data = server.transform(facade.lines_of_code_commit_counts_by_calendar_year_grouped, args=([]), repo_url_base=repo_url_base, kwargs=({'calendar_year': calendar_year, 'interval': interval}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped Unaffiliated Countributors Lines of Code Commit Counts by Calendar Year Grouped
    @apiName unaffiliated-contributors-lines-of-code-commit-counts-by-calendar-year-grouped
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "added": 53480,
                                "whitespace": 5141,
                                "removed": 20291,
                                "net_lines_minus_whitespace": 28048,
                                "patches": 180,
                                "month": 1,
                                "affiliation": "(Unknown)"
                            },
                            {
                                "added": 1,
                                "whitespace": 0,
                                "removed": 1,
                                "net_lines_minus_whitespace": 0,
                                "patches": 1,
                                "month": 1,
                                "affiliation": "(Academic)"
                            }
                        ]
    """
    @server.app.route('/{}/git/unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped'.format(server.api_version))
    def unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped():

        repo_url_base = request.args.get('repo_url_base')

        calendar_year = request.args.get('calendar_year')
        interval = request.args.get('interval')
        # repo_group = request.args.get('repo_group')

        data = server.transform(facade.unaffiliated_contributors_lines_of_code_commit_counts_by_calendar_year_grouped, args=([]), repo_url_base=repo_url_base, kwargs=({'calendar_year': calendar_year, 'interval': interval}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")

    """
    @api {get} /git/repo_group_lines_of_code_commit_counts_calendar_year_grouped Repo Group Lines of Code Commit Counts by Calendar Year Grouped
    @apiName repo-group-lines-of-code-commit-counts-by-calendar-year-grouped
    @apiGroup Facade (Legacy)
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "name": "pelikan",
                                "added": 127,
                                "whitespace": 39,
                                "removed": 17,
                                "net_lines_minus_whitespace": 71,
                                "patches": 4,
                                "month": 1
                            },
                            {
                                "name": "bijection",
                                "added": 1,
                                "whitespace": 1,
                                "removed": 0,
                                "net_lines_minus_whitespace": 0,
                                "patches": 2,
                                "month": 1
                            }
                        ]
    """
    @server.app.route('/{}/git/repo_group_lines_of_code_commit_counts_calendar_year_grouped'.format(server.api_version))

    # @server.app.route('/{}/git/<calendar_year>/<interval>/<repo_group>/loc_commits'.format(server.api_version))
    def repo_group_lines_of_code_commit_counts_calendar_year_grouped():

        repo_url_base = request.args.get('repo_url_base')

        calendar_year = request.args.get('calendar_year')
        interval = request.args.get('interval')
        repo_group = request.args.get('repo_group')

        data = server.transform(facade.repo_group_lines_of_code_commit_counts_calendar_year_grouped, args=([]), repo_url_base=repo_url_base, kwargs=({'calendar_year': calendar_year, 'interval': interval, 'repo_group': repo_group}))

        return Response(response=data,
                       status=200,
                       mimetype="application/json")
