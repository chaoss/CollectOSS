import pandas as pd
import sqlalchemy as s
import numpy as np
import re
from augur import logger

class GHTorrent(object):
    """Uses GHTorrent and other GitHub data sources and returns dataframes with interesting GitHub indicators"""

    def __init__(self, user, password, host, port, dbname):
        """
        Connect to GHTorrent

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
            user, password, host, port, dbname
        )
        logger.info('GHTorrent: Connecting to {}:{}/{} as {}'.format(host, port, dbname, user))
        self.db = s.create_engine(self.DB_STR, poolclass=s.pool.NullPool)
        try:
            self.userid('howderek')
        except Exception as e:
            logger.error("Could not connect to GHTorrent database. Error: " + str(e))

    def __single_table_count_by_date(self, table, repo_col='project_id', user_col='author_id', group_by="week"):
        """
        Generates query string to count occurances of rows per date for a given table.
        External input must never be sent to this function, it is for internal use only.

        :param table: The table in GHTorrent to generate the string for
        :param repo_col: The column in that table with the project ids
        :param user_col: The column in that table with the user ids
        :param group_by: Default week; Options raw, day, week, month, year; Selects period of time to be grouped by
        :return: Query string
        """
        if group_by == "raw":
            return """
                SELECT date(created_at) AS "date", {2} AS "user_id"
                FROM {0}
                WHERE {1} = :repoid
                """.format(table, repo_col, user_col)

        if group_by == "day":
            return """
                SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
                FROM {0} 
                WHERE {1} = :repoid
                GROUP BY DATE(created_at)""".format(table, repo_col)

        if group_by == "week":
            return """
                SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY YEARWEEK(created_at)""".format(table, repo_col)

        if group_by == "month":
            return """
                SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY MONTH(created_at), YEAR(created_at)""".format(table, repo_col)

        if group_by == "year":
            return """
                SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY YEAR(created_at)""".format(table, repo_col)


    def __sub_table_count_by_date(self, parent_table, sub_table, parent_id, sub_id, project_id):
        """
        Generates query string to count occurances of rows per date for a given query sub-table.
        A query sub-table is a table that describes in more detail a specfic asset of another query table-
        for example, the table "pull_request_comments" is a sub table of "pull_request", where the query is pull requests.
        External input must never be sent to this function, it is for internal use only.

        :param parent_table: The table in GHTorrent that holds the related project_id and parent_id
        :param sub_table: The table in GHTorrent to generate the string for
        :param parent_id: The column in parent_table with the query id
        :param sub_id: The column in sub_id with the query id
        :param project_id: the column in parent_table that holds the repoid
        :return: Query string
        """
        return """
            SELECT date({1}.created_at) AS "date", COUNT(*) AS counter
            FROM {1}, {0}
            WHERE {1}.{3} = {0}.{2}
            AND {0}.{4} = :repoid
            GROUP BY YEARWEEK({1}.created_at)""".format(parent_table, sub_table, parent_id, sub_id, project_id)
    

    def repoid(self, owner_or_repoid, repo=None):
        """
        Returns a repository's ID as it appears in the GHTorrent projects table
        github.com/[owner]/[project]

        :param owner: The username of a project's owner
        :param repo: The name of the repository
        :return: The repository's ID as it appears in the GHTorrent projects table
        """
        repoid = 0
        if repo is None:
            repoid = owner_or_repoid
        else:
            reposql = s.sql.text('SELECT projects.id FROM projects INNER JOIN users ON projects.owner_id = users.id WHERE projects.name = :repo AND users.login = :repoowner')
            result = self.db.execute(reposql, repo=repo, repoowner=owner_or_repoid)
            for row in result:
                repoid = row[0]
        return repoid

    def userid(self, username):
        """
        Returns the userid given a username

        :param username: GitHub username to be matched against the login table in GHTorrent
        :return: The id from the users table in GHTorrent
        """
        reposql = s.sql.text('SELECT users.id FROM users WHERE users.login = :username')
        userid = 0
        result = self.db.execute(reposql, username=username)
        for row in result:
            userid = row[0]
        return userid


    #####################################
    ###    DIVERSITY AND INCLUSION    ###
    #####################################



    #####################################
    ### GROWTH, MATURITY, AND DECLINE ###
    #####################################

    def issues(self, owner, repo=None, group_by="week"):
        """
        Subgroup: Individual Diversity
        chaoss-metric: open-issues

        Timeseries of issues opened per day

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with issues/day
        """
        repoid = self.repoid(owner, repo)
        issuesSQL = s.sql.text(self.__single_table_count_by_date('issues', 'repo_id', 'reporter_id', group_by=group_by))
        return pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})

    def issues_closed(self, owner, repo=None):
        """
        Subgroup: Issue Resolution
        chaoss-metric: closed-issues
        """
        repoid = self.repoid(owner, repo)
        issuesClosedSQL = s.sql.text("""
        SELECT date(issue_events.created_at) as "date", COUNT(*) as issues_closed
            FROM issue_events, issues
            WHERE issue_events.issue_id = issues.id
            AND issue_events.action = "closed"
            AND issues.repo_id = :repoid
            GROUP BY YEARWEEK(issue_events.created_at)
        """)
        return pd.read_sql(issuesClosedSQL, self.db, params={"repoid": str(repoid)})

    def issue_response_time(self, owner, repo):
        """
        Subgroup: Issue Resolution
        chaoss-metric: issue-response-time

        Time to comment by issue

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame with each row being am issue
        """
        repoid = self.repoid(owner, repo)
        issueCommentsSQL = s.sql.text("""
            SELECT *, TIMESTAMPDIFF(MINUTE, opened, first_commented) AS minutes_to_comment FROM ( 
                
                SELECT issues.id AS id, issues.created_at AS opened, MIN(issue_comments.created_at) AS first_commented, 0 AS pull_request
                FROM issues
                LEFT JOIN issue_comments
                ON issues.id = issue_comments.issue_id
                WHERE issues.pull_request = 0 AND issues.repo_id = :repoid
                GROUP BY id
                
                UNION ALL
                
                SELECT issues.id AS id, issues.created_at AS opened, MIN(pull_request_comments.created_at) AS first_commented, 1 AS pull_request
                FROM issues
                LEFT JOIN pull_request_comments
                ON issues.pull_request_id = pull_request_comments.pull_request_id
                WHERE issues.pull_request = 1 AND issues.repo_id = :repoid
                GROUP BY id
             ) a
            """)
        rs = pd.read_sql(issueCommentsSQL, self.db, params={"repoid": str(repoid)})
        return rs

    def issues_with_close(self, owner, repo=None):
        """
        Subgroup: Issue Resolution
        chaoss-metric: closed-issue-resolution-duration

        How long on average each week it takes to close an issue

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with issues/day
        """
        repoid = self.repoid(owner, repo)
        issuesWithCloseSQL = s.sql.text("""
            SELECT issues.id as "id",
                   issues.created_at as "date",
                   DATEDIFF(closed.created_at, issues.created_at)  AS "days_to_close"
            FROM issues

           JOIN
                (SELECT * FROM issue_events
                 WHERE issue_events.action = "closed") closed
            ON issues.id = closed.issue_id

            WHERE issues.repo_id = :repoid""")
        return pd.read_sql(issuesWithCloseSQL, self.db, params={"repoid": str(repoid)})

    def commits(self, owner, repo=None, group_by="week"):
        """
        Subgroup: Code Development
        chaoss-metric: code-commits

        Timeseries of all the commits on a repo

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with commits/day
        """
        repoid = self.repoid(owner, repo)
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits', group_by=group_by))
        return pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})

    def time_to_first_maintainer_response_to_merge_request(self, owner, repo=None):
        """
        Subgroup: Code Development
        chaoss-metric: maintainer-response-to-merge-request-duration

        *1). Get a list of all the comments on merge requests, and the user ids of the people who made those comments
        2). Get a list of all maintainers for the repository
        3). For merge request, append the ID of the first comment that was made by a maintainer to an array, if it exists (also append the issue id to a different array) ***use a data frame?***
        *4). For every one of those comment IDs, append the timestamp difference to a array
        5). Calculate mean time per week

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame with each row being am issue
        """
        repoid = self.repoid(owner, repo)
        maintainerResponseToMRSQL = s.sql.text("""
             SELECT issues.id AS issue_id, issues.created_at AS pull_request_created_at, pull_request_comments.created_at AS pull_request_comment_created_at, pull_request_comments.user_id AS user_id, pull_request_comments.comment_id as pull_request_comment_id
                FROM issues
                JOIN pull_request_comments
                ON issues.pull_request_id = pull_request_comments.pull_request_id
                WHERE issues.pull_request = 1 
                AND issues.repo_id = :repoid
            """) 
        df = pd.read_sql(maintainerResponseToMRSQL, self.db, params={"repoid": str(repoid)})

        classified = self.classify_contributors(repoid, repo=None)

        maintainerIDs = []
        for index, row in classified.iterrows():
            if row['role'] == "maintainer":
                maintainerIDs = np.append(maintainerIDs, row['user'])

        commentIDs = []
        issueIDs = []
        rowArray = []
        for index, row in df.iterrows():
            for user in maintainerIDs:
                if row['user_id'] == user:
                    commentIDs.append(row['pull_request_comment_id'])
                    issueIDs.append(row['issue_id'])
                    rowArray.append(index)
                    break

        times = []
        for row in rowArray:
            timedelta = (df.loc[row, 'pull_request_comment_created_at'] - df.loc[row, 'pull_request_created_at']).total_seconds()
            if timedelta > 0:
                times = np.append(times, timedelta)

        df2 = pd.DataFrame(data=times, columns=["response_time"])
        return df2

    def forks(self, owner, repo=None, group_by="week"):
        """
        Subgroup: Code Development
        chaoss-metric: forks

        Timeseries of when a repo's forks were created

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with forks/day
        """
        repoid = self.repoid(owner, repo)
        forksSQL = s.sql.text(self.__single_table_count_by_date('projects', 'forked_from', 'owner_id', group_by=group_by))
        return pd.read_sql(forksSQL, self.db, params={"repoid": str(repoid)}).drop(0)


    def pulls(self, owner, repo=None):
        """
        Subgroup: Code Development
        chaoss-metric: pull-requests-open

        Timeseries of pull requests creation, also gives their associated activity

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with pull requests by day
        """
        repoid = self.repoid(owner, repo)
        pullsSQL = s.sql.text("""
            SELECT date(pull_request_history.created_at) AS "date",
            COUNT(pull_requests.id) AS "pull_requests"
            FROM pull_request_history
            INNER JOIN pull_requests
            ON pull_request_history.pull_request_id = pull_requests.id
            WHERE pull_requests.head_repo_id = :repoid
            AND pull_request_history.action = "merged"
            GROUP BY WEEK(pull_request_history.created_at)
        """)
        return pd.read_sql(pullsSQL, self.db, params={"repoid": str(repoid)})

    def pull_request_comments(self, owner, repo=None):
        """
        Subgroup: Code Development
        chaoss-metric: pull-request-comments

        Timeseries of pull request comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new by week
        """
        repoid = self.repoid(owner, repo)
        pullRequestCommentsSQL = s.sql.text(self.__sub_table_count_by_date("pull_requests", "pull_request_comments", "pullreq_id", "pull_request_id", "base_repo_id"))
        return pd.read_sql(pullRequestCommentsSQL, self.db, params={"repoid": str(repoid)})


    #####################################
    ###            RISK               ###
    #####################################





    #####################################
    ###            VALUE              ###
    #####################################





    #####################################
    ###           ACTIVITY            ###
    #####################################

    def watchers(self, owner, repo=None, group_by="week"):
        """
        Timeseries of when people starred a repo

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with stargazers/day
        """
        repoid = self.repoid(owner, repo)
        stargazersSQL = s.sql.text(self.__single_table_count_by_date('watchers', 'repo_id', 'user_id', group_by=group_by))
        df = pd.read_sql(stargazersSQL, self.db, params={"repoid": str(repoid)})
        df.drop(df.index[:1], inplace=True)
        return df


    def issue_comments(self, owner, repo=None):
        """
        Timeseries of issue comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new by week
        """
        repoid = self.repoid(owner, repo)
        issueCommentsSQL = s.sql.text(self.__sub_table_count_by_date("issues", "issue_comments", "issue_id", "issue_id", "repo_id"))
        return pd.read_sql(issueCommentsSQL, self.db, params={"repoid": str(repoid)})


    #####################################
    ###         EXPERIMENTAL          ###
    #####################################







    # DEPENDENCY RELATED




    # COMMIT RELATED

    def commits100(self, owner, repo=None, group_by="week"):
        """
        Timeseries of all the commits on a repo

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with commits/day
        """
        repoid = self.repoid(owner, repo)
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits', group_by=group_by))
        temp = pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})
        tem = temp['commits'] > 100
        return temp[tem].reset_index(drop=True)

    def commit_comments(self, owner, repo=None, group_by="week"):
        """
        augur-metric: commit-comments

        Timeseries of commit comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new by week
        """
        repoid = self.repoid(owner, repo)
        commitCommentsSQL = s.sql.text(self.__sub_table_count_by_date("commits", "commit_comments", "id", "commit_id", "project_id"))
        return pd.read_sql(commitCommentsSQL, self.db, params={"repoid": str(repoid)})

    def committer_locations(self, owner, repo=None):        
        """
        Return committers and their locations

        @todo: Group by country code instead of users, needs the new schema

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo.
        :return: DataFrame with users and locations sorted by commtis
        """
        repoid = self.repoid(owner, repo)
        rawContributionsSQL = s.sql.text("""
            SELECT users.login, users.location, COUNT(*) AS "commits"
            FROM commits
            JOIN project_commits
            ON commits.id = project_commits.commit_id
            JOIN users
            ON users.id = commits.author_id
            WHERE project_commits.project_id = :repoid
            GROUP BY users.id
            ORDER BY commits DESC
        """)
        return pd.read_sql(rawContributionsSQL, self.db, params={"repoid": str(repoid)})


    def total_committers(self, owner, repo=None):
        """
        augur-metric: total-committers
        
        Number of total committers as of each week

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame with each row being a week
        """
        repoid = self.repoid(owner, repo)
        totalCommittersSQL = s.sql.text("""
        SELECT total_committers.created_at AS "date", COUNT(total_committers.author_id) total_total_committers
        FROM (
            SELECT author_id, MIN(DATE(created_at)) created_at
            FROM commits
            WHERE project_id = :repoid
            GROUP BY author_id
            ORDER BY created_at ASC) AS total_committers
        GROUP BY YEARWEEK(total_committers.created_at)
        """)
        df = pd.read_sql(totalCommittersSQL, self.db, params={"repoid": str(repoid)})
        df['total_total_committers'] = df['total_total_committers'].cumsum()
        return df

    # ISSUE RELATED

    def issue_activity(self, owner, repo=None):
        """
        augur-metric: issue-activity
        """
        repoid = self.repoid(owner, repo)
        issueActivity = s.sql.text("""
            SELECT Date(issues.created_at) as 'date', COUNT(issues.id) as 'issues_opened', SUM(CASE WHEN issue_events.action = 'closed' THEN 1 ELSE 0 END) as 'issues_closed', SUM(CASE WHEN issue_events.action = 'reopened' THEN 1 ELSE 0 END) as 'issues_reopened'
                FROM issues
                JOIN issue_events ON issues.id = issue_events.issue_id
                WHERE issues.repo_id = :repoid
                GROUP BY YEARWEEK(issues.created_at)
            """) 
        df = pd.read_sql(issueActivity, self.db, params={"repoid": str(repoid)})
        df = df.assign(issues_open = 0)
        globalIssuesOpened = 0
        df["issues_open"] = df["issues_opened"] - df["issues_closed"] + df["issues_reopened"] 
        dates = []
        issueActivityCount = []
        issuesAction = []
        for index, row in df.iterrows():
            for x in range(0, 4):
                dates = np.append(dates, row["date"])
            issueActivityCount = np.append(issueActivityCount, row["issues_closed"])
            issuesAction = np.append(issuesAction, "closed")
            issueActivityCount = np.append(issueActivityCount, row["issues_opened"])
            issuesAction = np.append(issuesAction, "opened")
            issueActivityCount = np.append(issueActivityCount, row["issues_reopened"])
            issuesAction = np.append(issuesAction, "reopened")
            issueActivityCount = np.append(issueActivityCount, row["issues_open"])
            issuesAction = np.append(issuesAction, "open")

        df1 = pd.DataFrame(data=dates, columns=["date"])
        df2 = pd.DataFrame(data=issueActivityCount, columns=["count"])
        df3 = pd.DataFrame(data=issuesAction, columns=["action"])
        df4 = df1.join(df2).join(df3)
        return df4


    # PULL REQUEST RELATED

    def pull_acceptance_rate(self, owner, repo=None):
        """
        augur-metric: pull-acceptance-rate

        Timeseries of pull request acceptance rate (Number of pull requests merged on a date over Number of pull requests opened on a date)

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the pull acceptance rate and the dates
        """
        repoid = self.repoid(owner, repo)
        pullAcceptanceSQL = s.sql.text("""
        SELECT DATE(date_created) AS "date", CAST(num_approved AS DECIMAL)/CAST(num_open AS DECIMAL) AS "rate"
        FROM
            (SELECT COUNT(DISTINCT pull_request_id) AS num_approved, DATE(pull_request_history.created_at) AS accepted_on
            FROM pull_request_history
            JOIN pull_requests ON pull_request_history.pull_request_id = pull_requests.id
            WHERE action = 'merged' AND pull_requests.base_repo_id = :repoid
            GROUP BY accepted_on) accepted
        JOIN
            (SELECT count(distinct pull_request_id) AS num_open, DATE(pull_request_history.created_at) AS date_created
            FROM pull_request_history
            JOIN pull_requests ON pull_request_history.pull_request_id = pull_requests.id
            WHERE action = 'opened'
            AND pull_requests.base_repo_id = :repoid
            GROUP BY date_created) opened
        ON opened.date_created = accepted.accepted_on
        """)
        return pd.read_sql(pullAcceptanceSQL, self.db, params={"repoid": str(repoid)})


    # COMMUNITY / CONRIBUTIONS

    def contributions(self, owner, repo=None, userid=None):
        """
        augur metric: contributions
        Timeseries of all the contributions to a project, optionally limited to a specific user

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :param userid: The id of user if you want to limit the contributions to a specific user.
        :return: DataFrame with all of the contributions seperated by day.
        """
        repoid = self.repoid(owner, repo)
        rawContributionsSQL = """
            SELECT  DATE(coms.created_at) as "date",
                    coms.count            as "commits",
                    pulls.count           as "pull_requests",
                    iss.count             as "issues",
                    comcoms.count         as "commit_comments",
                    pullscoms.count       as "pull_request_comments",
                    isscoms.count         as "issue_comments",
                    coms.count + pulls.count + iss.count + comcoms.count + pullscoms.count + isscoms.count as "total"

            FROM (SELECT created_at AS created_at, COUNT(*) AS count FROM commits INNER JOIN project_commits ON project_commits.commit_id = commits.id WHERE project_commits.project_id = :repoid[[ AND commits.author_id = :userid]] GROUP BY DATE(created_at)) coms

            LEFT JOIN (SELECT pull_request_history.created_at AS created_at, COUNT(*) AS count FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.pull_request_id WHERE pull_requests.base_repo_id = :repoid AND pull_request_history.action = 'merged'[[ AND pull_request_history.actor_id = :userid]] GROUP BY DATE(created_at)) AS pulls
            ON DATE(pulls.created_at) = DATE(coms.created_at)

            LEFT JOIN (SELECT issues.created_at AS created_at, COUNT(*) AS count FROM issues WHERE issues.repo_id = :repoid[[ AND issues.reporter_id = :userid]] GROUP BY DATE(created_at)) AS iss
            ON DATE(iss.created_at) = DATE(coms.created_at)

            LEFT JOIN (SELECT commit_comments.created_at AS created_at, COUNT(*) AS count FROM commit_comments JOIN project_commits ON project_commits.commit_id = commit_comments.commit_id WHERE project_commits.project_id = :repoid[[ AND commit_comments.user_id = :userid]] GROUP BY DATE(commit_comments.created_at)) AS comcoms
            ON DATE(comcoms.created_at) = DATE(coms.created_at)

            LEFT JOIN (SELECT pull_request_comments.created_at AS created_at, COUNT(*) AS count FROM pull_request_comments JOIN pull_requests ON pull_request_comments.pull_request_id = pull_requests.id WHERE pull_requests.base_repo_id = :repoid[[ AND pull_request_comments.user_id = :userid]] GROUP BY DATE(pull_request_comments.created_at)) AS pullscoms
            ON DATE(pullscoms.created_at) = DATE(coms.created_at)

            LEFT JOIN (SELECT issue_comments.created_at AS created_at, COUNT(*) AS count FROM issue_comments JOIN issues ON issue_comments.issue_id = issues.id WHERE issues.repo_id = :repoid[[ AND issue_comments.user_id = :userid]] GROUP BY DATE(issue_comments.created_at)) AS isscoms
            ON DATE(isscoms.created_at) = DATE(coms.created_at)

            GROUP BY YEARWEEK(coms.created_at)
            ORDER BY DATE(coms.created_at)
        """

        if (userid is not None and len(userid) > 0):
            rawContributionsSQL = rawContributionsSQL.replace('[[', '')
            rawContributionsSQL = rawContributionsSQL.replace(']]', '')
            parameterized = s.sql.text(rawContributionsSQL)
            return pd.read_sql(parameterized, self.db, params={"repoid": str(repoid), "userid": str(userid)})
        else:
            rawContributionsSQL = re.sub(r'\[\[.+?\]\]', '', rawContributionsSQL)
            parameterized = s.sql.text(rawContributionsSQL)
            return pd.read_sql(parameterized, self.db, params={"repoid": str(repoid)})

    def classify_contributors(self, owner, repo=None):
        """
        Classify everyone who has interacted with a repo into
          - user
          - tester
          - rejected_contributor
          - contributor
          - major_contributor
          - maintainer

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the login and role of contributors
        """
        repoid = self.repoid(owner, repo)
        contributors = self.contributors(repoid, repo=None)
        sums = contributors.sum()

        def classify(row):
            role = 'user'
            ratio = row / sums
            if (ratio['issue_comments'] > 0.05):
                role = 'tester'
            if (row['pull_requests'] >= 1 and row['commits'] == 0):
                role = 'rejected_contributor'
            if (row['pull_requests'] >= 1 and row['commits'] >= 1):
                role = 'contributor'
            if (ratio['pull_requests'] > 0.10 or ratio['commits'] > 0.01):
                role = 'major_contributor'
            if (ratio['commits'] > 0.02 or ratio['pull_request_comments'] > 0.15):
                role = 'maintainer'

            return pd.Series({'user': row['user'], 'role': role})

        roles = contributors.apply(classify, axis=1)
        return roles

    def project_age(self, owner, repo=None):
        repoid = self.repoid(owner, repo)
        projectAgeSQL = s.sql.text("""
            SELECT date(created_at) AS "date", COUNT(*) AS "{0}"
                FROM projects
                WHERE id = :repoid
                GROUP BY YEARWEEK(created_at)
                """)
        return pd.read_sql(projectAgeSQL, self.db, params={"repoid": str(repoid)})

    def community_age(self, owner, repo=None):
        """
        Information helpful to determining a community's age

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the first event of each type (commits, fork, ...)
        """
        repoid = self.repoid(owner, repo)
        communityAgeSQL = s.sql.text("""
        SELECT DATE(proj.created_at) AS "project",
               DATE(commits.created_at) AS "commit",
               DATE(frk.created_at) AS "fork",
               DATE(iss.created_at) AS "issue",
               DATE(pr.created_at) AS "pull_request"

        FROM commits

        LEFT JOIN (SELECT forked_from_id AS "repo_id", created_at AS "created_at" FROM forks WHERE forks.forked_from_id = :repoid ORDER BY created_at DESC LIMIT 1) AS frk
        ON frk.repo_id = commits.project_id

        LEFT JOIN (SELECT repo_id AS "repo_id", created_at AS "created_at" FROM issues WHERE issues.repo_id = :repoid ORDER BY created_at DESC LIMIT 1) AS iss
        ON iss.repo_id = commits.project_id

        LEFT JOIN (SELECT pull_request_history.created_at AS "created_at", pull_requests.base_repo_id AS "repo_id" FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.pull_request_id WHERE pull_requests.base_repo_id = :repoid AND pull_request_history.action = 'merged' ORDER BY pull_request_history.created_at DESC LIMIT 1) AS pr
        ON pr.repo_id = commits.project_id

        LEFT JOIN (SELECT projects.id AS "repo_id", created_at AS "created_at" FROM projects WHERE projects.id = :repoid) AS proj
        ON proj.repo_id = commits.project_id

        WHERE commits.project_id = :repoid
        ORDER BY commits.created_at DESC
        LIMIT 1
        """)

        return pd.read_sql(communityAgeSQL, self.db, params={"repoid": str(repoid)})

    def community_engagement(self, owner, repo):
        """
        Lots of information about issues and pull requests

        TODO: More documentation

        :param owner: The name of the project owner
        :param repo: The name of the repo
        :return: DataFrame with each row being a week
        """
        repoid = self.repoid(owner, repo)
        issuesFullSQL = s.sql.text("""
        SELECT DATE(date) as "date", 
               SUM(issues_opened) AS "issues_opened",
               SUM(issues_closed) AS "issues_closed",
               SUM(pull_requests_opened) AS "pull_requests_opened",
               SUM(pull_requests_merged) AS "pull_requests_merged",
               SUM(pull_requests_closed) AS "pull_requests_closed"

        FROM (

            SELECT issue_events.created_at as "date", 
                   issue_events.action = "closed" AND issues.pull_request = 0  AS issues_closed,
                   0 AS pull_requests_closed,
                   0 AS pull_requests_merged,
                   issue_events.action = "reopened" AND issues.pull_request = 0 AS issues_opened,
                   0 AS pull_requests_opened
            FROM issues
            LEFT JOIN issue_events
            ON issue_events.issue_id = issues.id
            LEFT JOIN pull_request_history
            ON pull_request_history.pull_request_id = issues.pull_request_id
            WHERE issues.repo_id = :repoid

            UNION ALL

            SELECT pull_request_history.created_at as "date", 
                   0 AS issues_closed,
                   pull_request_history.action = "closed" AND issues.pull_request = 1  AS pull_requests_closed,
                   pull_request_history.action = "merged" AND issues.pull_request = 1   AS pull_requests_merged,
                   0 AS issues_opened,
                   pull_request_history.action = "reopened" AND issues.pull_request = 1 AS pull_requests_opened
            FROM issues
            LEFT JOIN pull_request_history
            ON pull_request_history.pull_request_id = issues.pull_request_id
            WHERE issues.repo_id = :repoid

            UNION ALL

            SELECT issues.created_at as "date",
                   0 AS issues_closed,
                   0 AS pull_requests_closed,
                   0 AS pull_requests_merged,
                   issues.pull_request = 0 AS issues_opened,
                   issues.pull_request AS pull_requests_opened
                   
            FROM issues
            WHERE issues.repo_id = :repoid

        ) summary

        GROUP BY YEARWEEK(date)
        """)
        counts = pd.read_sql(issuesFullSQL, self.db, params={"repoid": str(repoid)})
        # counts.drop(0, inplace=True)
        counts['issues_opened_total'] = counts.issues_opened.cumsum()
        counts['issues_closed_total'] = counts.issues_closed.cumsum()
        counts['issues_closed_rate_this_window'] = counts.issues_closed / counts.issues_opened
        counts['issues_closed_rate_total'] = counts.issues_closed_total / counts.issues_opened_total
        counts['issues_delta'] = counts.issues_opened - counts.issues_closed
        counts['issues_open'] = counts['issues_delta'].cumsum()
        counts['pull_requests_opened_total'] = counts.pull_requests_opened.cumsum()
        counts['pull_requests_closed_total'] = counts.pull_requests_closed.cumsum()
        counts['pull_requests_closed_rate_this_window'] = counts.pull_requests_closed / counts.pull_requests_opened
        counts['pull_requests_closed_rate_total'] = counts.pull_requests_closed_total / counts.pull_requests_opened_total
        counts['pull_requests_delta'] = counts.pull_requests_opened - counts.pull_requests_closed
        counts['pull_requests_open'] = counts['pull_requests_delta'].cumsum()
        return counts

    def contributors(self, owner, repo=None):        
        """
        augur-metric: contributors

        All the contributors to a project and the counts of their contributions

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with users id, users login, and their contributions by type
        """
        repoid = self.repoid(owner, repo)
        contributorsSQL = s.sql.text("""
            SELECT id AS user, SUM(commits) AS commits, SUM(issues) AS issues,
                               SUM(commit_comments) AS commit_comments, SUM(issue_comments) AS issue_comments,
                               SUM(pull_requests) AS pull_requests, SUM(pull_request_comments) AS pull_request_comments,
                  SUM(a.commits + a.issues + a.commit_comments + a.issue_comments + a.pull_requests + a.pull_request_comments) AS total
            FROM
            (
               (SELECT committer_id AS id, COUNT(*) AS commits, 0 AS issues, 0 AS commit_comments, 0 AS issue_comments, 0 AS pull_requests, 0 AS pull_request_comments FROM commits INNER JOIN project_commits ON project_commits.commit_id = commits.id WHERE project_commits.project_id = :repoid GROUP BY commits.committer_id)
               UNION ALL
               (SELECT reporter_id AS id, 0 AS commits, COUNT(*) AS issues, 0 AS commit_comments, 0 AS issue_comments, 0, 0 FROM issues WHERE issues.repo_id = :repoid GROUP BY issues.reporter_id)
               UNION ALL
               (SELECT commit_comments.user_id AS id, 0 AS commits, 0 AS commit_comments, COUNT(*) AS commit_comments, 0 AS issue_comments, 0 , 0 FROM commit_comments JOIN project_commits ON project_commits.commit_id = commit_comments.commit_id WHERE project_commits.project_id = :repoid GROUP BY commit_comments.user_id)
               UNION ALL
               (SELECT issue_comments.user_id AS id, 0 AS commits, 0 AS commit_comments, 0 AS issue_comments, COUNT(*) AS issue_comments, 0, 0 FROM issue_comments JOIN issues ON issue_comments.issue_id = issues.id WHERE issues.repo_id = :repoid GROUP BY issue_comments.user_id)
               UNION ALL
               (SELECT actor_id AS id, 0, 0, 0, 0, COUNT(*) AS pull_requests, 0 FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.id WHERE pull_request_history.action = 'opened' AND pull_requests.`base_repo_id` = 1334 GROUP BY actor_id)
               UNION ALL
               (SELECT user_id AS id, 0, 0, 0, 0, 0, COUNT(*) AS pull_request_comments FROM pull_request_comments JOIN pull_requests ON pull_requests.base_commit_id = pull_request_comments.commit_id WHERE pull_requests.base_repo_id = 1334 GROUP BY user_id)
            ) a
            WHERE id IS NOT NULL
            GROUP BY id
            ORDER BY total DESC;
        """)
        return pd.read_sql(contributorsSQL, self.db, params={"repoid": str(repoid)})


    # OTHER

    def fakes(self, owner, repo=None):
        """
        augur-metric: fakes
        """
        repoid = self.repoid(owner, repo)
        contributorsSQL = s.sql.text("""
            SELECT date(created_at) AS "date", COUNT(*) AS fakes
            FROM users
            WHERE fake = true
            GROUP BY YEARWEEK(date)
        """)    
        return pd.read_sql(contributorsSQL, self.db, params={"repoid": str(repoid)})



    def ghtorrent_range(self):
        ghtorrentRangeSQL = s.sql.text("""
        SELECT MIN(date(created_at)) AS "min_date", MAX(date(created_at)) AS "max_date" 
        FROM commits
        """)
        return pd.read_sql(ghtorrentRangeSQL, self.db)
