#SPDX-License-Identifier: MIT
"""
Data source that uses the GHTorrent relational database of GitHub activity. 
"""

import pandas as pd
import sqlalchemy as s
import numpy as np
import re
from augur import logger
from augur.util import annotate

class GHTorrent(object):
    """Uses the GHTorrent database to return dataframes with interesting GitHub indicators"""

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
                SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", {2} AS "user_id"
                FROM {0}
                WHERE {1} = :repoid
                """.format(table, repo_col, user_col)

        if group_by == "day":
            return """
                SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY DATE(created_at)
                ORDER BY DATE(created_at) DESC""".format(table, repo_col)

        if group_by == "week":
            return """
                SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY YEARWEEK(created_at)
                ORDER BY DATE(created_at) DESC""".format(table, repo_col)

        if group_by == "month":
            return """
                SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY MONTH(created_at), YEAR(created_at)
                ORDER BY DATE(created_at) DESC""".format(table, repo_col)

        if group_by == "year":
            return """
                SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS "{0}"
                FROM {0}
                WHERE {1} = :repoid
                GROUP BY YEAR(created_at)
                ORDER BY DATE(created_at) DESC""".format(table, repo_col)

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
            SELECT date({1}.created_at) AS "date", COUNT(*) AS {1}
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

    @annotate(tag='code-commits')
    def code_commits(self, owner, repo=None, group_by="week"):        
        """
        Timeseries of the count of commits

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new commits/week
        """
        repoid = self.repoid(owner, repo)
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits', group_by=group_by))
        return pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='code-review-iteration')
    def code_review_iteration(self, owner, repo=None):
        """
        Timeseries of the count of iterations (being closed and reopened) that a merge request (code review) goes through until it is finally merged

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with iterations/issue for each issue that week
        """
        repoid = self.repoid(owner, repo)

        codeReviewIterationSQL = s.sql.text("""
        SELECT
            DATE(issues.created_at) AS "created_at",
            DATE(pull_request_history.created_at) AS "merged_at",
            issues.issue_id AS "issue_id",
            pull_request_history.pull_request_id AS "pull_request_id",
            pull_request_history.action AS "action",
            COUNT(CASE WHEN action = "closed" THEN 1 ELSE NULL END) AS "iterations"
        FROM issues, pull_request_history
        WHERE find_in_set(pull_request_history.action, "closed,merged")>0
        AND pull_request_history.pull_request_id IN(
            SELECT pull_request_id
            FROM pull_request_history
            WHERE pull_request_history.action = "closed")   #go by reopened or closed??? (min: completed 1 iteration and has started another OR min: completed 1 iteration)
        AND pull_request_history.pull_request_id = issues.issue_id
        AND issues.pull_request = 1
        AND issues.repo_id = :repoid
        GROUP BY YEARWEEK(issues.created_at) #YEARWEEK to get (iterations (all PRs in repo) / week) instead of (iterations / PR)?
        """)

        df = pd.read_sql(codeReviewIterationSQL, self.db, params={"repoid": str(repoid)})
        return pd.DataFrame({'date': df['created_at'], 'iterations': df['iterations']})

    @annotate(tag='contribution-acceptance')
    def contribution_acceptance(self, owner, repo=None):
        """
        Timeseries of the rolling ratio between merged pull requests over unmerged pull requests

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with ratio/week
        """
        source_df = self.community_engagement(owner, repo)
        df = pd.DataFrame()
        df['date'] = source_df['date']
        df['acceptance_rate'] = source_df['pull_requests_merged_rate_this_week']
        return df

    @annotate(tag='contributing-github-organizations')
    def contributing_github_organizations(self, owner, repo=None): #needs clarification about return value
        """
        Returns of all the contributing organizations to a project and the counts of each organization's contributions

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with each organization's information
        """
        repoid = self.repoid(owner, repo)
        contributingOrgSQL = s.sql.text("""
            SELECT id AS contributing_org, SUM(commits) AS commits, SUM(issues) AS issues,
                               SUM(commit_comments) AS commit_comments, SUM(issue_comments) AS issue_comments,
                               SUM(pull_requests) AS pull_requests, SUM(pull_request_comments) AS pull_request_comments,
                  SUM(contribution_fields.commits + contribution_fields.issues + contribution_fields.commit_comments + contribution_fields.issue_comments + contribution_fields.pull_requests + contribution_fields.pull_request_comments) AS total, COUNT(DISTINCT contribution_fields.user) AS distinct_users
            FROM
            (
                (SELECT organization_members.org_id AS id, commits.author_id AS user, COUNT(*) AS commits, 0 AS issues, 0 AS commit_comments, 0 AS issue_comments, 0 AS pull_requests, 0 AS pull_request_comments FROM organization_members, projects, commits
                    WHERE projects.id = :repoid
                    AND commits.project_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND commits.author_id = organization_members.user_id GROUP BY commits.committer_id)
                UNION ALL
                (SELECT organization_members.org_id AS id, reporter_id AS user, 0 AS commits, COUNT(*) AS issues, 0 AS commit_comments, 0 AS issue_comments, 0, 0 FROM organization_members, projects, issues
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND pull_request = 0
                    AND projects.owner_id <> organization_members.org_id
                    AND reporter_id = organization_members.user_id GROUP BY issues.reporter_id)
                UNION ALL
                (SELECT organization_members.org_id AS id, commit_comments.user_id AS user, 0 AS commits, 0 AS commit_comments, COUNT(*) AS commit_comments, 0 AS issue_comments, 0 , 0 FROM organization_members, projects, commit_comments JOIN commits ON commits.id = commit_comments.commit_id
                    WHERE projects.id = :repoid
                    AND commits.project_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND commit_comments.user_id = organization_members.user_id GROUP BY commit_comments.user_id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, issue_comments.user_id AS user, 0 AS commits, 0 AS commit_comments, 0 AS commit_comments, COUNT(*) AS issue_comments, 0 , 0 FROM organization_members, projects, issue_comments JOIN issues ON issues.id = issue_comments.issue_id
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND issue_comments.user_id = organization_members.user_id GROUP BY id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, reporter_id AS user, 0, 0, 0, 0, COUNT(*) AS pull_requests, 0 FROM organization_members, projects, issues
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND pull_request = 1
                    AND projects.owner_id <> organization_members.org_id
                    AND reporter_id = organization_members.user_id GROUP BY issues.reporter_id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, pull_request_comments.user_id AS user, 0, 0, 0, 0, 0, COUNT(*) AS pull_request_comments FROM organization_members, projects, pull_request_comments JOIN pull_requests ON pull_requests.base_commit_id = pull_request_comments.commit_id
                    WHERE pull_requests.base_repo_id = :repoid
                    AND projects.id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND pull_request_comments.user_id = organization_members.user_id GROUP BY pull_request_comments.user_id)
            ) contribution_fields
            group by id
            having distinct_users > 1
            ORDER BY total DESC
        """)
        return pd.read_sql(contributingOrgSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='first-response-to-issue-duration')
    def first_response_to_issue_duration(self, owner, repo): #needs clarification about return value
        """
        Timeseries of the time to first comment by issue

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame of issues with their response information
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

    @annotate(tag='forks')
    def forks(self, owner, repo=None, group_by="week"): 
        """
        
        Timeseries of when a repo's forks were created

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new forks/week
        """
        repoid = self.repoid(owner, repo)
        forksSQL = s.sql.text(self.__single_table_count_by_date('projects', 'forked_from', 'owner_id', group_by=group_by))
        return pd.read_sql(forksSQL, self.db, params={"repoid": str(repoid)}).drop(0)

    @annotate(tag='maintainer-response-to-merge-request-duration')
    def maintainer_response_to_merge_request_duration(self, owner, repo=None): #needs clarification on return value
        """
        Timeseries of duration of time between a merge request being created and a maintainer commenting on that request

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with each row being a week
        """
        repoid = self.repoid(owner, repo)
        maintainerResponseToMRSQL = s.sql.text("""
            SELECT DATE(issues.created_at) AS date, TIMESTAMPDIFF(DAY, issues.created_at, pull_request_comments.created_at) as days, pull_request_comments.created_at AS pull_request_comment_created_at, issues.id AS issue_id, pull_request_comments.user_id AS user_id, pull_request_comments.comment_id as pull_request_comment_id
            FROM issues
            JOIN pull_request_comments
            ON issues.pull_request_id = pull_request_comments.pull_request_id
            JOIN
                (SELECT DISTINCT actor_id
                FROM pull_request_history
                JOIN pull_requests
                ON pull_request_history.pull_request_id = pull_requests.pullreq_id
                WHERE action = "merged"
                AND base_repo_id = :repoid
                ORDER BY actor_id) a
            ON a.actor_id = user_id
            WHERE issues.pull_request = 1
            AND issues.repo_id = :repoid
            GROUP BY YEARWEEK(date)
            """)
        df = pd.read_sql(maintainerResponseToMRSQL, self.db, params={"repoid": str(repoid)})
        return df.iloc[:, 0:2]

    @annotate(tag='new-contributing-github-organizations')
    def new_contributing_github_organizations(self, owner, repo=None): #needs clarification about return value
        """
        Timeseries of information about new contributing organizations on a certain date

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with each organization's information
        """
        repoid = self.repoid(owner, repo)

        contributingOrgSQL = s.sql.text("""
        SELECT
            SUBDATE(DATE(fields.date), WEEKDAY(DATE(fields.date))) AS "date",
            fields.id AS "contributing_org",
            count(DISTINCT fields.user) AS distinct_users
        FROM (
                (SELECT organization_members.org_id AS id, commits.created_at AS date, commits.author_id AS user FROM organization_members, projects, commits
                    WHERE projects.id = :repoid
                    AND commits.project_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND commits.author_id = organization_members.user_id GROUP BY commits.committer_id)
                UNION ALL
                (SELECT organization_members.org_id AS id, issues.created_at AS date, issues.reporter_id AS user FROM organization_members, projects, issues
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND pull_request = 0
                    AND projects.owner_id <> organization_members.org_id
                    AND reporter_id = organization_members.user_id GROUP BY issues.reporter_id)
                UNION ALL
                (SELECT organization_members.org_id AS id, commit_comments.created_at AS date, commit_comments.user_id as user FROM organization_members, projects, commit_comments JOIN commits ON commits.id = commit_comments.commit_id
                    WHERE projects.id = :repoid
                    AND commits.project_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND commit_comments.user_id = organization_members.user_id GROUP BY commit_comments.user_id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, issue_comments.created_at AS date, issue_comments.user_id AS user FROM organization_members, projects, issue_comments JOIN issues ON issues.id = issue_comments.issue_id
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND issue_comments.user_id = organization_members.user_id GROUP BY id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, issues.created_at AS date, issues.reporter_id AS user FROM organization_members, projects, issues
                    WHERE projects.id = :repoid
                    AND issues.repo_id = :repoid
                    AND pull_request = 1
                    AND projects.owner_id <> organization_members.org_id
                    AND reporter_id = organization_members.user_id GROUP BY issues.reporter_id)
                 UNION ALL
                 (SELECT organization_members.org_id AS id, pull_request_comments.created_at AS date, pull_request_comments.user_id AS user FROM organization_members, projects, pull_request_comments JOIN pull_requests ON pull_requests.base_commit_id = pull_request_comments.commit_id
                    WHERE pull_requests.base_repo_id = :repoid
                    AND projects.id = :repoid
                    AND projects.owner_id <> organization_members.org_id
                    AND pull_request_comments.user_id = organization_members.user_id GROUP BY pull_request_comments.user_id)) fields

        Group BY contributing_org
        HAVING distinct_users > 1
        ORDER BY YEARWEEK(date)
        """)
        df = pd.read_sql(contributingOrgSQL, self.db, params={"repoid": str(repoid)})
        numOrgs = []
        count = 0
        for index, row in df.iterrows():
            count += 1
            numOrgs = np.append(numOrgs, count)
        return pd.DataFrame({'date': df["date"], 'organizations': numOrgs})

    @annotate(tag='open-issues')
    def open_issues(self, owner, repo=None, group_by="week"):
        """
        Timeseries of the count of newly issues opened per week

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with opened issues/week
        """
        repoid = self.repoid(owner, repo)
        issuesSQL = s.sql.text(self.__single_table_count_by_date('issues', 'repo_id', 'reporter_id', group_by=group_by))
        return pd.read_sql(issuesSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='pull-request-comments')
    def pull_request_comments(self, owner, repo=None):
        """
        Timeseries of the count of new pull request comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new pull request comments/week
        """
        repoid = self.repoid(owner, repo)
        pullRequestCommentsSQL = s.sql.text(self.__sub_table_count_by_date("pull_requests", "pull_request_comments", "pullreq_id", "pull_request_id", "base_repo_id"))
        return pd.read_sql(pullRequestCommentsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='pull-requests-open')
    def pull_requests_open(self, owner, repo=None):
        """
        Timeseries of pull requests creation and their associated activity

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with pull request information/week
        """
        repoid = self.repoid(owner, repo)
        pullsSQL = s.sql.text("""
            SELECT SUBDATE(DATE(pull_request_history.created_at), WEEKDAY(DATE(pull_request_history.created_at))) AS "date",
            COUNT(pull_requests.id) AS "pull_requests"
            FROM pull_request_history
            INNER JOIN pull_requests
            ON pull_request_history.pull_request_id = pull_requests.id
            WHERE pull_requests.head_repo_id = :repoid
            AND pull_request_history.action = "merged"
            GROUP BY YEARWEEK(DATE(pull_request_history.created_at))
        """)
        return pd.read_sql(pullsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='pull-requests-closed')
    def pull_requests_closed(self, owner, repo=None):
        """
        Timeseries of pull requests closed and their associated activity

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.

        :return: DataFrame with closed pull request information/week
        """
        repoid = self.repoid(owner, repo)
        pullsSQL = s.sql.text("""
            SELECT SUBDATE(DATE(pull_request_history.created_at), WEEKDAY(DATE(pull_request_history.created_at))) AS "date",
            COUNT(pull_requests.id) AS "pull_requests"
            FROM pull_request_history
            INNER JOIN pull_requests
            ON pull_request_history.pull_request_id = pull_requests.id
            WHERE pull_requests.head_repo_id = :repoid
            AND pull_request_history.action = "closed"
            GROUP BY YEARWEEK(DATE(pull_request_history.created_at))
        """)
        return pd.read_sql(pullsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='pull-request-comment-duration')
    def pull_request_comment_duration(self, owner, repo=None):
        """
        Timeseries of the time to recentt comment by pull requests

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame of pull requests with their response information
        """
        repoid = self.repoid(owner, repo)
        durationSQL = s.sql.text("""
        SELECT
            pull_request_history.id AS "pull_request_id" ,
            pull_request_history.created_at AS "opened" ,
            MIN( pull_request_comments.created_at ) AS "first_pr_comment",
            TIMESTAMPDIFF( MINUTE ,
            pull_request_history.created_at ,
            MIN( pull_request_comments.created_at )) AS "minutes_to_first_pr_comment" ,
            MIN( pull_request_comments.created_at ) AS "most_recent_comment",
            TIMESTAMPDIFF( MINUTE ,
            pull_request_history.created_at ,
            MAX( pull_request_comments.created_at )) AS "minutes_to_recent_pr_comment" 
        FROM
            pull_request_history
        JOIN pull_requests ON pull_request_history.pull_request_id = pull_requests.id
        JOIN pull_request_comments ON pull_request_comments.pull_request_id = pull_requests.id
        WHERE
            pull_requests.base_repo_id = :repoid  AND pull_request_history.action = 'opened'
        GROUP BY
            pull_request_history.id ,
            pull_requests.base_repo_id ,
            pull_request_history.created_at
        ORDER BY
            pull_request_history.created_at
        """)

        return pd.read_sql(durationSQL, self.db, params={"repoid": str(repoid)})

    #####################################
    ###            RISK               ###
    #####################################


    #####################################
    ###            VALUE              ###
    #####################################


    #####################################
    ###           ACTIVITY            ###
    #####################################

    @annotate(tag='issue-comments')
    def issue_comments(self, owner, repo=None):
        """
        Timeseries of the count of new issue comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new issue comments/week
        """
        repoid = self.repoid(owner, repo)
        issueCommentsSQL = s.sql.text(self.__sub_table_count_by_date("issues", "issue_comments", "issue_id", "issue_id", "repo_id"))
        return pd.read_sql(issueCommentsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='pull-requests-made-closed')
    def pull_requests_made_closed(self, owner, repo=None):
        """
        Timeseries of the ratio of pull requests made/closed

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the ratio of pull requests made/closed
        """
        repoid = self.repoid(owner, repo)
        pullRequestsMadeClosedSQL = s.sql.text("""
        SELECT DATE(closed_on) AS "date", CAST(num_opened AS DECIMAL)/CAST(num_closed AS DECIMAL) AS "rate"
                FROM
                    (SELECT COUNT(DISTINCT pull_request_id) AS num_opened, DATE(pull_request_history.created_at) AS opened_on
                    FROM pull_request_history
                    JOIN pull_requests ON pull_request_history.pull_request_id = pull_requests.id
                    WHERE action = 'opened' AND pull_requests.base_repo_id = :repoid
                    GROUP BY opened_on) opened
                JOIN
                    (SELECT count(distinct pull_request_id) AS num_closed, DATE(pull_request_history.created_at) AS closed_on
                    FROM pull_request_history
                    JOIN pull_requests ON pull_request_history.pull_request_id = pull_requests.id
                    WHERE action = 'closed'
                    AND pull_requests.base_repo_id = :repoid
                    GROUP BY closed_on) closed
                ON closed.closed_on = opened.opened_on
        """)
        return pd.read_sql(pullRequestsMadeClosedSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='watchers')
    def watchers(self, owner, repo=None, group_by="week"):
        """
        Returns of the count of people who starred the repo on that date

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new stargazers
        """
        repoid = self.repoid(owner, repo)
        stargazersSQL = s.sql.text(self.__single_table_count_by_date('watchers', 'repo_id', 'user_id', group_by=group_by))
        df = pd.read_sql(stargazersSQL, self.db, params={"repoid": str(repoid)})
        df.drop(df.index[:1], inplace=True)
        return df

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    # COMMIT RELATED
    @annotate(tag='commits100')
    def commits100(self, owner, repo=None, group_by="week"):
        """
        Timeseries of the count of commits, limited to the first 100 overall

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with commits/day
        """
        repoid = self.repoid(owner, repo)
        commitsSQL = s.sql.text(self.__single_table_count_by_date('commits', group_by=group_by))
        temp = pd.read_sql(commitsSQL, self.db, params={"repoid": str(repoid)})
        tem = temp['commits'] > 100
        return temp[tem].reset_index(drop=True)

    @annotate(tag='commit-comments')
    def commit_comments(self, owner, repo=None, group_by="week"):
        """
        Timeseries of the count of new commit comments

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new by week
        """
        repoid = self.repoid(owner, repo)
        commitCommentsSQL = s.sql.text(self.__sub_table_count_by_date("commits", "commit_comments", "id", "commit_id", "project_id"))
        return pd.read_sql(commitCommentsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='committer-locations')
    def committer_locations(self, owner, repo=None):
        """
        Returns committers and their locations


        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo.
        :return: DataFrame with users and locations sorted by descending count of commits
        """
        #TODO: Group by country code instead of users, needs the new schema
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

    @annotate(tag='total-committers')
    def total_committers(self, owner, repo=None):
        """
        Timeseries of total committers as of each week

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with total committers/week
        """
        repoid = self.repoid(owner, repo)
        totalCommittersSQL = s.sql.text("""
        SELECT total_committers.created_at AS "date", COUNT(total_committers.author_id) total_committers
        FROM (
            SELECT author_id, MIN(DATE(created_at)) created_at
            FROM commits
            WHERE project_id = :repoid
            GROUP BY author_id
            ORDER BY created_at ASC) AS total_committers
        GROUP BY YEARWEEK(total_committers.created_at)
        """)
        df = pd.read_sql(totalCommittersSQL, self.db, params={"repoid": str(repoid)})
        df['total_committers'] = df['total_committers'].cumsum()
        return df

    # ISSUE RELATED
    @annotate(tag='issue-activity')
    def issue_activity(self, owner, repo=None):
        """
        Timeseries of issue related activity: issues opened, closed, reopened, and currently open

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with total committers/week
        """
        repoid = self.repoid(owner, repo)
        issueActivity = s.sql.text("""
            SELECT Date(issues.created_at) as 'date', COUNT(issues.id) as 'issues_opened', SUM(CASE WHEN issue_events.action = 'closed' THEN 1 ELSE 0 END) as 'issues_closed', SUM(CASE WHEN issue_events.action = 'reopened' THEN 1 ELSE 0 END) as 'issues_reopened'
                FROM issues
                JOIN issue_events ON issues.id = issue_events.issue_id
                WHERE issues.repo_id = :repoid
                GROUP BY YEARWEEK(issues.created_at)
            """)
        #TODO: clean this up
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
    @annotate(tag='pull-request-acceptance-rate')
    def pull_request_acceptance_rate(self, owner, repo=None):
        """
        Timeseries of pull request acceptance rate (expressed as the ratio of pull requests merged on a date to the count of pull requests opened on a date)

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with ratio/day
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
        df = pd.read_sql(pullAcceptanceSQL, self.db, params={"repoid": str(repoid)})
        print(df)
        return df

    # COMMUNITY / CONRIBUTIONS
    @annotate(tag='community-age')
    def community_age(self, owner, repo=None):
        """
        Information helpful to determining a community's age

        (Currently broken)

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

        LEFT JOIN (SELECT forked_from AS "repo_id", created_at AS "created_at" FROM projects WHERE projects.forked_from = :repoid ORDER BY created_at DESC LIMIT 1) AS frk
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

    @annotate(tag='community-engagement')
    def community_engagement(self, owner, repo):
        """
        Timeseries with lots of information about issues and pull requests

        DataFrame returns these columns:
        date
        issues_opened
        issues_closed
        pull_requests_opened
        pull_requests_merged
        pull_requests_closed
        issues_opened_total
        issues_closed_total
        issues_closed_rate_this_window
        issues_closed_rate_total
        issues_delta
        issues_open
        pull_requests_opened_total
        pull_requests_closed_total
        pull_requests_closed_rate_this_window
        pull_requests_closed_rate_total
        pull_requests_delta
        pull_requests

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the associated information about a repo's activity on that specific date
        """
        repoid = self.repoid(owner, repo)
        issuesFullSQL = s.sql.text("""
        SELECT STR_TO_DATE(CONCAT(YEARWEEK(DATE,0),' Sunday'), '%X%V %W') as "date",
               SUM(issues_opened) AS "issues_opened",
               SUM(issues_closed) AS "issues_closed",
               SUM(pull_requests_opened) AS "pull_requests_opened",
               SUM(pull_requests_merged) AS "pull_requests_merged",
               SUM(pull_requests_closed) AS "pull_requests_closed"

        FROM (

            SELECT  STR_TO_DATE(CONCAT(YEARWEEK(issue_events.created_at,0),' Sunday'), '%X%V %W') as "date",
                   issue_events.action = "closed" AND issues.pull_request = 0   AS issues_closed,
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
            AND issue_events.action IN ('closed', 'reopened')

            UNION ALL

            SELECT STR_TO_DATE(CONCAT(YEARWEEK(pull_request_history.created_at,0),' Sunday'), '%X%V %W') as "date",
                   0 AS issues_closed,
                   pull_request_history.action = "closed" AND issues.pull_request = 1   AS pull_requests_closed,
                   pull_request_history.action = "merged" AND issues.pull_request = 1   AS pull_requests_merged,
                   0 AS issues_opened,
                   pull_request_history.action = "reopened" AND issues.pull_request = 1 AS pull_requests_opened
            FROM issues
            LEFT JOIN pull_request_history
            ON pull_request_history.pull_request_id = issues.pull_request_id
            WHERE issues.repo_id = :repoid
            AND pull_request_history.action IN ('closed', 'merged', 'reopened')

            UNION ALL

            SELECT STR_TO_DATE(CONCAT(YEARWEEK(issues.created_at ,0),' Sunday'), '%X%V %W') as "date",
                   0 AS issues_closed,
                   0 AS pull_requests_closed,
                   0 AS pull_requests_merged,
                   issues.pull_request = 0 AS issues_opened,
                   issues.pull_request AS pull_requests_opened

            FROM issues
            WHERE issues.repo_id = :repoid

        ) summary

        GROUP BY YEARWEEK(date, 1)


        """)
        counts = pd.read_sql(issuesFullSQL, self.db, params={"repoid": str(repoid)})
        counts.drop(0, inplace=True)
        counts['issues_opened_total'] = counts.issues_opened.cumsum()
        counts['issues_closed_total'] = counts.issues_closed.cumsum()
        counts['issues_closed_rate_this_week'] = counts.issues_closed / counts.issues_opened
        counts['issues_closed_rate_total'] = counts.issues_closed_total / counts.issues_opened_total
        counts['issues_delta'] = counts.issues_opened - counts.issues_closed
        counts['issues_open'] = counts['issues_delta'].cumsum()
        counts['pull_requests_opened_total'] = counts.pull_requests_opened.cumsum()
        counts['pull_requests_closed_total'] = counts.pull_requests_closed.cumsum()
        counts['pull_requests_merged_total'] = counts.pull_requests_merged.cumsum()
        counts['pull_requests_closed_rate_this_week'] = counts.pull_requests_closed / counts.pull_requests_opened
        counts['pull_requests_merged_rate_this_week'] = counts.pull_requests_merged / counts.pull_requests_opened
        counts['pull_requests_closed_rate_total'] = counts.pull_requests_closed_total / counts.pull_requests_opened_total
        counts['pull_requests_merged_rate_total'] = counts.pull_requests_merged_total / counts.pull_requests_opened_total
        counts['pull_requests_delta'] = counts.pull_requests_opened - counts.pull_requests_closed
        counts['pull_requests_open'] = counts['pull_requests_delta'].cumsum()
        return counts

    @annotate(tag='contributors')
    def contributors(self, owner, repo=None):
        """
        All the contributors to a project and the counts of their contributions

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with user's id and contributions by type, separated by user
        """
        repoid = self.repoid(owner, repo)
        contributorsSQL = s.sql.text("""
            SELECT users.login as name, a.id AS user, SUM(commits) AS commits, SUM(issues) AS issues,
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
               (SELECT actor_id AS id, 0, 0, 0, 0, COUNT(*) AS pull_requests, 0 FROM pull_request_history JOIN pull_requests ON pull_requests.id = pull_request_history.id WHERE pull_request_history.action = 'opened' AND pull_requests.`base_repo_id` = :repoid GROUP BY actor_id)
               UNION ALL
               (SELECT user_id AS id, 0, 0, 0, 0, 0, COUNT(*) AS pull_request_comments FROM pull_request_comments JOIN pull_requests ON pull_requests.base_commit_id = pull_request_comments.commit_id WHERE pull_requests.base_repo_id = :repoid GROUP BY user_id)
            ) a JOIN users ON users.id = a.id
            WHERE a.id IS NOT NULL
            GROUP BY a.id
            ORDER BY total DESC;
        """)
        return pd.read_sql(contributorsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='contributions')
    def contributions(self, owner, repo=None, userid=None):
        """
        Timeseries of all the contributions to a project, optionally limited to a specific user

        DataFrame has these columns:
        date
        commits
        pull_requests
        issues
        commit_comments
        pull_request_comments
        issue_comments
        tota

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :param userid: The id of user if you want to limit the contributions to a specific user.
        :return: DataFrame with all of the contributions separated by day
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
        :return: DataFrame with the id and role of contributors
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

    @annotate(tag='project-age')
    def project_age(self, owner, repo=None):
        """
        Date of the project's creation

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with the date of the project's creation
        """
        repoid = self.repoid(owner, repo)
        projectAgeSQL = s.sql.text("""
            SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS "{0}"
                FROM projects
                WHERE id = :repoid
                GROUP BY YEARWEEK(created_at)
                """)
        return pd.read_sql(projectAgeSQL, self.db, params={"repoid": str(repoid)})

    # DEPENDENCY RELATED

    # OTHER
    @annotate(tag='fakes')
    def fakes(self, owner, repo=None): #should this be for users who contribute to the given repo?
        """
        Timeseries of new fake users per week

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new fake users/week
        """
        repoid = self.repoid(owner, repo)
        contributorsSQL = s.sql.text("""
            SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) AS "date", COUNT(*) AS fakes
            FROM users
            WHERE fake = true
            GROUP BY YEARWEEK(date)
        """)
        return pd.read_sql(contributorsSQL, self.db, params={"repoid": str(repoid)})

    @annotate(tag='total-watchers')
    def total_watchers(self, owner, repo=None):
        """
        Timeseries of total watchers as of each week
            
        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with total watchers/week
        """
        
        repoid = self.repoid(owner, repo)
        totalWatchersSQL = s.sql.text("""
            SELECT total_watchers.created_at AS "date", COUNT(total_watchers.user_id) total_watchers
            FROM (
                SELECT user_id, MIN(DATE(created_at)) created_at
                FROM watchers
                WHERE repo_id = :repoid
                GROUP BY user_id
                ORDER BY created_at ASC) AS total_watchers
            GROUP BY YEARWEEK(total_watchers.created_at)
        """)
        df = pd.read_sql(totalWatchersSQL, self.db, params={"repoid": str(repoid)})
        df['total_watchers'] = df['total_watchers'].cumsum()
        return df
    
    @annotate(tag='new-watchers')
    def new_watchers(self, owner, repo=None): 
        """
        Timeseries of new watchers per week

        :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table.
        :param repo: The name of the repo. Unneeded if repository id was passed as owner.
        :return: DataFrame with new watchers/week
        """
        repoid = self.repoid(owner, repo)
        newWatchersSQL = s.sql.text("""
            SELECT SUBDATE(DATE(created_at), WEEKDAY(DATE(created_at))) as "date", COUNT(*) as "watchers"
            FROM watchers
            WHERE repo_id = :repoid
            GROUP BY YEARWEEK(created_at)
        """)
        return pd.read_sql(newWatchersSQL, self.db, params={"repoid": str(repoid)})



    ### Utility
    def user(self, user_id):
        usersSQL = s.sql.text("""
            SELECT *
            FROM users
            WHERE id = :user_id
        """)
        return pd.read_sql(usersSQL, self.db, params={"user_id": int(user_id)})
