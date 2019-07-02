#SPDX-License-Identifier: MIT
"""
Creates routes for the Augur database data source plugin
"""

from flask import request, Response

def create_routes(server):

    augur_db = server._augur['augur_db']()

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
        drs = server.transform(augur_db.repo_groups)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=augur_db.repo_groups, endpoint='/{}/repo-groups'.format(server.api_version), metric_type='git')

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
        drs = server.transform(augur_db.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")

    server.updateMetricMetadata(function=augur_db.downloaded_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    """
    @api {get} /repos/:owner/:repo Get Repo
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
    @server.app.route('/{}/repos/<owner>/<repo>'.format(server.api_version))
    def get_repo(owner, repo):
        a = [owner, repo]
        gre = server.transform(augur_db.get_repo, args = a)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    server.updateMetricMetadata(function=augur_db.get_repo, endpoint='/{}/repos/<owner>/<repo>'.format(server.api_version), metric_type='git')

    server.addRepoGroupMetric(augur_db.get_issues, 'get-issues')
    server.addRepoMetric(augur_db.get_issues, 'get-issues')
    #####################################
    ###           EVOLUTION           ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/code-changes Code Changes (Repo Group)
    @apiName code-changes-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2018-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "commit_count": 5140
                        },
                        {
                            "date": "2019-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "commit_count": 711
                        },
                        {
                            "date": "2015-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "commit_count": 1071
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes Code Changes (Repo)
    @apiName code-changes-repo
    @apiGroup Evolution
    @apiDescription Time series number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2018-01-01T00:00:00.000Z",
                            "commit_count": 2287
                        },
                        {
                            "date": "2018-02-01T00:00:00.000Z",
                            "commit_count": 1939
                        },
                        {
                            "date": "2018-03-01T00:00:00.000Z",
                            "commit_count": 1979
                        },
                        {
                            "date": "2018-04-01T00:00:00.000Z",
                            "commit_count": 2159
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/code-changes-lines Code Changes Lines (Repo Group)
    @apiName code-changes-lines-repo-group
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2018-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "added": 640098,
                            "removed": 694608
                        },
                        {
                            "date": "2019-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "added": 56549,
                            "removed": 48962
                        },
                        {
                            "date": "2014-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "added": 19,
                            "removed": 1
                        },
                        {
                            "date": "2015-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "added": 429535,
                            "removed": 204015
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes-lines Code Changes Lines (Repo)
    @apiName code-changes-lines-repo
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2014-01-01T00:00:00.000Z",
                            "added": 19,
                            "removed": 1
                        },
                        {
                            "date": "2015-01-01T00:00:00.000Z",
                            "added": 429535,
                            "removed": 204015
                        },
                        {
                            "date": "2016-01-01T00:00:00.000Z",
                            "added": 2739765,
                            "removed": 944568
                        },
                        {
                            "date": "2017-01-01T00:00:00.000Z",
                            "added": 3945001,
                            "removed": 1011396
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/issues-new Issues New (Repo Group)
    @apiName issues-new-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of new issues opened during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 1,
                            "issues": 3
                        },
                        {
                            "date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "issues": 1
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-new Issues New (Repo)
    @apiName issues-new-repo
    @apiGroup Evolution
    @apiDescription Time series of number of new issues opened during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2019-05-01T00:00:00.000Z",
                            "issues": 1
                        },
                        {
                            "date": "2019-06-01T00:00:00.000Z",
                            "issues": 31
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/issues-active Issues Active (Repo Group)
    @apiName issues-active-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of issues that showed some activity during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 21326,
                            "issues": 27
                        },
                        {
                            "date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 21327,
                            "issues": 54
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_active, 'issues-active')

    """
    @api {get} /repo-groups/:repo_group_id/issues-active Issues Active (Repo)
    @apiName issues-active-repo
    @apiGroup Evolution
    @apiDescription Time series of number of issues that showed some activity during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2015-07-01T00:00:00.000Z",
                            "issues": 32
                        },
                        {
                            "date": "2015-08-01T00:00:00.000Z",
                            "issues": 62
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_active, 'issues-active')

    """
    @api {get} /repo-groups/:repo_group_id/issues-closed Issues Closed (Repo Group)
    @apiName issues-closed-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of issues closed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_close_date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 21681,
                            "issues": 55
                        },
                        {
                            "issue_close_date": "2019-06-01T00:00:00.000Z",
                            "repo_id": 21681,
                            "issues": 79
                        },
                        {
                            "issue_close_date": "2013-02-01T00:00:00.000Z",
                            "repo_id": 21682,
                            "issues": 3
                        },
                        {
                            "issue_close_date": "2014-06-01T00:00:00.000Z",
                            "repo_id": 21682,
                            "issues": 10
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-closed Issues Closed (Repo)
    @apiName issues-closed-repo
    @apiGroup Evolution
    @apiDescription Time series of number of issues closed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_close_date": "2019-05-01T00:00:00.000Z",
                            "issues": 55
                        },
                        {
                            "issue_close_date": "2019-06-01T00:00:00.000Z",
                            "issues": 79
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/issue-duration Issue Duration (Repo Group)
    @apiName issue-duration-repo-group
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21682,
                            "issue_id": 41786,
                            "duration": "0 days 00:56:26.000000000"
                        },
                        {
                            "repo_id": 21682,
                            "issue_id": 41787,
                            "duration": "0 days 13:25:04.000000000"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_duration, 'issue-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-backlog Issue Duration (Repo)
    @apiName issue-duration-repo
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_id": 43893,
                            "duration": "8 days 18:53:54.000000000"
                        },
                        {
                            "issue_id": 43896,
                            "duration": "0 days 01:06:31.000000000"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_duration, 'issue-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-participants Issue Participants (Repo Group)
    @apiName issue-participants-repo-group
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "issue_id": 38803,
                            "participants": 11
                        },
                        {
                            "repo_id": 21327,
                            "issue_id": 26422,
                            "participants": 4
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_participants, 'issue-participants')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-participants Issue Participants (Repo)
    @apiName issue-participants-repo
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_id": 38829,
                            "participants": 23
                        },
                        {
                            "issue_id": 38830,
                            "participants": 8
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_participants, 'issue-participants')

    """
    @api {get} /repo-groups/:repo_group_id/issue-backlog Issue Backlog (Repo Group)
    @apiName issue-backlog-repo-group
    @apiGroup Evolution
    @apiDescription Number of issues currently open.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 1,
                            "issue_backlog": 3
                        },
                        {
                            "repo_id": 25001,
                            "issue_backlog": 32
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_backlog, 'issue-backlog')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-backlog Issue Backlog (Repo)
    @apiName issue-backlog-repo
    @apiGroup Evolution
    @apiDescription Number of issues currently open.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_backlog": 3
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_backlog, 'issue-backlog')

    """
    @api {get} /repo-groups/:repo_group_id/issue-throughput Issue Throughput (Repo Group)
    @apiName issue-throughput-repo-group
    @apiGroup Evolution
    @apiDescription Ratio of issues closed to total issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21682,
                            "throughput": 0.783692
                        },
                        {
                            "repo_id": 21681,
                            "throughput": 0.301124
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_throughput, 'issue-throughput')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-throughput Issue Throughput (Repo)
    @apiName issue-throughput-repo
    @apiGroup Evolution
    @apiDescription Ratio of issues closed to total issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "throughput": 0.301124
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_throughput, 'issue-throughput')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_group_route(repo_group_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'period': period,
    #               'begin_date': begin_date, 'end_date': end_date}

    #     data = server.transform(augur_db.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/repo/<repo_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_route(repo_group_id, repo_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'repo_id': repo_id,
    #               'period': period, 'begin_date': begin_date,
    #               'end_date': end_date}

    #     data = server.transform(augur_db.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    """
    @api {get} /repo-groups/:repo_group_id/pull-requests-merge-contributor-new New Contributors of Commits (Repo Group)
    @apiName New Contributors of Commits(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "count": 5140
                        },
                        {
                            "commit_date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 711
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/pull-requests-merge-contributor-new New Contributors of Commits (Repo)
    @apiName New Contributors of Commits(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "count": 2287
                        },
                        {
                            "commit_date": "2018-02-01T00:00:00.000Z",
                            "count": 1939
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repo-groups/:repo_group_id/issues-first-time-opened New Contributors of Issues (Repo Group)
    @apiName New Contributors of Issues(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_first_time_opened, 'issues-first-time-opened')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-opened New Contributors of Issues (Repo)
    @apiName New Contributors of Issues(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_first_time_opened, 'issues-first-time-opened')

    """
    @api {get} /repo-groups/:repo_group_id/issues-first-time-closed Closed Issues New Contributor (Repo Group)
    @apiName Closed Issues New Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons closing an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_first_time_closed, 'issues-first-time-closed')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-closed Closed Issues New Contributors (Repo)
    @apiName Closed Issues New Contributors(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons closing an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_first_time_closed, 'issues-first-time-closed')

    """
    @api {get} /repo-groups/:repo_group_id/sub-projects Sub-Projects (Repo Group)
    @apiName Sub-Projects(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.sub_projects, 'sub-projects')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/sub-projects Sub-Projects (Repo)
    @apiName Sub-Projects(Repo)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.sub_projects, 'sub-projects')

    """
    @api {get} /repo-groups/:repo_group_id/contributors Contributors (Repo Group)
    @apiName Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription List of contributors and their contributions.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "user_id": 1,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        },
                        {
                            "user_id": 2,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.contributors, 'contributors')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/contributors Contributors (Repo)
    @apiName Contributors(Repo)
    @apiGroup Evolution
    @apiDescription List of contributors and their contributions.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                       {
                            "user": 1,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        },
                        {
                            "user": 2,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.contributors, 'contributors')

    """
    @api {get} /repo-groups/:repo_group_id/contributors-new New Contributors (Repo Group)
    @apiName New Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription Time series of number of new contributors during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "contribute_at": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "contribute_at": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.contributors_new, 'contributors-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/contributors-new New Contributors (Repo)
    @apiName New Contributors(Repo)
    @apiGroup Evolution
    @apiDescription Time series of number of new contributors during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "contribute_at": "2018-05-20T00:00:00.000Z",
                            "count": 3
                        },
                        {
                            "contribute_at": "2019-06-03T00:00:00.000Z",
                            "count": 23
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.contributors_new, 'contributors-new')

    """
    @api {get} /repo-groups/:repo_group_id/open-issues-count Open Issues Count (Repo Group)
    @apiName open-issues-count-repo-group
    @apiGroup Evolution
    @apiDescription Count of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "rg_name": "Netflix",
                            "open_count": 1,
                            "date": "2017-09-11T00:00:00.000Z"
                        },
                        {
                            "rg_name": "Netflix",
                            "open_count": 4,
                            "date": "2019-06-10T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.open_issues_count, 'open-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/open-issues-count Open Issues Count (Repo)
    @apiName open-issues-count-repo
    @apiGroup Evolution
    @apiDescription Count of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "open_count": 18,
                            "date": "2019-04-15T00:00:00.000Z"
                        },
                        {
                            "repo_id": 21681,
                            "open_count": 16,
                            "date": "2019-04-22T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.open_issues_count, 'open-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/closed-issues-count Closed Issues Count (Repo Group)
    @apiName closed-issues-count-repo-group
    @apiGroup Evolution
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "rg_name": "Apache",
                            "closed_count": 4,
                            "date": "2014-06-02T00:00:00.000Z"
                        },
                        {
                            "rg_name": "Apache",
                            "closed_count": 6,
                            "date": "2014-06-09T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.closed_issues_count, 'closed-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/closed-issues-count Closed Issues Count (Repo)
    @apiName closed-issues-count-repo
    @apiGroup Evolution
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "closed_count": 26,
                            "date": "2018-11-26T00:00:00.000Z"
                        },
                        {
                            "repo_id": 21681,
                            "closed_count": 14,
                            "date": "2018-12-03T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.closed_issues_count, 'closed-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/issues-open-age Open Issue Age (Repo Group)
    @apiName Open Issue Age(Repo Group)
    @apiGroup Evolution
    @apiDescription Age of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_open_age, 'issues-open-age')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-open-age Open Issue Age (Repo)
    @apiName Open Issue Age(Repo)
    @apiGroup Evolution
    @apiDescription Age of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_open_age, 'issues-open-age')

    """
    @api {get} /repo-groups/:repo_group_id/issues-closed-resolution-duration Closed Issue Resolution Duration (Repo Group)
    @apiName Closed Issue Resolution Duration(Repo Group)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4110,
                            "issue_title":"rm incubating word",
                            "created_at":"2019-05-22T03:18:13.000Z",
                            "closed_at":"2019-05-22T05:27:29.000Z",
                            "diffdate":0.0
                        },
                        {
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4111,
                            "issue_title":"nacos registry serviceName may conflict",
                            "created_at":"2019-05-22T03:30:23.000Z",
                            "closed_at":"2019-05-23T14:36:17.000Z",
                            "diffdate":1.0
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-closed-resolution-duration Closed Issue Resolution Duration (Repo)
    @apiName Closed Issue Resolution Duration(Repo)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "gh_issue_number":4223,
                            "issue_title":"Cloud Native PR",
                            "created_at":"2019-05-31T07:55:44.000Z",
                            "closed_at":"2019-06-17T03:12:48.000Z",
                            "diffdate":16.0
                        },
                        {
                            "gh_issue_number":4131,
                            "issue_title":"Reduce context switching cost by optimizing thread model on consumer side.",
                            "created_at":"2019-05-23T06:18:21.000Z",
                            "closed_at":"2019-06-03T08:07:27.000Z",
                            "diffdate":11.0
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_closed_resolution_duration, 'issues-closed-resolution-duration')


    #####################################
    ###              RISK             ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/cii-best-practices-badge CII Best Practices Badge (Repo Group)
    @apiName cii-best-practices-badge-repo-group
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21277,
                            "badge_level": "passing"
                        },
                        {
                            "repo_id": 21252,
                            "badge_level": "in_progress"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repo-groups/:repo_group_id/cii-best-practices-badge CII Best Practices Badge (Repo)
    @apiName cii-best-practices-badge-repo
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "badge_level": "gold"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo Group)
    @apiName languages-repo-group
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21277,
                            "primary_language": "Go"
                        },
                        {
                            "repo_id": 21252,
                            "primary_language": "PHP"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo)
    @apiName languages-repo
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "primary_language":"PHP"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/license-declared License Declared (Repo Group)
    @apiName license-declared-repo-group
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21277,
                            "license": "Apache-2.0"
                        },
                        {
                            "repo_id": 21252,
                            "license": "Apache-2.0"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.license_declared, 'license-declared')

    """
    @api {get} /repo-groups/:repo_group_id/license-declared License Declared (Repo)
    @apiName license-declared-repo
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "license": "Apache-2.0"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.license_declared, 'license-declared')

    #####################################
    ###         EXPERIMENTAL          ###
    ##################################### 

    """
    @api {get} /repo-groups/:repo_group_id/lines-changed-by-author Lines Changed by Author(Repo)
    @apiNames lines-changed-by-author
    @apiGroup Experimental
    @apiDescription Returns number of lines changed per author per day 
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-24",
                            "affiliation": "NULL",
                            "additions": 25611,
                            "deletions": 296,
                            "whitespace": 5279
                        },
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-25",
                            "affiliation": "NULL",
                            "additions": 163,
                            "deletions": 179,
                            "whitespace": 46
                        }
                    ]
    """
    server.addRepoMetric(augur_db.lines_changed_by_author,'lines-changed-by-author')

    """
    @api {get} /repo-groups/:repo_group_id/lines-changed-by-author Lines Changed by Author(Repo)
    @apiNames lines-changed-by-author
    @apiGroup Experimental
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-24",
                            "affiliation": "NULL",
                            "additions": 25611,
                            "deletions": 296,
                            "whitespace": 5279
                        },
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-25",
                            "affiliation": "NULL",
                            "additions": 163,
                            "deletions": 179,
                            "whitespace": 46
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.lines_changed_by_author,'lines-changed-by-author')

    
    """
    @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-new-repo-in-repo-group Annual Commit Count Ranked by New Repo in Repo Group
    @apiName annual-commit-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experiment
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
    server.addRepoGroupMetric(augur_db.annual_commit_count_ranked_by_new_repo_in_repo_group,'annual-commit-count-ranked-by-new-repo-in-repo-group')