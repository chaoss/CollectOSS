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

    """
    @api {get} /repo-groups/:repo_group_id/pull-requests-merge-contributor-new
    @apiName New Contributors of Commits
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} [period="day"] Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} [begin_date="1970-1-1 0:0:1"] Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:1'
    @apiParam {string} [end_date] Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
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
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/pull-requests-merge-contributor-new
    @apiName New Contributors of Commits
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} [period="day"] Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} [begin_date="1970-1-1 0:0:1"] Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:1'
    @apiParam {string} [end_date] Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
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
    @api {get} /repo-groups/:repo_group_id/issues-first-time-opened
    @apiName New Contributors of Issues
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {String} repo_group_id Repository Group ID
    @apiParam {string} [period="day"] Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} [begin_date="1970-1-1 0:0:1"] Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:1'
    @apiParam {string} [end_date] Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
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
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-opened
    @apiName New Contributors of Issues
    @apiGroup Evolution
    @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {String} repo_group_id Repository Group ID.
    @apiParma {String} repo_id Repository ID.
    @apiParam {string} [period="day"] Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
    @apiParam {string} [begin_date="1970-1-1 0:0:1"] Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:1'
    @apiParam {string} [end_date] Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
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