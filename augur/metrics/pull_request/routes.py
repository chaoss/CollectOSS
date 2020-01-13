#SPDX-License-Identifier: MIT

def create_pull_request_routes(server):

    metrics = server._augur.metrics

    """
    @api {get} /repo-groups/:repo_group_id/reviews Reviews (Repo Group)
    @apiName reviews-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of new reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/reviews.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21035,
                            "repo_name": "prototype-ujs",
                            "date": "2010-01-01T00:00:00.000Z",
                            "pull_requests": 1
                        },
                        {
                            "repo_id": 21035,
                            "repo_name": "prototype-ujs",
                            "date": "2011-01-01T00:00:00.000Z",
                            "pull_requests": 5
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2011-01-01T00:00:00.000Z",
                            "pull_requests": 16
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2012-01-01T00:00:00.000Z",
                            "pull_requests": 14
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.reviews, 'reviews')

    """
    @api {get} /repos/:repo_id/reviews Reviews (Repo)
    @apiName reviews-repo
    @apiGroup Evolution
    @apiDescription Time series of number of new reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/reviews.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-spec",
                            "date": "2016-01-01T00:00:00.000Z",
                            "pull_requests": 37
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2017-01-01T00:00:00.000Z",
                            "pull_requests": 49
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2018-01-01T00:00:00.000Z",
                            "pull_requests": 63
                        }
                    ]
    """
    server.addRepoMetric(metrics.reviews, 'reviews')

    """
    @api {get} /repo-groups/:repo_group_id/reviews-accepted Reviews Accepted (Repo Group)
    @apiName reviews-accepted-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of accepted reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Accepted.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21035,
                            "repo_name": "prototype-ujs",
                            "date": "2010-01-01T00:00:00.000Z",
                            "pull_requests": 1
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2011-01-01T00:00:00.000Z",
                            "pull_requests": 4
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2012-01-01T00:00:00.000Z",
                            "pull_requests": 4
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.reviews_accepted, 'reviews-accepted')

    """
    @api {get} /repos/:repo_id/reviews-accepted Reviews Accepted (Repo)
    @apiName reviews-accepted-repo
    @apiGroup Evolution
    @apiDescription Time series of number of accepted reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Accepted.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-spec",
                            "date": "2016-01-01T00:00:00.000Z",
                            "pull_requests": 30
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2017-01-01T00:00:00.000Z",
                            "pull_requests": 37
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2018-01-01T00:00:00.000Z",
                            "pull_requests": 46
                        }
                    ]
    """
    server.addRepoMetric(metrics.reviews_accepted, 'reviews-accepted')

    """
    @api {get} /repo-groups/:repo_group_id/reviews-declined Reviews Declined (Repo Group)
    @apiName reviews-declined-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of declined reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Accepted.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21035,
                            "repo_name": "prototype-ujs",
                            "date": "2010-01-01T00:00:00.000Z",
                            "pull_requests": 1
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2011-01-01T00:00:00.000Z",
                            "pull_requests": 3
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "date": "2012-01-01T00:00:00.000Z",
                            "pull_requests": 6
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.reviews_declined, 'reviews-declined')

    """
    @api {get} /repos/:repo_id/reviews-declined Reviews Declined (Repo)
    @apiName reviews-declined-repo
    @apiGroup Evolution
    @apiDescription Time series of number of declined reviews / pull requests opened within a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Accepted.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-spec",
                            "date": "2016-01-01T00:00:00.000Z",
                            "pull_requests": 11
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2017-01-01T00:00:00.000Z",
                            "pull_requests": 16
                        },
                        {
                            "repo_name": "graphql-spec",
                            "date": "2018-01-01T00:00:00.000Z",
                            "pull_requests": 4
                        }
                    ]
    """
    server.addRepoMetric(metrics.reviews_declined, 'reviews-declined')

    """
    @api {get} /repo-groups/:repo_group_id/review-duration Review Duration (Repo Group)
    @apiName review-duration-repo-group
    @apiGroup Evolution
    @apiDescription Time since an review/pull request is proposed until it is accepted.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21035,
                            "repo_name": "prototype-ujs",
                            "pull_request_id": 25386,
                            "created_at": "2010-09-28T19:07:15.000Z",
                            "merged_at": "2010-09-29T17:46:59.000Z",
                            "duration": "0 days 22:39:44.000000000"
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "pull_request_id": 25392,
                            "created_at": "2011-05-18T14:11:23.000Z",
                            "merged_at": "2011-05-18T19:03:01.000Z",
                            "duration": "0 days 04:51:38.000000000"
                        },
                        {
                            "repo_id": 21042,
                            "repo_name": "pjax_rails",
                            "pull_request_id": 25396,
                            "created_at": "2011-05-25T10:09:01.000Z",
                            "merged_at": "2011-05-25T19:30:01.000Z",
                            "duration": "0 days 09:21:00.000000000"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.review_duration, 'review-duration')

    """
    @api {get} /repos/:repo_id/review-duration review Duration (Repo)
    @apiName review-duration-repo
    @apiGroup Evolution
    @apiDescription Time since an review/pull request is proposed until it is accepted.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Reviews_Duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-spec",
                            "pull_request_id": 25374,
                            "created_at": "2019-01-02T11:02:08.000Z",
                            "merged_at": "2019-07-05T09:10:45.000Z",
                            "duration": "183 days 22:08:37.000000000"
                        },
                        {
                            "repo_name": "graphql-spec",
                            "pull_request_id": 25378,
                            "created_at": "2019-03-28T13:44:04.000Z",
                            "merged_at": "2019-07-03T23:10:36.000Z",
                            "duration": "97 days 09:26:32.000000000"
                        }
                    ]
    """
    server.addRepoMetric(metrics.review_duration, 'review-duration')

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
                            "count": 5140,
                            "repo_name": "rails"
                        },
                        {
                            "commit_date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 711,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoGroupMetric(
        metrics.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repos/:repo_id/pull-requests-merge-contributor-new New Contributors of Commits (Repo)
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
                            "count": 2287,
                            "repo_name": "rails"
                        },
                        {
                            "commit_date": "2018-02-01T00:00:00.000Z",
                            "count": 1939,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        metrics.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repo-groups/:repo_group_id/pull-request-acceptance-rate Pull Request Acceptance Rate (Repo Group)
    @apiName pull-request-acceptance-rate-repo-group
    @apiGroup Experimental
    @apiDescription Timeseries of pull request acceptance rate (expressed as the ratio of pull requests merged on a date to the count of pull requests opened on a date)
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [group_by="week"] Allows for results to be grouped by day, week, month, or year. E.g. values: `year`, `day`, `month`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2019-02-11T00:00:00.000Z",
                            "rate": 120.5
                        },
                        {
                            "date": "2019-02-18T00:00:00.000Z",
                            "rate": 34
                        },
                        {
                            "date": "2019-02-25T00:00:00.000Z",
                            "rate": 38.6666666667
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.pull_request_acceptance_rate, 'pull-request-acceptance-rate')

    """
    @api {get} /repos/:repo_id/pull-request-acceptance-rate Pull Request Acceptance Rate (Repo)
    @apiName pull-request-acceptance-rate-repo
    @apiGroup Experimental
    @apiDescription Timeseries of pull request acceptance rate (expressed as the ratio of pull requests merged on a date to the count of pull requests opened on a date)
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2019-01-01T00:00:00.000Z",
                            "rate": 5.3333333333
                        }
                    ]
    """
    server.addRepoMetric(metrics.pull_request_acceptance_rate, 'pull-request-acceptance-rate')
