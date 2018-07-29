def create_routes(server):

    publicwww = server.augur_app.publicwww()

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
    @api {get} /:owner/:repo/linking_websites Linking Websites
    @apiName linking-websites
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
    server.addMetric(publicwww.linking_websites, 'linking_websites')
