#SPDX-License-Identifier: MIT
import pandas as pd
import sqlalchemy as s
import numpy as np
import re

class GHTorrent(object):
    """Uses GHTorrent and other GitHub data sources and returns dataframes with interesting GitHub indicators"""

    def __init__(self, dbstr):
        """
        Connect to GHTorrent

        :param dbstr: The [database string](http://docs.sqlalchemy.org/en/latest/core/engines.html) to connect to the GHTorrent database
        """
        self.DB_STR = dbstr
        self.db = s.create_engine(dbstr)
        try:
            self.userid('howderek')
        except Exception as e:
            g("Could not connect to database.\nError: " + str(e))

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


    # Basic timeseries queries
    def stargazers(self, owner, repo=None, group_by="week"):
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

    def commits(self, owner, repo=None, group_by="week"):
        """
        Timeseries of all the commits on a repo

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with commits/day
        """
        repoid = self.repoid(owner, repo)
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits', group_by=group_by))
        return pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})

    def forks(self, owner, repo=None, group_by="week"):
        """
        Timeseries of when a repo's forks were created

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with forks/day
        """
        repoid = self.repoid(owner, repo)
        forksSQL = s.sql.text(self.__single_table_count_by_date('projects', 'forked_from', 'owner_id', group_by=group_by))
        return pd.read_sql(forksSQL, self.db, params={"repoid": str(repoid)}).drop(0)

    def issues(self, owner, repo=None, group_by="week"):
        """
        Timeseries of when people starred a repo

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with issues/day
        """
        repoid = self.repoid(owner, repo)
        issuesSQL = s.sql.text(self.__single_table_count_by_date('issues', 'repo_id', 'reporter_id', group_by=group_by))
        return pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})

    def issues_with_close(self, owner, repo=None):
        """
        How long on average each week it takes to close an issue

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with issues/day
        """
        repoid = self.repoid(owner, repo)
        issuesSQL = s.sql.text("""
            SELECT issues.id as "id",
                   issues.created_at as "date",
                   DATEDIFF(closed.created_at, issues.created_at)  AS "days_to_close"
            FROM issues

           JOIN
                (SELECT * FROM issue_events
                 WHERE issue_events.action = "closed") closed
            ON issues.id = closed.issue_id

            WHERE issues.repo_id = :repoid""")
        return pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})

    def pulls(self, owner, repo=None):
        """
        Timeseries of pull requests creation, also gives their associated activity

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with pull requests by day
        """
        repoid = self.repoid(owner, repo)
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

    def contributors(self, owner, repo=None):
        """
        All the contributors to a project and the counts of their contributions

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with users id, users login, and their contributions by type
        """
        repoid = self.repoid(owner, repo)
        print(repoid)
        contributorsSQL = s.sql.text("""
            SELECT * FROM

               (
               SELECT   users.id        as "user_id",
                        users.login     as "login",
                        users.location  as "location",
                        com.count       as "commits",
                        pulls.count     as "pull_requests",
                        iss.count       as "issues",
                        comcoms.count   as "commit_comments",
                        pullscoms.count as "pull_request_comments",
                        isscoms.count   as "issue_comments",
                        com.count + pulls.count + iss.count + comcoms.count + pullscoms.count + isscoms.count as "total"

               FROM users

               LEFT JOIN (SELECT committer_id AS id, COUNT(*) AS count FROM commits INNER JOIN project_commits ON project_commits.commit_id = commits.id WHERE project_commits.project_id = :repoid GROUP BY commits.committer_id) AS com
               ON com.id = users.id

               LEFT JOIN (SELECT pull_request_history.actor_id AS id, COUNT(*) AS count FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.pull_request_id WHERE pull_requests.base_repo_id = :repoid AND pull_request_history.action = 'merged' GROUP BY pull_request_history.actor_id) AS pulls
               ON pulls.id = users.id

               LEFT JOIN (SELECT reporter_id AS id, COUNT(*) AS count FROM issues WHERE issues.repo_id = :repoid GROUP BY issues.reporter_id) AS iss
               ON iss.id = users.id

               LEFT JOIN (SELECT commit_comments.user_id AS id, COUNT(*) AS count FROM commit_comments JOIN project_commits ON project_commits.commit_id = commit_comments.commit_id WHERE project_commits.project_id = :repoid GROUP BY commit_comments.user_id) AS comcoms
               ON comcoms.id = users.id

               LEFT JOIN (SELECT pull_request_comments.user_id AS id, COUNT(*) AS count FROM pull_request_comments JOIN pull_requests ON pull_request_comments.pull_request_id = pull_requests.id WHERE pull_requests.base_repo_id = :repoid GROUP BY pull_request_comments.user_id) AS pullscoms
               ON pullscoms.id = users.id

               LEFT JOIN (SELECT issue_comments.user_id AS id, COUNT(*) AS count FROM issue_comments JOIN issues ON issue_comments.issue_id = issues.id WHERE issues.repo_id = :repoid GROUP BY issue_comments.user_id) AS isscoms
               ON isscoms.id = users.id

               GROUP BY users.id
               ORDER BY com.count DESC
               ) user_activity

            WHERE commits IS NOT NULL
            OR    pull_requests IS NOT NULL
            OR    issues IS NOT NULL
            OR    commit_comments IS NOT NULL
            OR    pull_request_comments IS NOT NULL
            OR    issue_comments IS NOT NULL;
        """)
        return pd.read_sql(contributorsSQL, self.db, index_col=['user_id'], params={"repoid": str(repoid)})


    def contributions(self, owner, repo=None, userid=None):
        """
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

    def committer_locations(self, owner, repo):
        """
        Return committers and their locations

        @todo: Group by country code instead of users, needs the new schema

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo.
        :return: DataFrame with users and locations sorted by commtis
        """
        repoid = self.repoid(owner, repo)
        rawContributionsSQL = s.sql.text("""
            SELECT users.login, users.location, users.long, users.lat, users.country_code, COUNT(*) AS "commits"
            FROM commits
            JOIN project_commits
            ON commits.id = project_commits.commit_id
            JOIN users
            ON users.id = commits.author_id
            WHERE project_commits.project_id = :repoid
            AND users.country_code IS NOT NULL
            GROUP BY users.id
            ORDER BY commits DESC
        """)
        return pd.read_sql(rawContributionsSQL, self.db, params={"repoid": str(repoid)})


    def issue_response_time(self, owner, repo=None):
        """
        How long it takes for issues to be responded to by people who have commits associate with the project

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the issues' id the date it was
                 opened, and the date it was first responded to
        """
        repoid = self.repoid(owner, repo)
        issuesSQL = s.sql.text("""
            SELECT issues.created_at               AS "created_at",
                   MIN(issue_comments.created_at)  AS "responded_at"
            FROM issues
            JOIN issue_comments
            ON issue_comments.issue_id = issues.id
            WHERE issue_comments.user_id IN
                (SELECT users.id
                FROM users
                JOIN commits
                WHERE commits.author_id = users.id
                AND commits.project_id = :repoid)
            AND issues.repo_id = :repoid
            GROUP BY issues.id
        """)
        df = pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['responded_at'] = pd.to_datetime(df['responded_at'])
        df['hours_between'] = np.floor((df['responded_at'] - df['created_at']) / np.timedelta64(1, 'h'))
        df = df['hours_between'].value_counts().sort_index().reset_index().rename(columns={'index': 'hours_between', 'hours_between': 'count'})
        df = df[df['hours_between'] < 48]
        return df

    def pull_acceptance_rate(self, owner, repo=None):
        """
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

            return pd.Series({'login': row['login'], 'role': role})

        roles = contributors.apply(classify, axis=1)
        return roles

    def community_age(self, owner, repo=None):
        """
        Information helpful to determining a community's age

        For now, returns the date of the first of each type of action (fork, pull request, etc.)
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

    def unique_committers(self, owner, repo=None):
        repoid = self.repoid(owner, repo)
        uniqueCommittersSQL = s.sql.text("""
        SELECT unique_committers.created_at AS "date", MAX(@number_of_committers:=@number_of_committers+1) total_unique_committers
        FROM (
            SELECT author_id, MIN(DATE(created_at)) created_at
            FROM commits
            WHERE project_id = :repoid
            GROUP BY author_id
            ORDER BY created_at ASC) AS unique_committers,
        (SELECT @number_of_committers:= 0) AS number_of_committers
        GROUP BY DATE(unique_committers.created_at)
        """)
        return pd.read_sql(uniqueCommittersSQL, self.db, params={"repoid": str(repoid)})

    def ghtorrent_range(self):
        ghtorrentRangeSQL = s.sql.text("""
        SELECT MIN(date(created_at)) AS "min_date", MAX(date(created_at)) AS "max_date" 
        FROM commits
        """)
        return pd.read_sql(ghtorrentRangeSQL, self.db)
