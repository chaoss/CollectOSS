#SPDX-License-Identifier: MIT
"""
Creates routes for the Augur database data source plugin
"""

from flask import request, Response

def create_routes(server):  

    augur_db = server._augur['augur_db']()

    """
    @api {get} /git/lines_changed/:facade_repo_url Lines Changed by Author
    @apiName lines-changed-by-author
    @apiGroup Experimental
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository

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
    server.addGitMetric(augur_db.lines_changed_by_author, 'changes_by_author')