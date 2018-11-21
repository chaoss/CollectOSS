from flask import Response

def create_routes(server):

    facade = server._augur['facade']()

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

    @server.app.route('/{}/git/repos'.format(server.api_version))
    def facade_downloaded_repos(): #TODO: make this name automatic - wrapper?
        drs = server.transform(facade.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=facade.downloaded_repos, endpoint='/{}/facade/repos'.format(server.api_version), metric_type='facade')

    """
    @api {get} /facade/lines_changed/:facade_repo_url Lines Changed by Author
    @apiName lines-changed-by-author
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

    @apiParam {String} facade_repo_url URL of the GitHub repository as it appears in the Facade

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
    server.addGitMetric(facade.lines_changed_by_author, 'changes_by_author')

    """
    @api {get} /facade/lines_changed_by_week/:facade_repo_url Lines Changed by Week
    @apiName lines-changed-by-week
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

    @apiParam {String} facade_repo_url URL of the GitHub repository as it appears in the Facade

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "date": "2014-11-07T00:00:00.000Z",
                                "additions": 1263564,
                                "deletions": 1834,
                                "whitespace": 27375
                            }
                        ]
    """
    server.addGitMetric(facade.lines_changed_by_week, 'lines_changed_by_week')

    """
    @api {get} /facade/lines_changed_by_month/:facade_repo_url Lines Changed by Month
    @apiName lines-changed-by-month
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally.

    @apiParam {String} facade_repo_url URL of the GitHub repository as it appears in the Facade

    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "author_email": "agiammarchi@twitter.com",
                                "affiliation": "Twitter",
                                "month": 11,
                                "year": 2014,
                                "additions": 5477,
                                "deletions": 50511,
                                "whitespace": 37
                            },
                            {
                                "author_email": "andrea.giammarchi@gmail.com",
                                "affiliation": "(Unknown)",
                                "month": 11,
                                "year": 2014,
                                "additions": 0,
                                "deletions": 0,
                                "whitespace": 0
                            }
                        ]
    """
    server.addGitMetric(facade.lines_changed_by_month, 'lines_changed_by_month')
