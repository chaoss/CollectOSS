
import pandas as pd
import sqlalchemy as s
import numpy as np
import re
from augur import logger
from augur.util import annotate
from flask import request, Response


def __init__(self, user, password, host, port, dbname):
        """
        Connect to GHTorrent

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )
        logger.debug('GHTorrent: Connecting to {}:{}/{} as {}'.format(host, port, dbname, user))
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)
        try:
            self.userid('howderek')
        except Exception as e:
            logger.error("Could not connect to GHTorrent database. Error: " + str(e))

def create_routes(server):  

    ghtorrent = server._augur['ghtorrent']()


    server.addTimeseries(ghtorrent.closed_issues, 'issues/closed')


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


@annotate(tag='closed-issues')
def closed_issues(self, owner, repo=None):
    """
    Timeseries of the count of the number of issues closed per week

    :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
    :param repo: The name of the repo. Unneeded if repository id was passed as owner.
    :return: DataFrame with newly closed issues/week
    """
    repoid = self.repoid(owner, repo)
    issuesClosedSQL = s.sql.text("""
    SELECT SUBDATE(DATE(issue_events.created_at), WEEKDAY(DATE(issue_events.created_at))) AS "date",
           COUNT(*) as issues_closed
        FROM issue_events, issues
        WHERE issue_events.issue_id = issues.id
        AND issue_events.action = "closed"
        AND issues.repo_id = :repoid
        GROUP BY YEARWEEK(issue_events.created_at)
    """)
    return pd.read_sql(issuesClosedSQL, self.db, params={"repoid": str(repoid)})