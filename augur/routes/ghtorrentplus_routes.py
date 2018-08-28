def create_routes(server):	

	ghtorrentplus = server.augur_app.ghtorrentplus()	

	#####################################	
	###    DIVERSITY AND INCLUSION    ###	
	#####################################	

	#####################################	
	### GROWTH, MATURITY, AND DECLINE ###	
	#####################################	

	"""	
	@api {get} /:owner/:repo/issue_close_time Closed Issue Resolution Duration	
	@apiName closed-issue-resolution-duration	
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
	server.addMetric(ghtorrentplus.closed_issue_resolution_duration, 'issues/time_to_close')	

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
