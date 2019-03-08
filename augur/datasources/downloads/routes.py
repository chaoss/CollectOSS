#SPDX-License-Identifier: MIT
"""
Creates routes for the downloads data source plugin
"""

def create_routes(server):

    downloads = server._augur['downloads']()

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
    
    """
    @api {get} /:owner/:repo/timeseries/downloads Downloads
    @apiName downloads
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: <a href="https://developer.github.com/">GitHub API</a>

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
    server.addTimeseries(downloads.downloads, 'downloads')

