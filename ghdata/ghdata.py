#SPDX-License-Identifier: MIT

import sqlalchemy as s
import pandas as pd

class GHData(object):
    """Uses GHTorrent and other GitHub data sources and returns dataframes with interesting GitHub indicators"""
    def __init__(self, dbstr):
        """Connect to GHTorrent and infer the schema"""
        self.db = s.create_engine(dbstr)

    def __single_table_count_by_date(self, table, repo_col='project_id'):
        """Returns query string to count occurances of rows per date for a given table.
        External input must never be sent to this function, it is for internal use only."""
        return """
            SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
            FROM {0}
            WHERE {1} = :repoid
            GROUP BY WEEK(created_at)""".format(table, repo_col)


    def __predicate_dates(table, start=None, end=None):
        """Returns date limiting WHERE clause"""
        if (start and end):
            return "created_at >= '{}'' AND created_at <= '{}'".format(start.isoformat(), end.isoformat())
        elif (start): 
            return "created_at >= '{}'".format(start.isoformat())
        elif (end):
            return "created_at <= '{}'".format(end.isoformat())
        else:
            return ''

    def repoid(self, owner, repo):
        """Returns the project.id given an owner and a repo"""
        reposql = s.sql.text('SELECT projects.id FROM projects INNER JOIN users ON projects.owner_id = users.id WHERE projects.name = :repo AND users.login = :owner')
        repoid = 0
        result = self.db.execute(reposql, repo=repo, owner=owner)
        for row in result:
            repoid = row[0]
        return repoid

    # Basic timeseries queries
    def stargazers(self, repoid, start=None, end=None):
        stargazersSQL = s.sql.text(self.__single_table_count_by_date('watchers', 'repo_id'))
        return pd.read_sql(stargazersSQL, self.db, params={"repoid": str(repoid)})

    def commits(self, repoid, start=None, end=None):
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits'))
        return pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})

    def forks(self, repoid, start=None, end=None):
        forksSQL = s.sql.text(self.__single_table_count_by_date('projects', 'forked_from'))
        return pd.read_sql(forksSQL, self.db, params={"repoid": str(repoid)}).drop(0)

    def issues(self, repoid, start=None, end=None):
        issuesSQL = s.sql.text(self.__single_table_count_by_date('issues', 'repo_id'))
        return pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})

    def pulls(self, repoid, start=None, end=None):
        pullsSQL = s.sql.text("""
            SELECT date(pull_request_history.created_at) AS "date",
            (COUNT(pull_requests.id)) AS "pull_requests",
            (SELECT COUNT(*) FROM pull_request_comments
            WHERE pull_request_comments.pull_request_id = pull_request_history.pull_request_id) AS "comments" 
            FROM pull_request_history
            INNER JOIN pull_requests
            ON pull_request_history.pull_request_id = pull_requests.id
            WHERE pull_requests.head_repo_id = :repoid
            AND pull_request_history.action = "merged"
            GROUP BY WEEK(pull_request_history.created_at)
        """)
        return pd.read_sql(pullsSQL, self.db, params={"repoid": str(repoid)})