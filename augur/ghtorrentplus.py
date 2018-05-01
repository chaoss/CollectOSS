import pandas as pd
import sqlalchemy as s
import numpy as np
import re

class GHTorrentPlus(object):
    """Manages the custom schema for GHTorrent to improve performance of slow queries"""

    def __init__(self, dbstr, ghtorrent, buildMode="auto"):
        """
        Connect to the database

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = dbstr
        self.db = s.create_engine(dbstr, poolclass=s.pool.NullPool)
        self.ghtorrent = ghtorrent

        try:
            # Table creation
            if (buildMode == 'rebuild') or ((not self.db.dialect.has_table(self.db.connect(), 'issue_response_time')) 
                                            and buildMode == "auto"):
                print("[GHTorrentPlus] Creating Issue Response Time table...")
                self.build_issue_response_time()
        except Exception as e:
            print("Could not connect to GHTorrentPlus database.\nError: " + str(e))
            print("API calls that depend on GHTorrentPlus will fail.")

    def build_issue_response_time(self):
        issuesClosedSQL = s.sql.text("""
            SELECT *, TIMESTAMPDIFF(MINUTE, opened, closed) AS minutes_to_close FROM ( 
                
                SELECT issues.id AS id, issues.repo_id AS repo_id, issues.created_at AS opened, issue_events.created_at AS closed, 0 AS pull_request
                FROM issue_events
                LEFT JOIN issues
                ON issues.id = issue_events.issue_id
                WHERE issues.pull_request = 0
                AND issue_events.action = 'closed'
                
                UNION ALL
                
                SELECT issues.id AS id, issues.repo_id AS repo_id, issues.created_at AS opened, pull_request_history.created_at AS closed, 1 AS pull_request
                FROM pull_request_history
                LEFT JOIN issues
                ON issues.pull_request_id = pull_request_history.pull_request_id
                WHERE issues.pull_request = 1
                AND pull_request_history.action = 'closed'

            ) a
        """)
        issue_response_time = pd.read_sql(issuesClosedSQL, self.ghtorrent.db, index_col=["id", "repo_id"])
        issue_response_time.to_sql("issue_response_time", self.db, if_exists="append")
        return issue_response_time

    def issue_close_time(self, owner, repo=None):
        repoid = self.ghtorrent.repoid(owner, repo)
        issuesClosedSQL = s.sql.text("""
            SELECT * FROM issue_response_time WHERE repo_id = :repoid ORDER BY closed ASC
        """)
        rs = pd.read_sql(issuesClosedSQL, self.db, params={"repoid": str(repoid)}, index_col='closed')
        rs['average_minutes_to_close_as_of_close'] = rs.rolling(len(rs), 1).mean()['minutes_to_close']
        rs['average_minutes_to_close_past_30_days'] = rs.rolling('30D').mean()['minutes_to_close']
        mean = rs['minutes_to_close'].mean()
        std = rs['minutes_to_close'].std(ddof=0)
        rs['z-score'] = (rs['minutes_to_close'] - mean)/std
        return rs
