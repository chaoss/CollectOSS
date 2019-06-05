#SPDX-License-Identifier: MIT
"""
Creates routes for the Augur database data source plugin
"""

from flask import request, Response

def create_routes(server):

    augur_db = server._augur['augur_db']()

    @server.app.route('/{}/repo-groups'.format(server.api_version))
    def get_repo_groups(): #TODO: make this name automatic - wrapper?
        drs = server.transform(augur_db.repo_groups)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=augur_db.repo_groups, endpoint='/{}/repo-groups'.format(server.api_version), metric_type='git')

    @server.app.route('/{}/repos'.format(server.api_version))
    def downloaded_repos():
        drs = server.transform(augur_db.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=augur_db.downloaded_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    #####################################
    ###           EVOLUTION           ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/code-changes
    @apiName Code Changes
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "commit_count": 5140
                        },
                        {
                            "commit_date": "2019-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "commit_count": 711
                        },
                        {
                            "commit_date": "2015-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "commit_count": 1071
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes
    @apiName Code Changes
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "commit_count": 2287
                        },
                        {
                            "commit_date": "2018-02-01T00:00:00.000Z",
                            "commit_count": 1939
                        },
                        {
                            "commit_date": "2018-03-01T00:00:00.000Z",
                            "commit_count": 1979
                        },
                        {
                            "commit_date": "2018-04-01T00:00:00.000Z",
                            "commit_count": 2159
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/code-changes-lines Code Changes Lines
    @apiName code-changes-lines
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "added": 640098,
                            "removed": 694608
                        },
                        {
                            "commit_date": "2019-01-01T00:00:00.000Z",
                            "repo_id": 1,
                            "added": 56549,
                            "removed": 48962
                        },
                        {
                            "commit_date": "2014-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "added": 19,
                            "removed": 1
                        },
                        {
                            "commit_date": "2015-01-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "added": 429535,
                            "removed": 204015
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes-lines Code Changes Lines
    @apiName code-changes-lines
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2014-01-01T00:00:00.000Z",
                            "added": 19,
                            "removed": 1
                        },
                        {
                            "commit_date": "2015-01-01T00:00:00.000Z",
                            "added": 429535,
                            "removed": 204015
                        },
                        {
                            "commit_date": "2016-01-01T00:00:00.000Z",
                            "added": 2739765,
                            "removed": 944568
                        },
                        {
                            "commit_date": "2017-01-01T00:00:00.000Z",
                            "added": 3945001,
                            "removed": 1011396
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/issues-new Issues New
    @apiName issues-new
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 1,
                            "issues": 3
                        },
                        {
                            "issue_date": "2019-05-01T00:00:00.000Z",
                            "repo_id": 25001,
                            "issues": 1
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-new Issues New
    @apiName issues-new
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2019-05-01T00:00:00.000Z",
                            "issues": 1
                        },
                        {
                            "issue_date": "2019-06-01T00:00:00.000Z",
                            "issues": 31
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/issues-closed Issues Closed
    @apiName issues-closed
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Closed.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    TODO
    """
    server.addRepoGroupMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-closed Issues Closed
    @apiName issues-closed
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
    @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.

    @apiSuccessExample {json} Success-Response:
                    TODO
    """
    server.addRepoMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/issue-backlog Issue Backlog
    @apiName issue-backlog
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID

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
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-backlog Issue Backlog
    @apiName issue-backlog
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>

    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_backlog": 3
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_backlog, 'issue-backlog')

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