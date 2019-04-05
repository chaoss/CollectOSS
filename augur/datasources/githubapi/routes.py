#SPDX-License-Identifier: MIT
"""
Creates routes for the GitHub API data source plugin
"""

def create_routes(server):

    github = server._augur['githubapi']()

    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################

    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    """
    @api {get} /:owner/:repo/timeseries/githubapi/issues/closed Closed Issues
    @apiName githubapi-closed-issues
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/wg-gmd/blob/master/metrics/issues-closed.md">CHAOSS Metric Definition</a>

    @apiGroup Growth-Maturity-Decline
    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "created_at": "2019-01-09T00:00:00.000Z",
                                "count": 1
                            },
                            {
                                "created_at": "2019-01-10T00:00:00.000Z",
                                "count": 2
                            }
                        ]
    """
    server.addTimeseries(github.closed_issues, 'githubapi/issues/closed')

    """
    @api {get} /:owner/:repo/timeseries/githubapi/commits Code Commits
    @apiName githubapi-code-commits
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/wg-gmd/blob/master/activity-metrics/code-commits.md">CHAOSS Metric Definition</a>

    @apiGroup Growth-Maturity-Decline
    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "created_at": "2017-01-30T00:00:00.000Z",
                                "count": 6
                            },
                            {
                                "created_at": "2017-01-31T00:00:00.000Z",
                                "count": 14
                            }
                        ]
    """
    server.addTimeseries(github.code_commits, 'githubapi/commits')

    """
    @api {get} /:owner/:repo/githubapi/contributors List of Contributors & their Contributions
    @apiName githubapi-contributors
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/wg-gmd/blob/master/metrics/contributors.md">CHAOSS Metric Definition</a>

    @apiGroup Growth-Maturity-Decline
    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "login": "howderek",
                                "contributions": 372
                            },
                            {
                                "login": "ccarterlandis",
                                "contributions": 190
                            }
                        ]
    """
    server.addMetric(github.contributors, 'githubapi/contributors')

    """
    @api {get} /:owner/:repo/lines_changed Lines of Code Changed
    @apiName lines-of-code-changed
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/augurlabs/metrics/blob/master/activity-metrics/lines-of-code-changed.md">CHAOSS Metric Definition</a>.  Source: <a href="https://developer.github.com/">GitHub API</a>

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
    server.addMetric(github.lines_of_code_changed, 'lines_changed')

    """
    @api {get} /:owner/:repo/timeseries/githubapi/issues Issues Opened
    @apiName githubapi-issues-opened
    @apiGroup Growth-Maturity-Decline
    @apiDescription <a href="https://github.com/chaoss/wg-gmd/blob/master/metrics/issues-open.md">CHAOSS Metric Definition</a>

    @apiGroup Growth-Maturity-Decline
    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "created_at": "2019-02-28T00:00:00.000Z",
                                "count": 4
                            },
                            {
                                "created_at": "2019-03-01T00:00:00.000Z",
                                "count": 1
                            },
                        ]
    """
    server.addTimeseries(github.open_issues, 'githubapi/issues')

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
    @api {get} /:owner/:repo/githubapi/repository_size Repository Size
    @apiName repository-size
    @apiGroup Activity
    @apiDescription <a href="https://github.com/chaoss/wg-gmd/blob/master/metrics/archived_metrics/repository-size.md">CHAOSS Metric Definition</a>

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
    server.addMetric(github.repository_size, "githubapi/repository_size")

    

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    """
    @api {get} /:owner/:repo/bus_factor Bus Factor
    @apiName bus-factor
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://developer.github.com/">GitHub API</a>

    @apiParam {String} owner Username of the owner of the GitHub repository
    @apiParam {String} repo Name of the GitHub repository
    @apiParam {Int} threshold Percentage used to determine how many lost people would kill the project

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "best": "5",
                                "worst": "1"
                            }
                        ]
    """
    server.addMetric(github.bus_factor, "bus_factor")

    """
    @api {get} /:owner/:repo/timeseries/tags/major Major Tags
    @apiName major-tags
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://developer.github.com/">GitHub API</a>

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
    server.addTimeseries(github.major_tags, 'tags/major')

    """
    @api {get} /:owner/:repo/timeseries/tags/major Tages
    @apiName tags
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://developer.github.com/">GitHub API</a>

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
    server.addTimeseries(github.tags, 'tags')