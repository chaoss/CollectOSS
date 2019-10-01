import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import logger, annotate, add_metrics

@annotate(tag='contributors')
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

@annotate(tag='contributors-new')
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
            SELECT date_trunc(:period, b.created_at::DATE) AS contribute_at, COUNT(id) AS count, repo.repo_id, repo_name
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
            GROUP BY contribute_at, repo.repo_id, repo_name
            """)

        results = pd.read_sql(contributorsNewSQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                   'begin_date': begin_date, 'end_date': end_date})
    else:
        contributorsNewSQL = s.sql.text("""
            SELECT date_trunc(:period, b.created_at::DATE) AS contribute_at, COUNT(id) AS count, repo.repo_id, repo_name
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
            GROUP BY contribute_at, repo.repo_id, repo_name
            """)

        results = pd.read_sql(contributorsNewSQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                   'begin_date': begin_date, 'end_date': end_date})
    return results
    
@annotate(tag='lines-changed-by-author')
def lines_changed_by_author(self, repo_group_id, repo_id=None):
    """
    Returns number of lines changed per author per day

    :param repo_url: the repository's URL
    """

    if repo_id:
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, cmt_author_date, cmt_author_affiliation as affiliation,
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace, repo_name
            FROM commits JOIN repo ON commits.repo_id = repo.repo_id
            WHERE commits.repo_id = :repo_id
            GROUP BY commits.repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email, repo_name
            ORDER BY cmt_author_date ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.database, params={"repo_id": repo_id})
        return results
    else:
        linesChangedByAuthorSQL = s.sql.text("""
            SELECT cmt_author_email, cmt_author_date, cmt_author_affiliation as affiliation,
                SUM(cmt_added) as additions, SUM(cmt_removed) as deletions, SUM(cmt_whitespace) as whitespace
            FROM commits
            WHERE repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
            GROUP BY repo_id, cmt_author_date, cmt_author_affiliation, cmt_author_email
            ORDER BY cmt_author_date ASC;
        """)
        results = pd.read_sql(linesChangedByAuthorSQL, self.database, params={"repo_group_id": repo_group_id})
        return results

@annotate(tag='top-committers')
def top_committers(self, repo_group_id, repo_id=None, year=None, threshold=0.5):
    """
    Returns a list of contributors contributing N% of all commits.

    :param repo_group_id: Repo group ID
    :param repo_id: Repo ID.
    :param year: Year. eg: 2018, 2107. Defaults to current year.
    :param threshold: The threshold to specify N%. Defaults to 0.5
    """
    threshold = float(threshold)
    if threshold < 0 or threshold > 1:
        raise ValueError('threshold should be between 0 and 1')

    if year is None:
        year = datetime.datetime.now().year

    if not repo_id:
        total_commits_SQL = s.sql.text("""
            SELECT SUM(patches)::int
            FROM
                (SELECT repo_group_id, email, year, patches
                FROM dm_repo_group_annual
                WHERE year = :year AND repo_group_id = :repo_group_id
                ORDER BY patches DESC) a
        """)

        results = pd.read_sql(total_commits_SQL, self.database,
                            params={'year': year, 'repo_group_id': repo_group_id})
    else:
        total_commits_SQL = s.sql.text("""
            SELECT SUM(patches)::int
            FROM
                (SELECT repo_id, email, year, patches
                FROM dm_repo_annual
                WHERE year = :year AND repo_id = :repo_id
                ORDER BY patches DESC) a
        """)

        results = pd.read_sql(total_commits_SQL, self.database,
                            params={'year': year, 'repo_id': repo_id})

    total_commits = int(results.iloc[0]['sum'])
    threshold_commits = round(threshold * total_commits)

    if not repo_id:
        committers_SQL = s.sql.text("""
            SELECT
                a.repo_group_id,
                rg_name AS repo_group_name,
                a.email,
                SUM(a.patches)::int AS commits
            FROM
                (SELECT repo_group_id, email, year, patches
                FROM dm_repo_group_annual
                WHERE year = :year AND repo_group_id = :repo_group_id
                ORDER BY patches DESC) a, repo_groups
            WHERE a.repo_group_id = repo_groups.repo_group_id
            GROUP BY a.repo_group_id, repo_group_name, a.email
            ORDER BY commits DESC
        """)

        results = pd.read_sql(committers_SQL, self.database,
                            params={'year': year, 'repo_group_id': repo_group_id})
    else:
        committers_SQL = s.sql.text("""
            SELECT
                a.repo_id,
                repo.repo_name,
                a.email,
                SUM(a.patches)::int AS commits
            FROM
                (SELECT repo_id, email, year, patches
                FROM dm_repo_annual
                WHERE year = :year AND repo_id = :repo_id
                ORDER BY patches DESC) a, repo
            WHERE a.repo_id = repo.repo_id
            GROUP BY a.repo_id, repo.repo_name, a.email
            ORDER BY commits DESC
        """)

        results = pd.read_sql(committers_SQL, self.database,
                              params={'year': year, 'repo_id': repo_id})

    cumsum = 0
    for i, row in results.iterrows():
        cumsum += row['commits']
        if cumsum >= threshold_commits:
            results = results[:i + 1]
            break

    if not repo_id:
        rg_name = results.iloc[0]['repo_group_name']
        results.loc[i+1] = [repo_group_id, rg_name, 'other_contributors',
                            int(total_commits - cumsum)]
    else:
        repo_name = results.iloc[0]['repo_name']
        results.loc[i+1] = [repo_id, repo_name, 'other_contributors',
                            int(total_commits - cumsum)]

    return results

def create_contributor_metrics(metrics):
    add_metrics(metrics, __name__)

