#SPDX-License-Identifier: MIT
"""
Creates routes for the GHTorrent data source plugin
"""

from flask import request, Response

def create_routes(server):  

    ghtorrent = server._augur['ghtorrent']()

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################

    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    """
    @api {get} /:owner/:repo/timeseries/issues/closed Closed Issues
    @apiName closed-issues
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issues-closed.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository
    @apiParam {string} group_by (default to week) allows for results to be grouped by day, week, month, or year

    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "date": "2011-03-19T00:00:00.000Z",
                            "issues_closed": 3
                        },
                        {
                            "date": "2011-03-25T00:00:00.000Z",
                            "issues_closed": 6
                        }
                    ]
    """
    server.addTimeseries(ghtorrent.closed_issues, 'issues/closed')

    """
    @api {get} /:owner/:repo/timeseries/commits?group_by=:group_by Code Commits
    @apiName code-commits
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="com/chaoss/metrics/blob/master/activity-metrics/code-commits.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository
    @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2017-08-27T00:00:00.000Z",
                                "commits": 44
                            },
                            {
                                "date": "2017-08-20T00:00:00.000Z",
                                "commits": 98
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.code_commits, 'commits')

    """
    @api {get} /:owner/:repo/timeseries/code_review_iteration Code Review Iteration
    @apiName code-review-iteration
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2012-05-16T00:00:00.000Z",
                                "iterations": 2
                            },
                            {
                                "date": "2012-05-16T00:00:00.000Z",
                                "iterations": 1
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.code_review_iteration, 'code_review_iteration')

    """
    @api {get} /:owner/:repo/timeseries/contribution_acceptance Contribution Acceptance
    @apiName contribution-acceptance
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://www.github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2012-05-16T00:00:00.000Z",
                                "ratio": 1.1579
                            },
                            {
                                "date": "2012-05-20T00:00:00.000Z",
                                "ratio": 1.3929
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.contribution_acceptance, 'contribution_acceptance')

    """
    @api {get} /:owner/:repo/contributing_github_organizations Contributing Github Organizations
    @apiName contributing-github-organizations
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "contributing_org": 4066,
                                "commits": 36069,
                                "issues": 432,
                                "commit_comments": 1597,
                                "issue_comments": 15421,
                                "pull_requests": 808,
                                "pull_request_comments": 0,
                                "total": 54327,
                                "count": 35
                            },
                            {
                                "contributing_org": 16465,
                                "commits": 39111,
                                "issues": 332,
                                "commit_comments": 524,
                                "issue_comments": 3188,
                                "pull_requests": 57,
                                "pull_request_comments": 18,
                                "total": 43230,
                                "count": 11
                            }
                        ]
    """
    server.addMetric(ghtorrent.contributing_github_organizations, 'contributing_github_organizations')

    """
    @api {get} /:owner/:repo/timeseries/issues/response_time First Response To Issue Duration
    @apiName first-response-to-issue-duration
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "id": 2,
                                "opened": "2012-01-19T05:24:55.000Z",
                                "first_commented": "2012-01-19T05:30:13.000Z",
                                "pull_request": 0,
                                "minutes_to_comment": 5
                            },
                            {
                                "id": 3,
                                "opened": "2012-01-26T15:07:56.000Z",
                                "first_commented": "2012-01-26T15:09:28.000Z",
                                "pull_request": 0,
                                "minutes_to_comment": 1
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.first_response_to_issue_duration, 'issues/response_time')

    """
    @api {get} /:owner/:repo/timeseries/forks?group_by=:group_by Forks
    @apiName forks
    @apiGroup Growth-Maturity-Decline
    @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2017-08-20T00:00:00.000Z",
                                "projects": 48
                            },
                            {
                                "date": "2017-08-13T00:00:00.000Z",
                                "projects": 53
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.forks, 'forks')

    """
    @api {get} /:owner/:repo/timeseries/pulls/maintainer_response_time Maintainer Response to Merge Request Duration
    @apiName maintainer-response-to-merge-request-duration
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/augurlabs/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2011-05-10T00:00:00.000Z",
                                "days": 32
                            },
                            {
                                "date": "2011-05-21T00:00:00.000Z",
                                "days": 3
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.maintainer_response_to_merge_request_duration, 'pulls/maintainer_response_time')

    """
    @api {get} /:owner/:repo/timeseries/pulls/new_contributing_github_organizations New Contributing Github Organizations
    @apiName new-github-contributing-organizations
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/augurlabs/metrics/blob/master/activity-metrics/new-contributing-organizations.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2008-04-12T23:43:38.000Z",
                                "organizations": 1
                            },
                            {
                                "date": "2008-08-23T15:05:52.000Z",
                                "organizations": 2
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.new_contributing_github_organizations, 'new_contributing_github_organizations')

    """
    @api {get} /:owner/:repo/timeseries/issues Open Issues
    @apiName open-issues
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/open-issues.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {string} group_by (default to week) allows for results to be grouped by day, week, month, or year
    @apiParam {string} owner username of the owner of the github repository
    @apiParam {string} repo name of the github repository

    @apiSucessExample {json} success-response:
                        [
                            {
                                "date": "2017-08-27T00:00:00.000Z",
                                "issues": 67
                            },
                            {
                                "date": "2017-08-20T00:00:00.000Z",
                                "issues": 100
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.open_issues, 'issues')

    """
    @api {get} /:owner/:repo/timeseries/pulls/comments?group_by=:group_by Pull Request Comments
    @apiName pull-request-comments
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-request-comments.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2011-11-15T00:00:00.000Z",
                                "counter": 3
                            },
                            {
                                "date": "2011-11-25T00:00:00.000Z",
                                "counter": 1
                            }
                        ]

    """
    server.addTimeseries(ghtorrent.pull_request_comments, 'pulls/comments')

    """
    @api {get} /:owner/:repo/timeseries/pulls Pull Requests Open
    @apiName pull-requests-open
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-open.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2013-01-09T00:00:00.000Z",
                                "pull_requests": 3
                            },
                            {
                                "date": "2016-01-14T00:00:00.000Z",
                                "pull_requests": 1
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.pull_requests_open, 'pulls')

    #####################################
    ###            RISK               ###
    #####################################

    #####################################
    ###            VALUE              ###
    #####################################

    #####################################
    ###           ACTIVITY            ###
    #####################################

    """
    @api {get} /:owner/:repo/timeseries/issue_comments Issue Comments
    @apiName issue-comments
    @apiGroup Activity
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-comments.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2009-04-05T00:00:00.000Z",
                                "counter": 3
                            },
                            {
                                "date": "2009-04-16T00:00:00.000Z",
                                "counter": 5
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.issue_comments, 'issue_comments')

    """
    @api {get} /:owner/:repo/timeseries/pulls/made_closed Pull Requests Made/Closed
    @apiName pull-requests-made-closed
    @apiGroup Activity
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-made-closed.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2010-09-11T00:00:00.000Z",
                                "rate": 0.3333
                            },
                            {
                                "date": "2010-09-13T00:00:00.000Z",
                                "rate": 0.3333
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.pull_requests_made_closed, 'pulls/made_closed')

    """
    @api {get} /:owner/:repo/timeseries/watchers Watchers
    @apiName watchers
    @apiGroup Activity
    @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/activity-metrics-list.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2017-08-23T00:00:00.000Z",
                                "watchers": 86
                            },
                            {
                                "date": "2017-08-16T00:00:00.000Z",
                                "watchers": 113
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.watchers, 'watchers')

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    """
    @api {get} /:owner/:repo/timeseries/commits100 Commits100
    @apiName commits100
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2017-08-13T00:00:00.000Z",
                                "commits": 114
                            },
                            {
                                "date": "2017-08-06T00:00:00.000Z",
                                "commits": 113
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.commits100, 'commits100')

    """
    @api {get} /:owner/:repo/timeseries/commits/comments Commit Comments
    @apiName commit-comments
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                                {
                                    "date": "2008-07-10T00:00:00.000Z",
                                    "counter": 2
                                },
                                {
                                    "date": "2008-07-25T00:00:00.000Z",
                                    "counter": 1
                                }
                        ]

    """
    server.addTimeseries(ghtorrent.commit_comments, 'commits/comments')

    """
    @api {get} /:owner/:repo/committer_locations Committer Locations
    @apiName committer-locations
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "login": "rafaelfranca",
                                "location": "São Paulo, Brazil",
                                "commits": 7171
                            },
                            {
                                "login": "tenderlove",
                                "location": "Seattle",
                                "commits": 4605
                            }
                        ]
    """
    server.addMetric(ghtorrent.committer_locations, 'committer_locations')

    """
    @api {get} /:owner/:repo/timeseries/total_committers Total Committers
    @apiName total-committers
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2004-11-24T00:00:00.000Z",
                                "total_total_committers": 1
                            },
                            {
                                "date": "2005-02-18T00:00:00.000Z",
                                "total_total_committers": 2
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.total_committers, 'total_committers')

    """
    @api {get} /:owner/:repo/timeseries/issues/activity Issue Activity
    @apiName issue-activity
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "0000-00-00",
                                "count": 2,
                                "action": "closed"
                            },
                            {
                                "date": "0000-00-00",
                                "count": 70,
                                "action": "opened"
                            },
                            {
                                "date": "0000-00-00",
                                "count": 0,
                                "action": "reopened"
                            },
                            {
                                "date": "0000-00-00",
                                "count": 68,
                                "action": "open"
                            },
                            {
                                "date": "2009-04-01T00:00:00.000Z",
                                "count": 0,
                                "action": "closed"
                            },
                            {
                                "date": "2009-04-01T00:00:00.000Z",
                                "count": 29,
                                "action": "opened"
                            },
                            {
                                "date": "2009-04-01T00:00:00.000Z",
                                "count": 0,
                                "action": "reopened"
                            },
                            {
                                "date": "2009-04-01T00:00:00.000Z",
                                "count": 29,
                                "action": "open"
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.issue_activity, 'issues/activity')

    """
    @api {get} /:owner/:repo/timeseries/pulls/acceptance_rate Pull Request Acceptance Rate
    @apiDeprecated This endpoint was removed. Please use (#Experimental:community-engagement)
    @apiName pull-request-acceptance-rate
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2010-09-11T00:00:00.000Z",
                                "rate": 0.3333
                            },
                            {
                                "date": "2010-09-13T00:00:00.000Z",
                                "rate": 0.3333
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.pull_request_acceptance_rate, 'pulls/acceptance_rate')

    """
    @api {get} /:owner/:repo/community_age Community Age
    @apiName community-age
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "login": "bonnie",
                                "location": "Rowena, TX",
                                "commits": 12
                            },
                            {
                                "login":"clyde",
                                "location":"Ellis County, TX",
                                "commits": 12
                            }
                        ]
    """
    server.addMetric(ghtorrent.community_age, 'community_age')

    """
    @api {get} /:owner/:repo/timeseries/community_engagement Community Engagement
    @apiName community-engagement
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2011-04-16T00:00:00.000Z",
                                "issues_opened": 0,
                                "issues_closed": 0,
                                "pull_requests_opened": 32,
                                "pull_requests_merged": 0,
                                "pull_requests_closed": 19,
                                "issues_opened_total": 4,
                                "issues_closed_total": 0,
                                "issues_closed_rate_this_window": null,
                                "issues_closed_rate_total": 0,
                                "issues_delta": 0,
                                "issues_open": 4,
                                "pull_requests_opened_total": 284,
                                "pull_requests_closed_total": 242,
                                "pull_requests_closed_rate_this_window": 0.59375,
                                "pull_requests_closed_rate_total": 0.8521126761,
                                "pull_requests_delta": 13,
                                "pull_requests_open": 42
                            },
                            {
                                "date": "2011-04-17T00:00:00.000Z",
                                "issues_opened": 0,
                                "issues_closed": 0,
                                "pull_requests_opened": 15,
                                "pull_requests_merged": 1,
                                "pull_requests_closed": 14,
                                "issues_opened_total": 4,
                                "issues_closed_total": 0,
                                "issues_closed_rate_this_window": null,
                                "issues_closed_rate_total": 0,
                                "issues_delta": 0,
                                "issues_open": 4,
                                "pull_requests_opened_total": 299,
                                "pull_requests_closed_total": 256,
                                "pull_requests_closed_rate_this_window": 0.9333333333,
                                "pull_requests_closed_rate_total": 0.856187291,
                                "pull_requests_delta": 1,
                                "pull_requests_open": 43
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.community_engagement, 'community_engagement')

    """
    @api {get} /:owner/:repo/contributors Total Contributions by User
    @apiName contributors
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                       [
                            {
                                "user": 8153,
                                "commits": 6825,
                                "issues": 127,
                                "commit_comments": 313,
                                "issue_comments": 13152,
                                "pull_requests": 1,
                                "pull_request_comments": 0,
                                "total": 20418
                            },
                            {
                                "user": 45381,
                                "commits": 2192,
                                "issues": 202,
                                "commit_comments": 130,
                                "issue_comments": 4633,
                                "pull_requests": 0,
                                "pull_request_comments": 0,
                                "total": 7157
                            }
                        ]
    """
    server.addMetric(ghtorrent.contributors, 'contributors')

    """
    @api {get} /:owner/:repo/timeseries/contributions Contributions
    @apiName contributions
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository
    @apiParam (String) user Limit results to the given user's contributions

    @apiSuccessExample {json} Success-Response:
                       [
                            {
                                "date": "2004-11-24T00:00:00.000Z",
                                "commits": 3,
                                "pull_requests": null,
                                "issues": null,
                                "commit_comments": null,
                                "pull_request_comments": null,
                                "issue_comments": null,
                                "total": null
                            },
                            {
                                "date": "2004-11-30T00:00:00.000Z",
                                "commits": 7,
                                "pull_requests": null,
                                "issues": null,
                                "commit_comments": null,
                                "pull_request_comments": null,
                                "issue_comments": null,
                                "total": null
                            }
                        ]
    """
    # ghtorrent.contributons, 'contributors'
    # don't remove the above line it's for a script
    @server.app.route('/{}/<owner>/<repo>/contributions'.format(server.api_version))
    def contributions(owner, repo):
        repoid = ghtorrent.repoid(owner, repo)
        user = request.args.get('user')
        transformed_contributors = server.transform(ghtorrent.contributions, args=(owner, repo), orient=request.args.get('orient'))
        return Response(response=transformed_contributors,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(ghtorrent.contributions, '/api/unstable/<owner>/<repo>/timeseries/contributions')

    """
    @api {get} /:owner/:repo/project_age Project Age
    @apiName project-age
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                            "date": "2008-04-11T00:00:00.000Z",
                            "{0}": 1
                            }
                        ]

    """
    server.addMetric(ghtorrent.project_age, 'project_age')

    """
    @api {get} /:owner/:repo/timeseries/fakes Fakes
    @apiName fakes
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2010-04-09T00:00:00.000Z",
                                "fakes": 1
                            },
                            {
                                "date": "2010-04-27T00:00:00.000Z",
                                "fakes": 2
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.fakes, 'fakes')

    """
    @api {get} /:owner/:repo/timeseries/new_watchers New Watchers
    @apiName new_watchers
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2010-04-09T00:00:00.000Z",
                                "new_watchers": 1
                            },
                            {
                                "date": "2010-04-27T00:00:00.000Z",
                                "new_watchers": 2
                            }
                        ]
    """
    server.addTimeseries(ghtorrent.new_watchers, 'new_watchers')

    """
    @api {get} /ghtorrent_range GHTorrent Date Range
    @apiName GhtorrentRange
    @apiGroup Utility
    @apiDescription Utility endpoint to show the range of dates GHTorrent covers.

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2008-04-10T17:25:06-07:00",
                                "release": "v0.9.1"
                            },
                            {
                                "date": "2008-04-10T17:25:07-07:00",
                                "release": "v0.9.2"
                            }
                        ]
    """
    @server.app.route('/{}/ghtorrent_range'.format(server.api_version))

    def ghtorrent_range():
        ghr = server.transform(ghtorrent.ghtorrent_range())
        return Response(response=ghr,
                        status=200,
                        mimetype="application/json")
    # server.updateMetricMetadata(ghtorrent.ghtorrent_range, '/{}/ghtorrent_range'.format(server.api_version))
