def create_routes(server):

	downloads = server.augur_app.downloads()

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
	server.addTimeseries(downloads.downloads, 'downloads')

