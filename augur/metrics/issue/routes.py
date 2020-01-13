#SPDX-License-Identifier: MIT

def create_issue_routes(server):

    metrics = server._augur.metrics

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
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 318
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2009-01-01T00:00:00.000Z",
                            "issues": 1
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2010-01-01T00:00:00.000Z",
                            "issues": 7
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issues_new, 'issues-new')

    """
    @api {get} /repos/:repo_id/issues-new Issues New (Repo)
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
                            "repo_name": "rails",
                            "date": "2015-01-01T00:00:00.000Z",
                            "issues": 116
                        },
                        {
                            "repo_name": "rails",
                            "date": "2016-01-01T00:00:00.000Z",
                            "issues": 196
                        },
                        {
                            "repo_name": "rails",
                            "date": "2017-01-01T00:00:00.000Z",
                            "issues": 180
                        }
                    ]
    """
    server.addRepoMetric(metrics.issues_new, 'issues-new')

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
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 18
                        },
                        {
                            "repo_id": 21041,
                            "repo_name": "prototype-rails",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 20
                        },
                        {
                            "repo_id": 21043,
                            "repo_name": "sprockets-rails",
                            "date": "2015-01-01T00:00:00.000Z",
                            "issues": 102
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issues_active, 'issues-active')

    """
    @api {get} /repos/:repo_id/issues-active Issues Active (Repo)
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
                            "repo_name": "rails",
                            "date": "2011-01-01T00:00:00.000Z",
                            "issues": 30
                        },
                        {
                            "repo_name": "rails",
                            "date": "2012-01-01T00:00:00.000Z",
                            "issues": 116
                        },
                        {
                            "repo_name": "rails",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 479
                        }
                    ]
    """
    server.addRepoMetric(metrics.issues_active, 'issues-active')

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
                            "repo_id": 21681,
                            "repo_name": "incubator-zipkin",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 425
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 7
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "date": "2014-01-01T00:00:00.000Z",
                            "issues": 47
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issues_closed, 'issues-closed')

    """
    @api {get} /repos/:repo_id/issues-closed Issues Closed (Repo)
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
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2012-01-01T00:00:00.000Z",
                            "issues": 97
                        },
                        {
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 395
                        },
                        {
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2014-01-01T00:00:00.000Z",
                            "issues": 265
                        }
                    ]
    """
    server.addRepoMetric(metrics.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/issue-duration Issue Duration (Repo Group)
    @apiName issue-duration-repo-group
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21017,
                            "repo_name": "ssl_requirement",
                            "issue_id": 50320,
                            "created_at": "2011-05-06T20:20:05.000Z",
                            "closed_at": "2011-05-06T20:21:47.000Z",
                            "duration": "0 days 00:01:42.000000000"
                        },
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50328,
                            "created_at": "2019-06-20T22:56:38.000Z",
                            "closed_at": "2019-06-21T20:17:28.000Z",
                            "duration": "0 days 21:20:50.000000000"
                        },
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50329,
                            "created_at": "2019-06-20T22:01:52.000Z",
                            "closed_at": "2019-06-22T02:29:03.000Z",
                            "duration": "1 days 04:27:11.000000000"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_duration, 'issue-duration')

    """
    @api {get} /repos/:repo_id/issue-backlog Issue Duration (Repo)
    @apiName issue-duration-repo
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "exception_notification",
                            "issue_id": 50306,
                            "created_at": "2011-02-13T03:46:06.000Z",
                            "closed_at": "2011-04-14T23:27:33.000Z",
                            "duration": "60 days 19:41:27.000000000"
                        },
                        {
                            "repo_name": "exception_notification",
                            "issue_id": 50308,
                            "created_at": "2011-01-19T18:47:41.000Z",
                            "closed_at": "2013-12-09T13:51:03.000Z",
                            "duration": "1054 days 19:03:22.000000000"
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_duration, 'issue-duration')

    """
    @api {get} /repo-groups/:repo_group_id/issue-participants Issue Participants (Repo Group)
    @apiName issue-participants-repo-group
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50328,
                            "created_at": "2019-06-20T22:56:38.000Z",
                            "participants": 1
                        },
                        {
                            "repo_id": 21030,
                            "repo_name": "arel",
                            "issue_id": 50796,
                            "created_at": "2017-03-02T21:14:46.000Z",
                            "participants": 1
                        },
                        {
                            "repo_id": 21030,
                            "repo_name": "arel",
                            "issue_id": 50795,
                            "created_at": "2017-03-24T15:39:08.000Z",
                            "participants": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_participants, 'issue-participants')

    """
    @api {get} /repos/:repo_id/issue-participants Issue Participants (Repo)
    @apiName issue-participants-repo
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "arel",
                            "issue_id": 50796,
                            "created_at": "2017-03-02T21:14:46.000Z",
                            "participants": 1
                        },
                        {
                            "repo_name": "arel",
                            "issue_id": 50795,
                            "created_at": "2017-03-24T15:39:08.000Z",
                            "participants": 2
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_participants, 'issue-participants')

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
                            "repo_id": 21055,
                            "repo_name": "cache_digests",
                            "issue_backlog": 21
                        },
                        {
                            "repo_id": 21056,
                            "repo_name": "rails-dev-box",
                            "issue_backlog": 1
                        },
                        {
                            "repo_id": 21058,
                            "repo_name": "activerecord-session_store",
                            "issue_backlog": 24
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_backlog, 'issue-backlog')

    """
    @api {get} /repos/:repo_id/issue-backlog Issue Backlog (Repo)
    @apiName issue-backlog-repo
    @apiGroup Evolution
    @apiDescription Number of issues currently open.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name":"render_component",
                            "issue_backlog": 3
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_backlog, 'issue-backlog')

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
                            "repo_id": 21681,
                            "repo_name": "incubator-zipkin",
                            "throughput": 0.819125
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "throughput": 0.861896
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_throughput, 'issue-throughput')

    """
    @api {get} /repos/:repo_id/issue-throughput Issue Throughput (Repo)
    @apiName issue-throughput-repo
    @apiGroup Evolution
    @apiDescription Ratio of issues closed to total issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "rails-contributors",
                            "throughput": 0.997531
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_throughput, 'issue-throughput')

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
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        metrics.issues_first_time_opened, 'issues-first-time-opened')

    """
    @api {get} /repos/:repo_id/issues-first-time-opened New Contributors of Issues (Repo)
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
                            "count": 3,
                            "repo_name": "rails"
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.issues_first_time_opened, 'issues-first-time-opened')

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
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        metrics.issues_first_time_closed, 'issues-first-time-closed')

    """
    @api {get} /repos/:repo_id/issues-first-time-closed Closed Issues New Contributors (Repo)
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
                            "count": 3,
                            "repo_name": "rails"
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.issues_first_time_closed, 'issues-first-time-closed')

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
    server.addRepoGroupMetric(metrics.open_issues_count, 'open-issues-count')

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
    server.addRepoMetric(metrics.open_issues_count, 'open-issues-count')

    """
    @api {get} /repos/:repo_id/closed-issues-count Closed Issues Count (Repo Group)
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
    server.addRepoGroupMetric(metrics.closed_issues_count, 'closed-issues-count')

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
    server.addRepoMetric(metrics.closed_issues_count, 'closed-issues-count')

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
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38318,
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38317,
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoGroupMetric(
        metrics.issues_open_age, 'issues-open-age')

    """
    @api {get} /repos/:repo_id/issues-open-age Open Issue Age (Repo)
    @apiName Open Issue Age(Repo)
    @apiGroup Evolution
    @apiDescription Age of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38318,
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38317,
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.issues_open_age, 'issues-open-age')

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
        metrics.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    """
    @api {get} /repos/:repo_id/issues-closed-resolution-duration Closed Issue Resolution Duration (Repo)
    @apiName Closed Issue Resolution Duration(Repo)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21682
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4223,
                            "issue_title":"Cloud Native PR",
                            "created_at":"2019-05-31T07:55:44.000Z",
                            "closed_at":"2019-06-17T03:12:48.000Z",
                            "diffdate":16.0
                        },
                        {
                            "repo_id": 21682,
                             "repo_name":"incubator-dubbo",
                            "gh_issue_number":4131,
                            "issue_title":"Reduce context switching cost by optimizing thread model on consumer side.",
                            "created_at":"2019-05-23T06:18:21.000Z",
                            "closed_at":"2019-06-03T08:07:27.000Z",
                            "diffdate":11.0
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    """
    @api {get} /repo-groups/:repo_group_id/issues-maintainer-response-duration Issue Response Time (Repo Group)
    @apiName Issue Response Time(Repo Group)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-maintainer-response-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_id": 21987,
                            "repo_name": "qpid-proton",
                            "average_days_comment": 27.1111111111
                        },
                        {
                            "repo_id": 22252,
                            "repo_name": "cordova-create",
                            "average_days_comment": 0.8
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    """
    @api {get} /repos/:repo_id/issues-maintainer-response-duration Issue Response Time (Repo)
    @apiName Issue Response Time(Repo)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-maintainer-response-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_id": 21987,
                            "repo_name": "qpid-proton",
                            "average_days_comment": 27.1111111111
                        }
                    ]
    """
    server.addRepoMetric(metrics.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    """
    @api {get} /repo-groups/:repo_group_id/avgerage-issue-resolution-time Average Issue Resolution Time (Repo Group)
    @apiName average-issue-resolution-time-repo-group
    @apiGroup Risk
    @apiDescription The average issue resolution time.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21353,
                            "repo_name": "open_id_authentication",
                            "avg_issue_resolution_time": "1413 days 15:39:48"
                        },
                        {
                            "repo_id": 21362,
                            "repo_name": "country_select",
                            "avg_issue_resolution_time": "140 days 09:37:58.2"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.average_issue_resolution_time, 'average-issue-resolution-time')

    """
    @api {get} /repos/:repo_id/avgerage-issue-resolution-time Average Issue Resolution Time (Repo)
    @apiName average-issue-resolution-time-repo
    @apiGroup Risk
    @apiDescription The average issue resolution time.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "maven-release",
                            "avg_issue_resolution_time": "276 days 13:54:13.2"
                        }
                    ]
    """
    server.addRepoMetric(metrics.average_issue_resolution_time, 'average-issue-resolution-time')

    """
    @api {get} /repo-groups/:repo_group_id/issue-comments-mean Issue Comments Mean (Repo Group)
    @apiName issue-comments-mean-repo-group
    @apiGroup Experimental
    @apiDescription Mean(Average) of issue comments per day.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [group_by="week"] Allows for results to be grouped by day, week, month, or year. E.g. values: `year`, `day`, `month`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "date": "2018-01-01T00:00:00.000Z",
                            "mean":0.6191780822
                        },
                        {
                            "repo_id": 21326,
                            "date": "2019-01-01T00:00:00.000Z",
                            "mean": 0.7671232877
                        },
                        {
                            "repo_id": 21327,
                            "date": "2015-01-01T00:00:00.000Z",
                            "mean": 0.0602739726
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_comments_mean, 'issue-comments-mean')

    """
    @api {get} /repos/:repo_id/issue-comments-mean Issue Comments Mean (Repo)
    @apiName issue-comments-mean-repo
    @apiGroup Experimental
    @apiDescription Mean(Average) of issue comments per day.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "date": "2018-01-01T00:00:00.000Z",
                            "mean":0.6191780822
                        },
                        {
                            "repo_id": 21326,
                            "date": "2019-01-01T00:00:00.000Z",
                            "mean": 0.7671232877
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_comments_mean, 'issue-comments-mean')

    """
    @api {get} /repo-groups/:repo_group_id/issue-comments-mean-std Issue Comments Mean Std (Repo Group)
    @apiName issue-comments-mean-std-repo-group
    @apiGroup Experimental
    @apiDescription Mean(Average) and Standard Deviation of issue comments per day.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [group_by="week"] Allows for results to be grouped by day, week, month, or year. E.g. values: `year`, `day`, `month`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "date": "2018-01-01T00:00:00.000Z",
                            "mean":0.6191780822
                        },
                        {
                            "repo_id": 21326,
                            "date": "2019-01-01T00:00:00.000Z",
                            "mean": 0.7671232877
                        },
                        {
                            "repo_id": 21327,
                            "date": "2015-01-01T00:00:00.000Z",
                            "mean": 0.0602739726
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.issue_comments_mean_std, 'issue-comments-mean-std')

    """
    @api {get} /repos/:repo_id/issue-comments-mean-std Issue Comments Mean Std (Repo)
    @apiName issue-comments-mean-repo
    @apiGroup Experimental
    @apiDescription Mean(Average) and Standard Deviation of issue comments per day.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "date": "2011-01-01T00:00:00.000Z",
                            "average": 2.5,
                            "standard_deviation":1.7159383568
                        },
                        {
                            "repo_id": 21000,
                            "date": "2012-01-01T00:00:00.000Z",
                            "average": 1.9666666667,
                            "standard_deviation": 1.3767361036
                        }
                    ]
    """
    server.addRepoMetric(metrics.issue_comments_mean_std, 'issue-comments-mean-std')

    """
    @api {get} /repo-groups/:repo_group_id/abandoned_issues Abandoned Issues (Repo)
    @apiName Abandoned Issues
    @apiGroup Experimental
    @apiDescription List of abandoned issues (last updated >= 1 year ago)
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "updated_at": "2017-10-30T06:52:19.000Z",
                            "issue_id": 125071,
                            "repo_id": 22004
                        },
                        {
                            "updated_at": "2018-01-10T06:02:16.000Z",
                            "issue_id": 125070,
                            "repo_id": 22003
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.abandoned_issues, 'abandoned_issues')