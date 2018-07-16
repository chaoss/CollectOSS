import pandas as pd
import sqlalchemy as s
import numpy as np
import re
from augur import logger
from augur.util import annotate
# end imports
# (don't remove the above line, it's for a script)

class Facade(object):
    """Queries Facade"""

    def __init__(self, user, password, host, port, dbname, buildMode="auto"):
        """
        Connect to the database

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )
        logger.debug('Facade: Connecting to {}:{}/{} as {}'.format(host, port, dbname, user))
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)

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

    @annotate(metric_name='downloaded-repos', group='experimental')
    def downloaded_repos(self):
        repoSQL = s.sql.text("""
            SELECT * FROM repos;
        """)
        results = pd.read_sql(repoSQL, self.db)
        return results

    @annotate(metric_name='lines-changed-by-author', group='experimental')
    def lines_changed_by_author(self, repo_url):
        """
        Makes sure the storageFolder contains updated versions of all the repos
        """
        repoSQL = s.sql.text("""
            SELECT author_email, author_date, SUM(added), SUM(removed), SUM(whitespace)
            FROM analysis_data
            WHERE repos_id = (SELECT id FROM repos WHERE git = :repourl)
            GROUP BY repos_id, author_date, author_email
            ORDER BY author_date ASC;
        """)
        results = pd.read_sql(repoSQL, self.db, params={"repourl": repo_url}, index_col=['author_email'])
        return results

    
