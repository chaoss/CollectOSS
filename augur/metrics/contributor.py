#SPDX-License-Identifier: MIT
"""
Metrics that provides data about contributors & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def contributors(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a timeseries of all the contributions to a project.

    DataFrame has these columns:
    date
    commits
    pull_requests
    issues
    commit_comments
    pull_request_comments
    issue_comments
    total

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    # In this version, pull request, pr request comments,issue comments haven't be calculated
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        contributorsSQL = s.sql.text("""
           SELECT id                           AS user_id,
                SUM(commits)                 AS commits,
                SUM(issues)                  AS issues,
                SUM(commit_comments)         AS commit_comments,
                SUM(issue_comments)          AS issue_comments,
                SUM(pull_requests)           AS pull_requests,
                SUM(pull_request_comments)   AS pull_request_comments,
                SUM(a.commits + a.issues + a.commit_comments + a.issue_comments + a.pull_requests +
                    a.pull_request_comments) AS total,
                a.repo_id, repo.repo_name
            FROM (
                    (SELECT gh_user_id AS id,
                            0          AS commits,
                            COUNT(*)   AS issues,
                            0          AS commit_comments,
                            0          AS issue_comments,
                            0          AS pull_requests,
                            0          AS pull_request_comments,
                            repo_id
                    FROM issues
                    WHERE repo_id = :repo_id
                        AND created_at BETWEEN :begin_date AND :end_date
                        AND gh_user_id IS NOT NULL
                        AND pull_request IS NULL
                    GROUP BY gh_user_id, repo_id)
                    UNION ALL
                    (SELECT cmt_ght_author_id AS id,
                            COUNT(*)          AS commits,
                            0                 AS issues,
                            0                 AS commit_comments,
                            0                 AS issue_comments,
                            0                 AS pull_requests,
                            0                 AS pull_request_comments,
                            repo_id
                    FROM commits
                    WHERE repo_id = :repo_id
                        AND cmt_ght_author_id IS NOT NULL
                        AND cmt_committer_date BETWEEN :begin_date AND :end_date
                    GROUP BY cmt_ght_author_id, repo_id)
                    UNION ALL
                    (SELECT cntrb_id AS id,
                            0        AS commits,
                            0        AS issues,
                            COUNT(*) AS commit_comments,
                            0        AS issue_comments,
                            0        AS pull_requests,
                            0        AS pull_request_comments,
                            repo_id
                    FROM commit_comment_ref,
                        commits,
                        message
                    WHERE commit_comment_ref.cmt_id = commit_comment_ref.cmt_id
                        AND message.msg_id = commit_comment_ref.msg_id
                        AND repo_id = :repo_id
                        AND created_at BETWEEN :begin_date AND :end_date
                    GROUP BY id, repo_id)
                    UNION ALL
                    (
                        SELECT message.cntrb_id AS id,
                                0                AS commits,
                                0                AS issues,
                                0                AS commit_comments,
                                count(*)         AS issue_comments,
                                0                AS pull_requests,
                                0                AS pull_request_comments,
                            repo_id
                        FROM issues,
                            issue_message_ref,
                            message
                        WHERE repo_id = :repo_id
                        AND gh_user_id IS NOT NULL
                        AND issues.issue_id = issue_message_ref.issue_id
                        AND issue_message_ref.msg_id = message.msg_id
                        AND issues.pull_request IS NULL
                        AND created_at BETWEEN :begin_date AND :end_date
                        GROUP BY id, repo_id
                    )
                ) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY a.id, a.repo_id, repo_name
            ORDER BY total DESC
        """)

        results = pd.read_sql(contributorsSQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
    else:
        contributorsSQL = s.sql.text("""
           SELECT id                           AS user_id,
                SUM(commits)                 AS commits,
                SUM(issues)                  AS issues,
                SUM(commit_comments)         AS commit_comments,
                SUM(issue_comments)          AS issue_comments,
                SUM(pull_requests)           AS pull_requests,
                SUM(pull_request_comments)   AS pull_request_comments,
                SUM(a.commits + a.issues + a.commit_comments + a.issue_comments + a.pull_requests +
                    a.pull_request_comments) AS total, a.repo_id, repo_name
            FROM (
                    (SELECT gh_user_id AS id,
                            repo_id,
                            0          AS commits,
                            COUNT(*)   AS issues,
                            0          AS commit_comments,
                            0          AS issue_comments,
                            0          AS pull_requests,
                            0          AS pull_request_comments
                    FROM issues
                    WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                        AND created_at BETWEEN :begin_date AND :end_date
                        AND gh_user_id IS NOT NULL
                        AND pull_request IS NULL
                    GROUP BY gh_user_id, repo_id)
                    UNION ALL
                    (SELECT cmt_ght_author_id AS id,
                            repo_id,
                            COUNT(*)          AS commits,
                            0                 AS issues,
                            0                 AS commit_comments,
                            0                 AS issue_comments,
                            0                 AS pull_requests,
                            0                 AS pull_request_comments
                    FROM commits
                    WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                        AND cmt_ght_author_id IS NOT NULL
                        AND cmt_committer_date BETWEEN :begin_date AND :end_date
                    GROUP BY cmt_ght_author_id, repo_id)
                    UNION ALL
                    (SELECT cntrb_id AS id,
                            repo_id,
                            0        AS commits,
                            0        AS issues,
                            COUNT(*) AS commit_comments,
                            0        AS issue_comments,
                            0        AS pull_requests,
                            0        AS pull_request_comments
                    FROM commit_comment_ref,
                        commits,
                        message
                    WHERE commit_comment_ref.cmt_id = commit_comment_ref.cmt_id
                        AND message.msg_id = commit_comment_ref.msg_id
                        AND repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                        AND created_at BETWEEN :begin_date AND :end_date
                    GROUP BY id, repo_id)
                    UNION ALL
                    (
                        SELECT message.cntrb_id AS id,
                                repo_id,
                                0                AS commits,
                                0                AS issues,
                                0                AS commit_comments,
                                count(*)         AS issue_comments,
                                0                AS pull_requests,
                                0                AS pull_request_comments
                        FROM issues,
                            issue_message_ref,
                            message
                        WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                        AND gh_user_id IS NOT NULL
                        AND issues.issue_id = issue_message_ref.issue_id
                        AND issue_message_ref.msg_id = message.msg_id
                        AND issues.pull_request IS NULL
                        AND created_at BETWEEN :begin_date AND :end_date
                        GROUP BY id, repo_id
                    )
                ) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY a.id, a.repo_id, repo_name
            ORDER BY total DESC
        """)

        results = pd.read_sql(contributorsSQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
    return results

@register_metric()
def contributors_new(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a timeseries of new contributions to a project.

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    # In this version, pull request, pr request comments,issue comments haven't be calculated
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        contributorsNewSQL = s.sql.text("""
            SELECT date_trunc(:period, b.created_at::DATE) AS date, COUNT(id) AS new_contributors, repo.repo_id, repo_name
            FROM (
                    SELECT id as id, MIN(created_at) AS created_at, a.repo_id
                    FROM (
                            (SELECT gh_user_id AS id, MIN(created_at) AS created_at, repo_id
                            FROM issues
                            WHERE repo_id = :repo_id
                                AND created_at BETWEEN :begin_date AND :end_date
                                AND gh_user_id IS NOT NULL
                                AND pull_request IS NULL
                            GROUP BY gh_user_id, repo_id)
                            UNION ALL
                            (SELECT cmt_ght_author_id                                AS id,
                                    MIN(TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD')) AS created_at,
                                    repo_id
                            FROM commits
                            WHERE repo_id = :repo_id
                                AND cmt_ght_author_id IS NOT NULL
                                AND TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD') BETWEEN :begin_date AND :end_date
                            GROUP BY cmt_ght_author_id, repo_id)
                            UNION ALL
                            (SELECT cntrb_id as id, MIN(created_at) AS created_at, commits.repo_id
                            FROM commit_comment_ref,
                                    commits,
                                    message
                            where commits.cmt_id = commit_comment_ref.cmt_id
                                and commits.repo_id = :repo_id
                                and commit_comment_ref.msg_id = message.msg_id
                            group by id, commits.repo_id)
                            UNION ALL
                            (SELECT issue_events.cntrb_id AS id, MIN(issue_events.created_at) AS created_at, repo_id
                            FROM issue_events, issues
                            WHERE issues.repo_id = :repo_id
                                AND issues.issue_id = issue_events.issue_id
                                AND issues.pull_request IS NULL
                                AND issue_events.created_at BETWEEN :begin_date AND :end_date
                                AND issue_events.cntrb_id IS NOT NULL
                                AND action = 'closed'
                            GROUP BY issue_events.cntrb_id, repo_id)
                        ) a
                    GROUP BY a.id, a.repo_id) b, repo
            WHERE repo.repo_id = b.repo_id
            GROUP BY date, repo.repo_id, repo_name
            """)

        results = pd.read_sql(contributorsNewSQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                   'begin_date': begin_date, 'end_date': end_date})
    else:
        contributorsNewSQL = s.sql.text("""
            SELECT date_trunc(:period, b.created_at::DATE) AS date, COUNT(id) AS new_contributors, repo.repo_id, repo_name
            FROM (
                    SELECT id as id, MIN(created_at) AS created_at, a.repo_id
                    FROM (
                            (SELECT gh_user_id AS id, MIN(created_at) AS created_at, repo_id
                            FROM issues
                            WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                                AND created_at BETWEEN :begin_date AND :end_date
                                AND gh_user_id IS NOT NULL
                                AND pull_request IS NULL
                            GROUP BY gh_user_id, repo_id)
                            UNION ALL
                            (SELECT cmt_ght_author_id                                AS id,
                                    MIN(TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD')) AS created_at,
                                    repo_id
                            FROM commits
                            WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                                AND cmt_ght_author_id IS NOT NULL
                                AND TO_TIMESTAMP(cmt_author_date, 'YYYY-MM-DD') BETWEEN :begin_date AND :end_date
                            GROUP BY cmt_ght_author_id, repo_id)
                            UNION ALL
                            (SELECT cntrb_id as id, MIN(created_at) AS created_at, commits.repo_id
                            FROM commit_comment_ref,
                                    commits,
                                    message
                            where commits.cmt_id = commit_comment_ref.cmt_id
                                and commits.repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                                and commit_comment_ref.msg_id = message.msg_id
                            group by id, commits.repo_id)
                            UNION ALL
                            (SELECT issue_events.cntrb_id AS id, MIN(issue_events.created_at) AS created_at, repo_id
                            FROM issue_events, issues
                            WHERE issues.repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                                AND issues.issue_id = issue_events.issue_id
                                AND issues.pull_request IS NULL
                                AND issue_events.created_at BETWEEN :begin_date AND :end_date
                                AND issue_events.cntrb_id IS NOT NULL
                                AND action = 'closed'
                            GROUP BY issue_events.cntrb_id, repo_id)
                        ) a
                    GROUP BY a.id, a.repo_id) b, repo
            WHERE repo.repo_id = b.repo_id
            GROUP BY date, repo.repo_id, repo_name
            """)

        results = pd.read_sql(contributorsNewSQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                   'begin_date': begin_date, 'end_date': end_date})
    return results
    
@register_metric()
def lines_changed_by_author(self, repo_group_id, repo_id=None):
    """
    Returns number of lines changed per author per day

    :param repo_url: the repository's URL
    """

    if repo_id:
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, date_trunc('week', cmt_author_date::date) as cmt_author_date, cmt_author_affiliation as affiliation,
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace, repo_name
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id = :repo_id
            GROUP BY commits.repo_id, date_trunc('week', cmt_author_date::date), cmt_author_affiliation, cmt_author_email, repo_name
            ORDER BY date_trunc('week', cmt_author_date::date) ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.database, params={"repo_id": repo_id})
        return results
    else:
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, date_trunc('week', cmt_author_date::date) as cmt_author_date, cmt_author_affiliation as affiliation,
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace
            FROM commits
            WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
            GROUP BY repo_id, date_trunc('week', cmt_author_date::date), cmt_author_affiliation, cmt_author_email
            ORDER BY date_trunc('week', cmt_author_date::date) ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.database, params={"repo_group_id": repo_group_id})
        return results

@register_metric()
def contributors_code_development(self, repo_group_id, repo_id=None, period='all', begin_date=None, end_date=None):
    """
    Returns a timeseries of all the contributions to a project.

    DataFrame has these columns:
    date
    commits

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
  -----  :param period: To set the periodicity to 'all', day', 'week', 'month' or 'year', defaults to 'all'
  -----  :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
  -----  :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    # In this version, pull request, pr request comments,issue comments haven't be calculated
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        contributorsSQL = s.sql.text("""
            SELECT 
                email                        AS email,
                SUM(commits)                 AS commits,
                SUM(lines_added)                   AS lines_added,
                a.repo_id, repo.repo_name
            FROM (
                    (
                    SELECT repo_id, email, SUM(patches)::int as commits, 0 as lines_added
                    FROM
                        (SELECT repo_id, email, patches
                        FROM dm_repo_annual
                        WHERE repo_id = :repo_id
                        ORDER BY patches DESC) a
                    GROUP BY email, a.repo_id
                    )
                    UNION ALL
                    (
                    SELECT repo_id, cmt_author_email as email, 0 as commits, SUM(cmt_added) as lines_added
                    -- cmt_author_affiliation as affiliation,
                        -- SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace, 
                    FROM commits
                    WHERE commits.repo_id = :repo_id
                    GROUP BY commits.repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email
                    ORDER BY cmt_author_date ASC
                    )
                ) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY a.email, a.repo_id, repo_name
        """)

        results = pd.read_sql(contributorsSQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
    else:
        contributorsSQL = s.sql.text("""
            SELECT 
                email                        AS email,
                SUM(commits)                 AS commits,
                SUM(lines_added)                   AS lines_added,
                a.repo_id, repo.repo_name
            FROM (
                    (
                    SELECT repo_id, email, SUM(patches)::INT AS commits, 0 AS lines_added
                    FROM
                        (SELECT dm_repo_annual.repo_id, email, patches
                        FROM dm_repo_annual JOIN repo ON repo.repo_id = dm_repo_annual.repo_id
                        WHERE repo_group_id = :repo_group_id
                        ORDER BY patches DESC) a
                    GROUP BY email, a.repo_id
                    )
                    UNION ALL
                    (
                    SELECT commits.repo_id, cmt_author_email AS email, 0 AS commits, SUM(cmt_added) AS lines_added
                    -- cmt_author_affiliation as affiliation,
                        -- SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace, 
                    FROM commits JOIN repo ON repo.repo_id = commits.repo_id
                    WHERE repo_group_id = :repo_group_id
                    GROUP BY commits.repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email
                    ORDER BY cmt_author_date ASC
                    )
                ) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY  a.email, a.repo_id, repo_name
            ORDER BY commits desc, email
        """)

        results = pd.read_sql(contributorsSQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
    return results
