#SPDX-License-Identifier: MIT

def create_contributor_routes(server):

    metrics = server._augur.metrics

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
                            "total": 2,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "user_id": 2,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.contributors, 'contributors')

    """
    @api {get} /repos/:repo_id/contributors Contributors (Repo)
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
    server.addRepoMetric(metrics.contributors, 'contributors')

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
                            "date": "2018-05-20T00:00:00.000Z",
                            "new_contributors": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "date": "2019-06-03T00:00:00.000Z",
                            "new_contributors": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.contributors_new, 'contributors-new')

    """
    @api {get} /repos/:repo_id/contributors-new New Contributors (Repo)
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
                            "date": "2018-05-20T00:00:00.000Z",
                            "new_contributors": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "date": "2019-06-03T00:00:00.000Z",
                            "new_contributors": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoMetric(metrics.contributors_new, 'contributors-new')

    """
    @api {get} /repos/:repo_id/committers Committers(Repo)
    @apiName committers-repo
    @apiGroup Risk
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/Committers.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="week"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date":"2018-10-25T00:00:00.000Z",
                            "repo_name":"weasel",
                            "rg_name":"Comcast",
                            "count":1
                        },
                        {
                            "date":"2018-10-17T00:00:00.000Z","repo_name":"weasel","rg_name":"Comcast","count":11
                        },
                        {
                            "date":"2018-06-21T00:00:00.000Z",
                            "repo_name":"weasel",
                            "rg_name":"Comcast",
                            "count":6
                        }
                    ]
    """
    server.addRepoMetric(metrics.committers, 'committers')

    """
    @api {get} /repo-groups/:repo_group_id/Committers (Repo Group)
    @apiName committers-repo-group
    @apiGroup Risk
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/metrics/Committers.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="week"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2007-01-01T00:00:00.000Z",
                            "rg_name": "Comcast",
                            "count": 372
                        },
                        {
                            "date": "2008-01-01T00:00:00.000Z",
                            "rg_name": "Comcast",
                            "count": 964
                        },
                        {
                            "date": "2009-01-01T00:00:00.000Z",
                            "rg_name": "Comcast",
                            "count": 28038
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.committers, 'committers')

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
    server.addRepoMetric(metrics.lines_changed_by_author,'lines-changed-by-author')

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
    server.addRepoGroupMetric(metrics.lines_changed_by_author,'lines-changed-by-author')

    """
    @api {get} /repo-groups/:repo_group_id/top-committers Top Committers (Repo Group)
    @apiName top-committers-repo-group
    @apiGroup Experimental
    @apiDescription Returns a list of contributors contributing N% of all commits.
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [year] Specify the year to return the results for. Default value: `current year`
    @apiParam {string} [threshold=0.5] Specify N%. Accepts a value between `0` & `1` where `0` specifies
                                        `0%` and `1` specifies `100%`.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "repo_group_name": "Rails",
                            "email": "kamipo@gmail.com",
                            "commits": 502
                        },
                        {
                            "repo_group_id": 20,
                            "repo_group_name": "Rails",
                            "email": "rafaelmfranca@gmail.com",
                            "commits": 246
                        },
                        {
                            "repo_group_id": 20,
                            "repo_group_name": "Rails",
                            "email": "kaspth@gmail.com",
                            "commits": 119
                        },
                        {
                            "repo_group_id": "20",
                            "repo_group_name": "Rails",
                            "email": "other_contributors",
                            "commits": 1774
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.top_committers, 'top-committers')

    """
    @api {get} /repos/:repo_id/top-committers Top Committers (Repo)
    @apiName top-committers-repo
    @apiGroup Experimental
    @apiDescription Returns a list of contributors contributing N% of all commits.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [year] Specify the year to return the results for. Default value: `current year`
    @apiParam {string} [threshold=0.5] Specify N%. Accepts a value between `0` & `1` where `0` specifies
                                        `0%` and `1` specifies `100%`.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21334,
                            "repo_name": "graphql",
                            "email": "caniszczyk@gmail.com",
                            "commits": 4
                        },
                        {
                            "repo_id": 21334,
                            "repo_name": "graphql",
                            "email": "richard.j.schulte@gmail.com",
                            "commits": 3
                        },
                        {
                            "repo_id": "21334",
                            "repo_name": "graphql",
                            "email": "other_contributors",
                            "commits": 5
                        }
                    ]
    """
    server.addRepoMetric(metrics.top_committers, 'top-committers')

    server.addRepoGroupMetric(metrics.contributors_code_development, 'contributors-code-development')

    server.addRepoMetric(metrics.contributors_code_development, 'contributors-code-development')