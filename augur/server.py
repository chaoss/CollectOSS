#spdx-license-identifier: mit
import os
import sys
import json
from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
import pandas as pd
import augur
from augur.util import update_metric, metrics

sys.path.append('..')

AUGUR_API_VERSION = 'api/unstable'

'''
make a try and accept condition
if its open the GH_DATA_CONFIG_FILE and then its open in read mode
and if the file does't open the it print Couldn\'t open config file, attempting to create.
'''

class Server(object):
    def __init__(self):
        # Create Flask application
        self.app = Flask(__name__)
        app = self.app
        CORS(app)

        # Create Augur application
        self.augur_app = augur.Application()
        augur_app = self.augur_app

        # Initialize cache
        expire = int(augur_app.read_config('Server', 'cache_expire', 'AUGUR_CACHE_EXPIRE', 3600))
        self.cache = augur_app.cache.get_cache('server', expire=expire)
        self.cache.clear()

        # Initalize all of the classes
        ghtorrent = augur_app.ghtorrent()
        ghtorrentplus = augur_app.ghtorrentplus()
        publicwww = augur_app.publicwww()
        git = augur_app.git()
        github = augur_app.githubapi()
        librariesio = augur_app.librariesio()
        downloads = augur_app.downloads()
        localcsv = augur_app.localcsv()


        #####################################
        ###          API STATUS           ###
        #####################################
        @app.route('/{}/'.format(AUGUR_API_VERSION))
        def status():
            status = {
                'status': 'OK',
                'avaliable_metrics': metrics
            }
            json = self.transform(status)
            return Response(response=json,
                            status=200,
                            mimetype="application/json")


        #####################################
        ###    DIVERSITY AND INCLUSION    ###
        #####################################


        #####################################
        ### GROWTH, MATURITY, AND DECLINE ###
        #####################################

        """
        @api {get} /:owner/:repo/timeseries/issues/closed Closed Issues
        @apiName ClosedIssues 
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issues-closed.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.closed_issues, "issues/closed")

        """
        @api {get} /:owner/:repo/issue_close_time Issue Resolution Duration
        @apiName IssueResolutionDuration
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-resolution-duration.md">CHAOSS Metric Definition</a>

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "id": 2,
                                "date": "2012-01-19T05:24:55.000Z",
                                "days_to_close": 7
                            },
                            {
                                "id": 3,
                                "date": "2012-01-26T15:07:56.000Z",
                                "days_to_close": 0
                            }
                        ]
        """
        self.addMetric(ghtorrentplus.closed_issue_resolution_duration, 'issues/time_to_close')

        """
        @api {get} /:owner/:repo/timeseries/commits?group_by=:group_by Code Commits
        @apiName CodeCommits
        @apiGroup Growth-Maturity-Decline
        @apiDescription/github.<a href="com/chaoss/metrics/blob/master/activity-metrics/code-commits.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.code_commits, 'commits')

        # self.addTimeseries(github.code_reviews, 'code_reviews')

        """
        @api {get} /:owner/:repo/timeseries/code_review_iteration Code Review Iteration
        @apiName CodeReviewIteration
        @apiGroup Growth-Maturity-Decline
        @apiDescription/github.<a href="com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.code_review_iteration, 'code_review_iteration')

        """
        @api {get} /:owner/:repo/timeseries/contribution_acceptance Contribution Acceptance
        @apiName ContributionAcceptance
        @apiGroup Growth-Maturity-Decline
        @apiDescription/github.<a href="com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.contribution_acceptance, 'contribution_acceptance')

        """
        @api {get} /:owner/:repo/timeseries/contributing_github_organizations Contributing Github Organizations
        @apiName ContributingGithubOrganizations 
        @apiGroup Growth-Maturity-Decline
        @apiDescription/github.<a href="com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md">CHAOSS Metric Definition</a>

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
        self.addMetric(ghtorrent.contributing_github_organizations, 'contributing_github_organizations')

        """
        @api {get} /:owner/:repo/timeseries/issues/response_time First Response To Issue Duration
        @apiName FirstResponseToIssueDuration
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.first_response_to_issue_duration, 'issues/response_time')

        """
        @api {get} /:owner/:repo/timeseries/forks?group_by=:group_by Forks
        @apiName Forks
        @apiGroup Growth-Maturity-Decline
        @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.forks, 'forks') 

        """
        @api {get} /:owner/:repo/timeseries/lines_changed Lines of Code Changed
        @apiName LinesOfCodeChanged
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/lines-of-code-changed.md">CHAOSS Metric Definition</a>

        @apiGroup Growth-Maturity-Decline
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    'date': '2015-11-01T00:00:00Z',
                                    'lines_changed': 396137.0
                                },
                                {
                                    'date': '2015-11-08T00:00:00Z',
                                    'lines_changed': 3896.0
                                }
                            ]
        """
        self.addTimeseries(github.lines_of_code_changed, 'lines_changed')

        """
        @api {get} /:owner/:repo/pulls/maintainer_response_time Maintainer to Merge Request Duration
        @apiName MaintainerToMergeRequestDuration
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.maintainer_response_to_merge_request_duration, 'pulls/maintainer_response_time')

        """
        @api {get} /:owner/:repo/pulls/new_contributing_github_organizations New Contributing Github Organizations
        @apiName NewContributingGithubOrganizations
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/new-contributing-organizations.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.new_contributing_github_organizations, 'new_contributing_github_organizations')

        """
        @api {get} /:owner/:repo/timeseries/issues Open Issues
        @apiName OpenIssues
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/open-issues.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.open_issues, 'issues')

        """
        @api {get} /:owner/:repo/timeseries/pulls/comments?group_by=:group_by Pull Request Comments
        @apiName PullRequestComments
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-request-comments.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.pull_request_comments, 'pulls/comments')

        """
        @api {get} /:owner/:repo/timeseries/pulls Pull Requests Open
        @apiName PullRequestsOpen
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-open.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.pull_requests_open, 'pulls')


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
        @apiName IssueComments
        @apiGroup Activity
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-comments.md">CHAOSS Metric Definition</a>

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
        self.addTimeseries(ghtorrent.issue_comments, 'issue/comments')

        """
        @api {get} /:owner/:repo/watchers Watchers
        @apiName Watchers
        @apiGroup Activity
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/activity-metrics-list.md">CHAOSS Metric Definition</a>

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
        self.addMetric(ghtorrent.watchers, 'watchers')

        #####################################
        ###         EXPERIMENTAL          ###
        #####################################

        ### COMMIT RELATED ###
        """
        @api {get} /:owner/:repo/timeseries/commits100 Commits100
        @apiName Commits100
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.commits100, 'commits100')

        """
        @api {get} /:owner/:repo/timeseries/commits/comments Commit Comments
        @apiName CommitComments
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.commit_comments, 'commits/comments')

        """
        @api {get} /:owner/:repo/committer_locations Committer Locations
        @apiName CommitterLocations
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addMetric(ghtorrent.committer_locations, 'committer_locations')

        """
        @api {get} /:owner/:repo/timeseries/total_committers Total Committers
        @apiName TotalCommitters
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.total_committers, 'total_committers')

        ### ISSUE RELATED ###
        """
        @api {get} /:owner/:repo/timeseries/issues/activity Issue Activity
        @apiName IssueActivity
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.issue_activity, 'issues/activity')

        # PULL REQUEST RELATED
        """
        @api {get} /:owner/:repo/timeseries/pulls/acceptance_rate Pull Request Acceptance Rate 
        @apiName PullRequestAcceptanceRate
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.pull_request_acceptance_rate, 'pulls/acceptance_rate')

        # COMMUNITY / CONTRIBUTIONS
        """
        @api {get} /:owner/:repo/timeseries/community_age Community Age
        @apiName CommunityAge
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addMetric(ghtorrent.community_age, 'community_age')

        """
        @api {get} /:owner/:repo/timeseries/community_engagement Community Engagement
        @apiName CommunityEngagement
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addTimeseries(ghtorrent.community_engagement, 'community_engagement')

        """
        @api {get} /:owner/:repo/contributors Total Contributions by User
        @apiName TotalContributions
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addMetric(ghtorrent.contributors, 'contributors')

        """
        @api {get} /:owner/:repo/timeseries/contributions Contributions
        @apiName ContributionsByWeek
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        @app.route('/{}/<owner>/<repo>/contributions'.format(AUGUR_API_VERSION))
        def contributions(owner, repo):
            repoid = ghtorrent.repoid(owner, repo)
            user = request.args.get('user')
            contribs = ghtorrent.contributions(owner, repo)
            transformed_contributors = self.transform(contribs, orient=request.args.get('orient'))
            return Response(response=transformed_contributors,
                            status=200,
                            mimetype="application/json")

        """
        @api {get} /:owner/:repo/timeseries/project_age Project Age
        @apiName ProjectAge
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

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
        self.addMetric(ghtorrent.project_age, 'project_age')

        ### DEPENDENCY RELATED ###
        """
        @api {get} /:owner/:repo/dependencies Dependencies
        @apiName Dependencies
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                "full_name": "rails/rails",
                                "description": "Ruby on Rails",
                                "fork": false,
                                "created_at": "2008-04-11T02:19:47.000Z",
                                "updated_at": "2018-05-08T14:18:07.000Z",
                                "pushed_at": "2018-05-08T11:38:30.000Z",
                                "homepage": "http://rubyonrails.org",
                                "size": 163747,
                                "stargazers_count": 39549,
                                "language": "Ruby",
                                "has_issues": true,
                                "has_wiki": false,
                                "has_pages": false,
                                "forks_count": 16008,
                                "mirror_url": null,
                                "open_issues_count": 1079,
                                "default_branch": "master",
                                "subscribers_count": 2618,
                                "uuid": "8514",
                                "source_name": null,
                                "license": "MIT",
                                "private": false,
                                "contributions_count": 2627,
                                "has_readme": "README.md",
                                "has_changelog": null,
                                "has_contributing": "CONTRIBUTING.md",
                                "has_license": "MIT-LICENSE",
                                "has_coc": "CODE_OF_CONDUCT.md",
                                "has_threat_model": null,
                                "has_audit": null,
                                "status": null,
                                "last_synced_at": "2018-03-31T12:40:28.163Z",
                                "rank": 28,
                                "host_type": "GitHub",
                                "host_domain": null,
                                "name": null,
                                "scm": "git",
                                "fork_policy": null,
                                "github_id": "8514",
                                "pull_requests_enabled": null,
                                "logo_url": null,
                                "github_contributions_count": 2627,
                                "keywords": [
                                    "activejob",
                                    "activerecord",
                                    "framework",
                                    "html",
                                    "mvc",
                                    "rails",
                                    "ruby"
                                ],
                                "dependencies": [
                                    {
                                        "project_name": "blade-sauce_labs_plugin",
                                        "name": "blade-sauce_labs_plugin",
                                        "platform": "rubygems",
                                        "requirements": "0.7.2",
                                        "latest_stable": "0.7.3",
                                        "latest": "0.7.3",
                                        "deprecated": false,
                                        "outdated": true,
                                        "filepath": "Gemfile.lock",
                                        "kind": "runtime"
                                    },
                                    {
                                        "project_name": "blade-qunit_adapter",
                                        "name": "blade-qunit_adapter",
                                        "platform": "rubygems",
                                        "requirements": "2.0.1",
                                        "latest_stable": "2.0.1",
                                        "latest": "2.0.1",
                                        "deprecated": false,
                                        "outdated": false,
                                        "filepath": "Gemfile.lock",
                                        "kind": "runtime"
                                    }
                            ]
        """
        self.addMetric(librariesio.dependencies, 'dependencies')
        
        """
        @api {get} /:owner/:repo/dependency_stats Dependency Stats
        @apiName DependencyStats
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "dependencies": "10",
                                    "dependent_projects": "10.6K",
                                    "dependent_repositories": "392K"
                                }
                            ]
        """
        self.addMetric(librariesio.dependency_stats, 'dependency_stats')

        """
        @api {get} /:owner/:repo/dependents Dependents
        @apiName Dependents
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "name": "rspec-rails",
                                    "platform": "Rubygems",
                                    "description": "rspec-rails is a testing framework for Rails 3+.",
                                    "homepage": "https://github.com/rspec/rspec-rails",
                                    "repository_url": "https://github.com/rspec/rspec-rails",
                                    "normalized_licenses": [
                                        "MIT"
                                    ],
                                    "rank": 26,
                                    "latest_release_published_at": "2017-11-20T09:27:22.144Z",
                                    "latest_release_number": "3.7.2",
                                    "language": "Ruby",
                                    "status": null,
                                    "package_manager_url": "https://rubygems.org/gems/rspec-rails",
                                    "stars": 3666,
                                    "forks": 732,
                                    "keywords": [],
                                    "latest_stable_release": {
                                        "id": 11315605,
                                        "project_id": 245284,
                                        "number": "3.7.2",
                                        "published_at": "2017-11-20T09:27:22.144Z",
                                        "created_at": "2017-11-20T09:31:11.532Z",
                                        "updated_at": "2017-11-20T09:31:11.532Z",
                                        "runtime_dependencies_count": 7
                                    },
                                    "latest_download_url": "https://rubygems.org/downloads/rspec-rails-3.7.2.gem",
                                    "dependents_count": 4116,
                                    "dependent_repos_count": 129847,
                                    "versions": [
                                        {
                                            "number": "2.12.2",
                                            "published_at": "2013-01-12T18:56:40.027Z"
                                        },
                                        {
                                            "number": "2.12.1",
                                            "published_at": "2013-01-07T23:04:53.104Z"
                                        },
                                        {
                                            "number": "2.12.0",
                                            "published_at": "2012-11-13T03:37:01.354Z"
                                }
                            ]
        """
        self.addMetric(librariesio.dependents, 'dependents')

        ### OTHER ###
        """
        @api {get} /:owner/:repo/bus_factor Bus Factor
        @apiName BusFactor
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "best": "5",
                                    "worst": "1"
                                }
                            ]
        """
        self.addMetric(github.bus_factor, "bus_factor")

        """
        @api {get} /git/lines_changed/:git_repo_url Lines Changed by Author
        @apiName ChangesByAuthor
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "additions":2,
                                    "author_date":"2018-05-14 10:09:57 -0500",
                                    "author_email":"s@goggins.com",
                                    "author_name":"Sean P. Goggins",
                                    "commit_date":"2018-05-16 10:12:22 -0500",
                                    "committer_email":"derek@howderek.com",
                                    "committer_name":"Derek Howard",
                                    "deletions":0,"hash":"77e603a",
                                    "message":"merge dev",
                                    "parents":"b8ec0ed"
                                }
                            ]
        """
        self.addGitMetric(git.changes_by_author, 'changes_by_author')

        """
        @api {get} /:owner/:repo/timeseries/downloads Downloads
        @apiName Downloads
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2018-06-14",
                                    "downloads": 129148
                                },
                                {
                                    "date": "2018-06-13",
                                    "downloads": 131262
                                }
                            ]
        """
        self.addTimeseries(downloads.downloads, 'downloads')

        @app.route('/{}/git/repos'.format(AUGUR_API_VERSION))
        def downloaded_repos():
            drs = self.transform(git.downloaded_repos())
            return Response(response=drs,
                            status=200,
                            mimetype="application/json")

        """
        @api {get} /git/lines_changed/:git_repo_url Lines Changed (minus whitespace)
        @apiName LinesChanged 
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "additions":2,
                                    "author_date":"2018-05-14 10:09:57 -0500",
                                    "author_email":"s@goggins.com",
                                    "author_name":"Sean P. Goggins",
                                    "commit_date":"2018-05-16 10:12:22 -0500",
                                    "committer_email":"derek@howderek.com",
                                    "committer_name":"Derek Howard",
                                    "deletions":0,
                                    "hash":"77e603a",
                                    "message":"merge dev",
                                    "parents":"b8ec0ed"
                                }
                            ]
        """
        self.addGitMetric(git.lines_changed_minus_whitespace, 'lines_changed')

        """
        @api {get} /:owner/:repo/linking_websites Linking Websites
        @apiName LinkingWebsites
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "url": "missouri.edu",
                                    "rank": "1"
                                },
                                {
                                    "url": "unomaha.edu",
                                    "rank": "2"
                                }
                            ]
        """
        self.addMetric(publicwww.linking_websites, 'linking_websites')

        """
        @api {get} /:owner/:repo/timeseries/tags/major Major Tags
        @apiName MajorTags
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2008-04-10T17:25:14-07:00",
                                    "release": "v1.0.0"
                                },
                                {
                                    "date": "2008-04-10T17:25:47-07:00",
                                    "release": "v2.0.0"
                                }
                            ]
        """
        self.addTimeseries(github.major_tags, 'tags/major')

        """
        @api {get} /:owner/:repo/timeseries/tags/major Tages
        @apiName Tags
        @apiGroup Experimental
        @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

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
        self.addTimeseries(github.tags, 'tags')

        """
        @api {get} /ghtorrent_range GHTorrent Date Range
        @apiName GhtorrentRange
        @apiGroup Utility
        """
        @app.route('/{}/ghtorrent_range'.format(AUGUR_API_VERSION))

        def ghtorrent_range():
            ghtorrent_range = self.transform(ghtorrent.ghtorrent_range())
            return Response(response=ghtorrent_range,
                            status=200,
                            mimetype="application/json")

        #######################
        #   Batch Requests    #
        #######################

        """
        @api {post} /batch Batch Requests
        @apiName Batch
        @apiGroup Batch
        @apiDescription Returns results of batch requests
        POST JSON of api requests
        """
        #TODO: documentation
        @app.route('/{}/batch'.format(AUGUR_API_VERSION), methods=['GET', 'POST'])
        def batch():
            """
            Execute multiple requests, submitted as a batch.
            :statuscode 207: Multi status
            """
            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response('{"status": "501", "response": "Defaults for batch requests not implemented. Please POST a JSON array of requests to this endpoint for now."}')

            try:
                requests = json.loads(request.data)
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):


                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:

                    with app.app_context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                # Can modify flask.g here without affecting
                                # flask.g of the root request for the batch

                                # Pre process Request
                                rv = app.preprocess_request()

                                if rv is None:
                                    # Main Dispatch
                                    rv = app.dispatch_request()

                            except Exception as e:
                                rv = app.handle_user_exception(e)

                            response = app.make_response(rv)

                            # Post process Request
                            response = app.process_response(response)

                    # Response is a Flask response object.
                    # _read_response(response) reads response.response
                    # and returns a string. If your endpoints return JSON object,
                    # this string would be the response as a JSON string.
                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8')
                    })

                except Exception as e:

                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })


            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")

        augur_app.finalize_config()


    def transform(self, data, orient='records', 
        group_by=None, on=None, aggregate='sum', resample=None, date_col='date'):

        if orient is None:
            orient = 'records'

        result = ''

        if hasattr(data, 'to_json'):
            if group_by is not None:
                data = data.group_by(group_by).aggregate(aggregate)
            if resample is not None:
                data['idx'] = pd.to_datetime(data[date_col])
                data = data.set_index('idx')
                data = data.resample(resample).aggregate(aggregate)
                data['date'] = data.index
            result = data.to_json(orient=orient, date_format='iso', date_unit='ms')
        else:
            try:
                result = json.dumps(data)
            except:
                result = data

        return result

    def flaskify(self, func, cache=True):
        """
        Simplifies API endpoints that just accept owner and repo,
        transforms them and spits them out
        """
        if cache:
            def generated_function(*args, **kwargs):
                def heavy_lifting():
                    return self.transform(func(*args, **kwargs), **request.args.to_dict())
                body = self.cache.get(key=str(request.url), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__name__
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=self.transform(func(*args, **kwargs)),
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__name__
            return generated_function

    def addMetric(self, function, endpoint, cache=True, augur_metric=None):
        """Simplifies adding routes that only accept owner/repo"""
        endpoint = '/{}/<owner>/<repo>/{}'.format(AUGUR_API_VERSION, endpoint)
        self.app.route(endpoint)(self.flaskify(function, cache=cache))
        self.updateMetricMetadata(augur_metric, endpoint)
        


    def addGitMetric(self, function, endpoint, cache=True, augur_metric=None):
        """Simplifies adding routes that accept"""
        endpoint = '/{}/git/{}/<path:repo_url>/'.format(AUGUR_API_VERSION, endpoint)
        self.app.route(endpoint)(self.flaskify(function, cache=cache))
        self.updateMetricMetadata(augur_metric, endpoint)

    def addTimeseries(self, function, endpoint, augur_metric=None):
        """
        Simplifies adding routes that accept owner/repo and return timeseries
        :param app:       Flask app
        :param function:  Function from a datasource to add
        :param endpoint:  GET endpoint to generate
        """
        self.addMetric(function, 'timeseries/{}'.format(endpoint), augur_metric=augur_metric)

    def updateMetricMetadata(self, augur_metric, endpoint):
        if augur_metric is not None:
            update_metric(augur_metric, {
                'endpoint': endpoint            
            })

def run():
    server = Server()
    host = server.augur_app.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = server.augur_app.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    Server().app.run(host=host, port=int(port))

wsgi_app = None
def wsgi(env, start_response):
    global wsgi_app
    if (wsgi_app is None):
        app_instance = Server()
        wsgi_app = app_instance.app
    return wsgi_app(env, start_response)

if __name__ == "__main__":
    run()