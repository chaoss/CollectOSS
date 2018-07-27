def create_routes(server):
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
    print('created routes for publicwww')
    publicwww = server.augur_app.publicwww()
    server.addMetric(publicwww.linking_websites, 'linking_websites')
