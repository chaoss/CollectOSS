#SPDX-License-Identifier: MIT
"""
Data source that uses the Augur relational database of GitHub activity. 
"""

import pandas as pd
import sqlalchemy as s
import numpy as np
import re
from augur import logger
from augur.util import annotate

class Augur(object):
    """Uses the Augur database to return dataframes with interesting GitHub indicators"""

    def __init__(self, user, password, host, port, dbname, schema):
        """
        Connect to Augur

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the Augur database
        """
        print(user, password, host, port, dbname, schema)
        self.DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )

        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool,
            connect_args={'options': '-csearch_path={}'.format(schema)})

        logger.debug('GHTorrent: Connecting to {} schema of {}:{}/{} as {}'.format(schema, host, port, dbname, user))
        
        # try:
        #     self.userid('howderek')
        # except Exception as e:
        #     logger.error("Could not connect to GHTorrent database. Error: " + str(e))

    @annotate(tag='lines-changed-by-author')
    def lines_changed_by_author(self, repo_url):
        """
        Returns number of lines changed per author per day 

        :param repo_url: the repository's URL
        """
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, cmt_author_date, cmt_author_affiliation as affiliation, 
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace
            FROM commits
            WHERE repo_id = (SELECT repo_id FROM repo WHERE repo_git LIKE :repourl LIMIT 1)
            GROUP BY repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email
            ORDER BY cmt_author_date ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results