#SPDX-License-Identifier: MIT
"""
Data source that uses Facade's tables
"""
import base64
import pandas as pd
import sqlalchemy as s
from augur import logger
from augur.util import annotate
# end imports
# (don't remove the above line, it's for a script)
class Facade(object):
    """Queries Facade"""
    def __init__(self, user, password, host, port, dbname, projects=None):
        """
        Connect to the database
        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )
        logger.debug('Facade: Connecting to {}:{}/{} as {}'.format(host, port, dbname, user))
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)
        self.projects = projects
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
    @annotate(tag='downloaded-repos')
    def downloaded_repos(self):
        """
        Returns all repository names, URLs, and base64 URLs in the facade database
        """
        downloadedReposSQL = s.sql.text("""
            SELECT git AS url, status, projects.name as project_name
            FROM repos
            JOIN projects
            ON repos.projects_id = projects.id
        """)
        results = pd.read_sql(downloadedReposSQL, self.db)
        results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])
        if self.projects:
            results = results[results.project_name.isin(self.projects)]
        b64_urls = []
        for i in results.index:
            b64_urls.append(base64.b64encode((results.at[i, 'url']).encode()))
        results['base64_url'] = b64_urls
        return results
    @annotate(tag='lines-changed-by-author')
    def lines_changed_by_author(self, repo_url):
        """
        Returns number of lines changed per author per day 
        :param repo_url: the repository's URL
        """
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT author_email, author_date, author_affiliation as affiliation, SUM(added) as additions, SUM(removed) as deletions, SUM(whitespace) as whitespace
            FROM analysis_data
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            GROUP BY repos_id, author_date, author_affiliation, author_email
            ORDER BY author_date ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='lines-changed-by-week')
    def lines_changed_by_week(self, repo_url):
        """
        Returns lines changed of a sent repository per week 
        :param repo_url: the repository's URL
        """
        linesChangedByWeekSQL = s.sql.text("""
            SELECT date(author_date) as date, SUM(added) as additions, SUM(removed) as deletions, SUM(whitespace) as whitespace
            FROM analysis_data
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            GROUP BY YEARWEEK(author_date) 
            ORDER BY YEARWEEK(author_date) ASC
        """)
        results = pd.read_sql(linesChangedByWeekSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='lines-changed-by-month')
    def lines_changed_by_month(self, repo_url):
        """
        Returns lines changed of a sent repository per month 
        :param repo_url: the repository's URL
        """
        linesChangedByMonthSQL = s.sql.text("""
            SELECT email as author_email, affiliation, month, year, SUM(added) as additions, SUM(removed) as deletions, SUM(whitespace) as whitespace FROM repo_monthly_cache 
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            GROUP BY email, month, year
            ORDER BY year, month, email ASC
        """)
        results = pd.read_sql(linesChangedByMonthSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='commits-by-week')
    def commits_by_week(self, repo_url):
        """
        Returns number of patches per commiter per week
        :param repo_url: the repository's URL
        """
        commitsByMonthSQL = s.sql.text("""
            SELECT email AS author_email, affiliation, WEEK AS `week`, YEAR AS `year`, patches FROM repo_weekly_cache 
            WHERE repos_id = (SELECT id FROM repos WHERE git LIKE :repourl LIMIT 1)
            GROUP BY email, WEEK, YEAR
            ORDER BY YEAR, WEEK, email ASC
        """)
        results = pd.read_sql(commitsByMonthSQL, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
<<<<<<< Updated upstream
=======
    @annotate(tag='top-new-repos-this-year-commits')
    def top_new_repos_this_year_commits(self, repo_url):
        """
        Returns top new repos this year by commits
        :param limit: number of repos the user wishes to display
        """
        
        topNewReposCommits = s.sql.text("""
           SELECT repos_id, sum(cast(repo_annual_cache.added as signed) - cast(removed as signed) - cast(whitespace as signed)) as net, patches, projects.name
           FROM repo_annual_cache, projects, repos
           where projects.name = (SELECT projects.name FROM repos, projects
           WHERE git LIKE :repourl
           and repos.projects_id = projects.id
           and YEAR(repos.added) = YEAR(CURDATE())
           LIMIT 1)
           and repo_annual_cache.repos_id = repos.id
           and repos.projects_id = projects.id
           group by repos_id
           ORDER BY net desc
           LIMIT 10
        """)
        results = pd.read_sql(topNewReposCommits, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='top-new-repos-this-year-lines-of-code')
    def top_new_repos_this_year_lines_of_code(self, repo_url):
        """
        Returns top new repos this year by lines of code
        :param limit: number of repos the user wishes to display
        """       
        topNewReposLines = s.sql.text("""
            SELECT repos_id, sum(cast(repo_annual_cache.added as signed) - cast(removed as signed) - cast(whitespace as signed)) as net, patches, projects.name
           FROM repo_annual_cache, projects, repos
           where projects.name = (SELECT projects.name FROM repos, projects
           WHERE git LIKE :repourl
           and YEAR(repos.added) = YEAR(CURDATE())
           and repos.projects_id = projects.id
           LIMIT 1)
           and repo_annual_cache.repos_id = repos.id
           and repos.projects_id = projects.id
           group by repos_id
           ORDER BY net desc
           LIMIT 10
        """)
        results = pd.read_sql(topNewReposLines, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='top-repos-all-time-commits')
    def top_repos_all_time_commits(self, repo_url):
        """
        Returns top new repos of all time by commits
        :param limit: number of repos the user wishes to display
        """       
        topNewReposCommitsAllTime = s.sql.text("""
           SELECT repos_id, repos.name as name, sum(cast(repo_annual_cache.added as signed) - cast(removed as signed) - cast(whitespace as signed)) as net, patches
           FROM repo_annual_cache, projects, repos
           where projects.name = (SELECT projects.name FROM repos, projects
           WHERE git LIKE :repourl
           and repos.projects_id = projects.id
           LIMIT 1)
           and repo_annual_cache.repos_id = repos.id
           and repos.projects_id = projects.id
           group by repos_id
           ORDER BY net desc
           LIMIT 10
        """)
        results = pd.read_sql(topNewReposCommitsAllTime, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
    @annotate(tag='top-repos-all-time-lines-of-code')
    def top_repos_all_time_lines_of_code(self, repo_url):
        """
        Returns top new repos of all time by lines of code
        :param limit: number of repos the user wishes to display
        """
        topNewReposLinesAllTime = s.sql.text("""
            SELECT repos_id, repos.name as name, sum(cast(repo_annual_cache.added as signed) - cast(removed as signed) - cast(whitespace as signed)) as net, patches
           FROM repo_annual_cache, projects, repos
           where projects.name = (SELECT projects.name FROM repos, projects
           WHERE git LIKE :repourl
           and repos.projects_id = projects.id
           LIMIT 1)
           and repo_annual_cache.repos_id = repos.id
           and repos.projects_id = projects.id
           group by repos_id
           ORDER BY net desc
           LIMIT 10
        """)
        results = pd.read_sql(topNewReposLinesAllTime, self.db, params={"repourl": '%{}%'.format(repo_url)})
        return results
>>>>>>> Stashed changes
