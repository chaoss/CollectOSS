#SPDX-License-Identifier: MIT
"""
Metrics that provides data about issues & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from augur.util import register_metric

@register_metric()
def issues_first_time_opened(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Returns a timeseries of the count of persons opening an issue for the first time.

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        issueNewContributor = s.sql.text("""
            SELECT
                date_trunc(:period, new_date::DATE) as issue_date,
                COUNT(gh_user_id),
                repo_name
            FROM (
                SELECT
                    gh_user_id,
                    MIN(issues.created_at) AS new_date,
                    repo_name
                FROM
                    issues JOIN repo ON issues.repo_id = repo.repo_id
                WHERE
                    issues.repo_id = :repo_id
                    AND issues.pull_request IS NULL
                    AND issues.created_at BETWEEN :begin_date AND :end_date
                GROUP BY gh_user_id, repo_name
            ) as abc
            GROUP BY issue_date, repo_name
            ORDER BY issue_date
        """)
        results = pd.read_sql(issueNewContributor, self.database, params={'repo_id': repo_id, 'period': period,
                                                                    'begin_date': begin_date, 'end_date': end_date})
    else:
        issueNewContributor = s.sql.text("""
            SELECT
                repo.repo_id,
                repo_name,
                date_trunc(:period, new_date::DATE) as issue_date,
                COUNT(gh_user_id)
            FROM (
                SELECT
                    repo_id,
                    gh_user_id,
                    MIN(created_at) AS new_date
                FROM
                    issues
                WHERE
                    issues.pull_request IS NULL 
                    AND repo_id in (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                    AND created_at BETWEEN :begin_date AND :end_date
                GROUP BY gh_user_id, repo_id
            ) as abc, repo
            WHERE repo.repo_id= abc.repo_id
            GROUP BY repo.repo_id, issue_date
            ORDER BY issue_date
        """)
        results = pd.read_sql(issueNewContributor, self.database,
                              params={'repo_group_id': repo_group_id, 'period': period,
                                      'begin_date': begin_date, 'end_date': end_date})
    return results

@register_metric()
def issues_first_time_closed(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None, ):
    """
    Returns a timeseries of the count of persons closing an issue for the first time.

    :param repo_id: The repository's id
    :param repo_group_id: The repository's group id
    :param period: To set the periodicity to 'day', 'week', 'month', or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of persons/period
    """

    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if repo_id:
        issuesClosedSQL = s.sql.text("""
            SELECT date_trunc(:period, new_date::DATE) AS issue_date,
                COUNT(cntrb_id),
                repo_name
            FROM (
                    SELECT issue_events.cntrb_id, MIN(issue_events.created_at) AS new_date, repo_name
                    FROM issue_events,
                        repo,
                        issues
                    WHERE repo.repo_id = :repo_id
                    AND action = 'closed'
                    AND repo.repo_id = issues.repo_id
                    AND issues.pull_request IS NULL 
                    AND issues.issue_id = issue_events.issue_id
                    And issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY issue_events.cntrb_id, repo_name
                ) AS iss_close
            GROUP BY issue_date, repo_name
        """)
        results = pd.read_sql(issuesClosedSQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
    else:
        issuesClosedSQL = s.sql.text("""
             SELECT date_trunc(:period, new_date::DATE) AS issue_date,
                COUNT(cntrb_id),
                repo_name, repo_id
            FROM (
                    SELECT issue_events.cntrb_id, MIN(issue_events.created_at) AS new_date, repo_name, repo.repo_id
                    FROM issue_events,
                        repo,
                        issues
                    WHERE repo.repo_group_id = :repo_group_id
                    AND issues.pull_request IS NULL 
                    AND action = 'closed'
                    AND repo.repo_id = issues.repo_id
                    AND issues.issue_id = issue_events.issue_id
                    And issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY issue_events.cntrb_id, repo.repo_id, repo_name
                ) AS iss_close
            GROUP BY repo_id, repo_name,issue_date
        """)
        results = pd.read_sql(issuesClosedSQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})

    return results

@register_metric()
def issues_new(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of new issues opened.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of new issues/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    issues_new_SQL = ''

    if not repo_id:
        issues_new_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, issues.created_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_new_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                               'begin_date': begin_date, 'end_date': end_date})

        return results

    else:
        issues_new_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, issues.created_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY date, repo_name
            ORDER BY date;
        """)

        results = pd.read_sql(issues_new_SQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                               'begin_date': begin_date, 'end_date': end_date})
        return results

@register_metric()
def issues_active(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of issues active.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of issues active/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not repo_id:
        issues_active_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, issue_events.created_at) as date,
                COUNT(issues.issue_id) AS issues
            FROM issues, repo, issue_events
            WHERE issues.issue_id = issue_events.issue_id
            AND issues.repo_id = repo.repo_id
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND issue_events.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            and issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_active_SQL, self.database, params={'repo_group_id': repo_group_id, 'period':period,
                                                                  'begin_date': begin_date, 'end_date':end_date})
        return results

    else:
        issues_active_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, issue_events.created_at) as date,
                COUNT(issues.issue_id) AS issues
            FROM issues, repo, issue_events
            WHERE issues.issue_id = issue_events.issue_id
            AND issues.repo_id = repo.repo_id
            AND issues.repo_id = :repo_id
            AND issue_events.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY date, repo_name
            ORDER BY date
        """)

        results = pd.read_sql(issues_active_SQL, self.database, params={'repo_id': repo_id, 'period':period,
                                                                  'begin_date': begin_date, 'end_date':end_date})
        return results

@register_metric()
def issues_closed(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """Returns a timeseries of issues closed.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of issues closed/period
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not repo_id:
        issues_closed_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, closed_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND closed_at IS NOT NULL
            AND closed_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_closed_SQL, self.database, params={'repo_group_id': repo_group_id, 'period': period,
                                                                   'begin_date': begin_date, 'end_date': end_date})

        return results

    else:
        issues_closed_SQL = s.sql.text("""
            SELECT
                repo_name,
                date_trunc(:period, closed_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND closed_at IS NOT NULL
            AND closed_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY date, repo_name
            ORDER BY date;
        """)

        results = pd.read_sql(issues_closed_SQL, self.database, params={'repo_id': repo_id, 'period': period,
                                                                'begin_date': begin_date, 'end_date': end_date})
        return results

@register_metric()
def issue_duration(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):
    """Returns the duration of each issue.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of issue id with the corresponding duration
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not repo_id:
        issue_duration_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                issue_id,
                issues.created_at,
                issues.closed_at,
                (issues.closed_at - issues.created_at) AS duration
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND closed_at IS NOT NULL
            AND issues.pull_request IS NULL
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY repo_id, issue_id
        """)

        results = pd.read_sql(issue_duration_SQL, self.database, params={'repo_group_id': repo_group_id,
                                                                   'begin_date': begin_date,
                                                                   'end_date': end_date})
        results['duration'] = results['duration'].astype(str)
        return results

    else:
        issue_duration_SQL = s.sql.text("""
            SELECT
                repo_name,
                issue_id,
                issues.created_at,
                issues.closed_at,
                (closed_at - issues.created_at) AS duration
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND issues.pull_request IS NULL
            AND closed_at IS NOT NULL
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY issue_id;
        """)

        results = pd.read_sql(issue_duration_SQL, self.database, params={'repo_id': repo_id,
                                                                   'begin_date': begin_date,
                                                                   'end_date': end_date})
        results['duration'] = results['duration'].astype(str)
        return results

@register_metric()
def issue_participants(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):
    """Returns number of participants per issue.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
    :param end_date: Specifies the end date, defaults to datetime.now()
    :return: DataFrame of count of participants per issue.
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:00'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not repo_id:
        issue_participants_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo.repo_name,
                derived.issue_id,
                issues.created_at,
                COUNT(DISTINCT derived.cntrb_id) AS participants
            FROM (
                (SELECT issue_id, cntrb_id FROM issues WHERE cntrb_id IS NOT NULL AND issues.pull_request IS NULL)
                UNION
                (SELECT issue_id, cntrb_id FROM issue_message_ref, message
                WHERE issue_message_ref.msg_id = message.msg_id)
            ) AS derived, issues, repo
            WHERE derived.issue_id = issues.issue_id
            AND issues.repo_id = repo.repo_id
            AND issues.pull_request IS NULL
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY issues.repo_id, repo.repo_name, derived.issue_id, issues.created_at
            ORDER BY issues.repo_id, issues.created_at
        """)

        result = pd.read_sql(issue_participants_SQL, self.database, params={'repo_group_id': repo_group_id,
                                                                      'begin_date': begin_date,
                                                                      'end_date': end_date})
        return result
    else:
        issue_participants_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                derived.issue_id,
                issues.created_at,
                COUNT(DISTINCT derived.cntrb_id) AS participants
            FROM (
                (SELECT issue_id, cntrb_id FROM issues WHERE cntrb_id IS NOT NULL AND issues.pull_request IS NULL)
                UNION
                (SELECT issue_id, cntrb_id FROM issue_message_ref, message
                WHERE issue_message_ref.msg_id = message.msg_id)
            ) AS derived, issues, repo
            WHERE derived.issue_id = issues.issue_id
            AND issues.repo_id = repo.repo_id
            AND issues.pull_request IS NULL
            AND issues.repo_id = :repo_id
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY repo_name, derived.issue_id, issues.created_at
            ORDER BY issues.created_at
        """)

        result = pd.read_sql(issue_participants_SQL, self.database, params={'repo_id': repo_id,
                                                                      'begin_date': begin_date,
                                                                      'end_date': end_date})
        return result

@register_metric()
def issue_backlog(self, repo_group_id, repo_id=None):
    """Returns number of issues currently open.

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: DataFrame of count of issues currently open.
    """
    if not repo_id:
        issue_backlog_SQL = s.sql.text("""
            SELECT issues.repo_id, repo_name, COUNT(issue_id) as issue_backlog
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id)
            AND issue_state = 'open'
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, repo_name
            ORDER BY issues.repo_id
        """)
        result = pd.read_sql(issue_backlog_SQL, self.database, params={'repo_group_id': repo_group_id})
        return result

    else:
        issue_backlog_SQL = s.sql.text("""
            SELECT repo_name, COUNT(issue_id) as issue_backlog
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND issues.pull_request IS NULL
            AND issue_state='open'
            GROUP BY repo_name
        """)

        result = pd.read_sql(issue_backlog_SQL, self.database, params={'repo_id': repo_id})
        return result

@register_metric()
def issue_throughput(self, repo_group_id, repo_id=None):
    """Returns the ratio of issues closed to total issues

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: DataFrame of ratio of issues closed to total issues.
    """
    if not repo_id:
        issue_throughput_SQL = s.sql.text("""
            SELECT table1.repo_id, repo.repo_name, (tot1 / tot2) AS throughput
            FROM
                (SELECT repo_id, COUNT(issue_id)::REAL AS tot1
                FROM issues WHERE issue_state='closed' AND issues.pull_request IS NULL
                AND repo_id IN (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id)
                GROUP BY repo_id) AS table1,
                (SELECT repo_id, COUNT(issue_id)::REAL AS tot2
                FROM issues
                WHERE repo_id IN (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id AND issues.pull_request IS NULL)
                GROUP BY repo_id) AS table2,
                repo
            WHERE table1.repo_id = table2.repo_id
            AND table1.repo_id = repo.repo_id
        """)

        results = pd.read_sql(issue_throughput_SQL, self.database, params={'repo_group_id': repo_group_id})
        return results

    else:
        issue_throughput_SQL = s.sql.text("""
            SELECT repo.repo_name, (tot1 / tot2) AS throughput
            FROM
                (SELECT repo_id, COUNT(issue_id)::REAL AS tot1 FROM issues
                WHERE issue_state='closed' AND repo_id=:repo_id AND issues.pull_request IS NULL
                GROUP BY repo_id) AS table1,
                (SELECT COUNT(issue_id)::REAL AS tot2 FROM issues
                WHERE repo_id=:repo_id AND issues.pull_request IS NULL) AS table2,
                repo
            WHERE table1.repo_id = repo.repo_id
        """)

        result = pd.read_sql(issue_throughput_SQL, self.database, params={'repo_id': repo_id})
        return result

@register_metric()
def issues_open_age(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Retrun the age of open issues

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: DataFrame of age of open issues.
    """

    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    openAgeSQL = None

    if not repo_id:
        openAgeSQL = s.sql.text("""
            SELECT  repo.repo_id, repo_name, issue_id, date_trunc(:period, issues.created_at ) as date, EXTRACT(DAY FROM NOW() - issues.created_at) AS open_date
            FROM issues,
                repo,
                repo_groups
            WHERE issue_state = 'open'
            AND issues.pull_request IS NULL
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id, repo_name, issue_id, date, open_date
            ORDER BY open_date DESC
        """)
    else:
        openAgeSQL = s.sql.text("""
            SELECT repo.repo_id, repo_name, issue_id, date_trunc(:period, issues.created_at ) as date, EXTRACT(DAY FROM NOW() - issues.created_at) AS open_date
            FROM issues,
                repo,
                repo_groups
            WHERE issue_state = 'open'
            AND issues.repo_id = :repo_id
            AND issues.pull_request IS NULL
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id,issue_id, date, open_date
            ORDER BY open_date DESC
        """)

    results = pd.read_sql(openAgeSQL, self.database,
                            params={'repo_id': repo_id, 'repo_group_id': repo_group_id,
                            'period': period, 'begin_date':begin_date, 'end_date':end_date})

    return results

@register_metric()
def issues_closed_resolution_duration(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    """
    Retrun Time duration of time for issues to be resolved

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: DataFrame of time duration of time for issues to be resolved
    """
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    issueSQL = None
    if not repo_id:
        issueSQL = s.sql.text("""
           SELECT repo.repo_id,
                repo_name,
                gh_issue_number,
                issue_title,
                date_trunc(:period, issues.created_at) as created_at,
                date_trunc(:period, issues.closed_at) as closed_at,
                EXTRACT(DAY FROM closed_at - issues.created_at) AS DIFFDATE
            FROM issues,
                repo
            WHERE issues.closed_at IS NOT NULL
            AND issues.pull_request IS NULL
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id, repo.repo_name, gh_issue_number, issue_title, issues.created_at, issues.closed_at, DIFFDATE
            ORDER BY gh_issue_number
        """)
    else:
        issueSQL = s.sql.text("""
            SELECT repo.repo_id,
                repo_name,
                gh_issue_number,
                issue_title,
                date_trunc(:period, issues.created_at) as created_at,
                date_trunc(:period, issues.closed_at) as closed_at,
                EXTRACT(DAY FROM closed_at - issues.created_at) AS DIFFDATE
            FROM issues,
                repo
            WHERE issues.closed_at IS NOT NULL
            AND issues.pull_request IS NULL
            AND issues.repo_id = :repo_id
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id, repo.repo_name, gh_issue_number, issue_title, issues.created_at, issues.closed_at, DIFFDATE
            ORDER BY gh_issue_number
        """)

    results = pd.read_sql(issueSQL, self.database,
                            params={'repo_id': repo_id,
                            'repo_group_id': repo_group_id,
                            'period': period, 'begin_date':begin_date,
                            'end_date':end_date})

    return results

@register_metric()
def average_issue_resolution_time(self, repo_group_id, repo_id=None):
    """
    Returns the average issue resolution time

    :param repo_group_id: The repository's repo_group_id
    :param repo_id: The repository's repo_id, defaults to None
    :return: Average issue resolution time
    """
    if not repo_id:
        avg_issue_resolution_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo.repo_name,
                AVG(issues.closed_at - issues.created_at)::text AS avg_issue_resolution_time
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN
                (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id)
            AND closed_at IS NOT NULL
            AND pull_request IS NULL 
            GROUP BY issues.repo_id, repo.repo_name
            ORDER BY issues.repo_id
        """)

        results = pd.read_sql(avg_issue_resolution_SQL, self.database,
                              params={'repo_group_id': repo_group_id})
        return results

    else:
        avg_issue_resolution_SQL = s.sql.text("""
            SELECT
                repo.repo_name,
                AVG(issues.closed_at - issues.created_at)::text AS avg_issue_resolution_time
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id = :repo_id
            AND closed_at IS NOT NULL
            AND pull_request IS NULL 
            GROUP BY repo.repo_name
        """)

        results = pd.read_sql(avg_issue_resolution_SQL, self.database,
                              params={'repo_id': repo_id})
        return results

@register_metric()
def issues_maintainer_response_duration(self, repo_group_id, repo_id=None, begin_date=None, end_date=None):

    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    issuesSQL = None
    if repo_id:
        issuesSQL = s.sql.text("""
            SELECT repo_id, repo_name, AVG(time_to_first_commit) as average_days_comment
            from (
                    select repo_id,
                            repo_name,
                            earliest_member_comments.issue_id                  as issue_id,
                            extract(day from first_response_time - created_at) as time_to_first_commit
                    from (
                            select issues.issue_id            as issue_id,
                                    issues.created_at          as created_at,
                                    MIN(message.msg_timestamp) as first_response_time,
                                    repo_name,
                                    repo.repo_id
                            from repo,
                                issues,
                                issue_message_ref,
                                message
                            where repo.repo_id = :repo_id
                                and repo.repo_id = issues.repo_id
                                AND issues.pull_request IS NULL
                                and issues.issue_id = issue_message_ref.issue_id
                                and issue_message_ref.msg_id = message.msg_id
                                and issues.created_at between :begin_date and :end_date
                            group by issues.issue_id, issues.created_at, repo.repo_id
                        ) as earliest_member_comments
                    group by repo_id, repo_name,issue_id, time_to_first_commit
                ) as time_to_comment
            group by repo_id, repo_name
        """)
    else:
        issuesSQL = s.sql.text("""
            SELECT repo_id, repo_name, AVG(time_to_first_commit) as average_days_comment
            from (
                    select repo_id,
                            repo_name,
                            earliest_member_comments.issue_id                  as issue_id,
                            extract(day from first_response_time - created_at) as time_to_first_commit
                    from (
                            select issues.issue_id            as issue_id,
                                    issues.created_at          as created_at,
                                    MIN(message.msg_timestamp) as first_response_time,
                                    repo_name,
                                    repo.repo_id
                            from repo,
                                issues,
                                issue_message_ref,
                                message
                            where repo.repo_id IN (SELECT repo.repo_id from repo where repo_group_id = :repo_group_id)
                                and repo.repo_id = issues.repo_id
                                AND issues.pull_request IS NULL
                                and issues.issue_id = issue_message_ref.issue_id
                                and issue_message_ref.msg_id = message.msg_id
                                and issues.created_at between :begin_date and :end_date
                            group by issues.issue_id, issues.created_at, repo.repo_id
                        ) as earliest_member_comments
                    group by repo_id, repo_name,issue_id, time_to_first_commit
                ) as time_to_comment
            group by repo_id, repo_name
        """)

    results = pd.read_sql(issuesSQL, self.database, params={'repo_id': repo_id, 'repo_group_id': repo_group_id,'begin_date': begin_date, 'end_date': end_date})

    return results

@register_metric()
def open_issues_count(self, repo_group_id, repo_id=None):
    """
    Returns number of lines changed per author per day

    :param repo_url: the repository's URL
    """
    if not repo_id:
        openIssueCountSQL = s.sql.text("""
            SELECT rg_name, count(issue_id) AS open_count, date_trunc('week', issues.created_at) AS DATE
            FROM issues, repo, repo_groups
            WHERE issue_state = 'open'
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id)
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo_groups.rg_name
            ORDER BY date
        """)
        results = pd.read_sql(openIssueCountSQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        openIssueCountSQL = s.sql.text("""
            SELECT repo.repo_id, count(issue_id) AS open_count, date_trunc('week', issues.created_at) AS DATE, repo_name
            FROM issues, repo, repo_groups
            WHERE issue_state = 'open'
            AND issues.repo_id = :repo_id
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo.repo_id
            ORDER BY date
        """)
        results = pd.read_sql(openIssueCountSQL, self.database, params={'repo_id': repo_id})
        return results


@register_metric()
def closed_issues_count(self, repo_group_id, repo_id=None):
    """
    Returns number of lines changed per author per day

    :param repo_url: the repository's URL
    """
    if not repo_id:
        closedIssueCountSQL = s.sql.text("""
            SELECT rg_name, count(issue_id) AS closed_count, date_trunc('week', issues.created_at) AS DATE
            FROM issues, repo, repo_groups
            WHERE issue_state = 'closed'
            AND issues.repo_id IN (SELECT repo_id FROM repo WHERE  repo_group_id = :repo_group_id)
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo_groups.rg_name
            ORDER BY date
        """)
        results = pd.read_sql(closedIssueCountSQL, self.database, params={'repo_group_id': repo_group_id})
        return results
    else:
        closedIssueCountSQL = s.sql.text("""
            SELECT repo.repo_id, count(issue_id) AS closed_count, date_trunc('week', issues.created_at) AS DATE, repo_name
            FROM issues, repo, repo_groups
            WHERE issue_state = 'closed'
            AND issues.repo_id = :repo_id
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo.repo_id
            ORDER BY date
        """)
        results = pd.read_sql(closedIssueCountSQL, self.database, params={'repo_id': repo_id})
        return results

@register_metric()
def issue_comments_mean(self, repo_group_id, repo_id=None, group_by='week'):
    group_by = group_by.lower()

    if not repo_id:
        if group_by == 'week':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('week', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 7.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND im.msg_id = m.msg_id
                AND i.repo_id IN
                    (SELECT repo_id FROM repo
                     WHERE  repo_group_id = :repo_group_id)
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        elif group_by == 'month':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('month', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 30.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND im.msg_id = m.msg_id
                AND i.repo_id IN
                    (SELECT repo_id FROM repo
                     WHERE  repo_group_id = :repo_group_id)
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        elif group_by == 'year':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('year', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 365.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND im.msg_id = m.msg_id
                AND i.pull_request IS NULL 
                AND i.repo_id IN
                    (SELECT repo_id FROM repo
                     WHERE  repo_group_id = :repo_group_id)
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        else:
            raise ValueError("Incorrect value for 'group_by'")

        results = pd.read_sql(issue_comments_mean_std_SQL, self.database,
                              params={'repo_group_id': repo_group_id})
        return results

    else:
        if group_by == 'week':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('week', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 7.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND i.repo_id = :repo_id
                AND im.msg_id = m.msg_id
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        elif group_by == 'month':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('month', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 30.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND i.repo_id = :repo_id
                AND im.msg_id = m.msg_id
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        elif group_by == 'year':
            issue_comments_mean_std_SQL = s.sql.text("""
                SELECT
                    i.repo_id,
                    DATE_TRUNC('year', m.msg_timestamp::DATE) AS date,
                    COUNT(*) / 365.0 AS mean
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND i.repo_id = :repo_id
                AND im.msg_id = m.msg_id
                GROUP BY i.repo_id, date
                ORDER BY i.repo_id
            """)

        else:
            raise ValueError("Incorrect value for 'group_by'")

        results = pd.read_sql(issue_comments_mean_std_SQL, self.database,
                              params={'repo_id': repo_id})
        return results

@register_metric()
def issue_comments_mean_std(self, repo_group_id, repo_id=None, group_by='week'):
    if not repo_id:
        issue_comments_mean_std_SQL = s.sql.text("""
            SELECT
                repo_id,
                DATE_TRUNC(:group_by, daily) AS date,
                avg(total) AS average,
                stddev(total) AS standard_deviation
            FROM
                (SELECT
                    i.repo_id,
                    DATE_TRUNC('day', m.msg_timestamp) AS daily,
                    COUNT(*) AS total
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND im.msg_id = m.msg_id
                AND i.repo_id IN
                    (SELECT repo_id FROM repo
                     WHERE  repo_group_id = :repo_group_id)
                GROUP BY i.repo_id, daily
                ORDER BY i.repo_id) a
            GROUP BY repo_id, date
            ORDER BY repo_id, date
        """)

        results = pd.read_sql(issue_comments_mean_std_SQL, self.database,
                              params={'repo_group_id': repo_group_id,
                                      'group_by': group_by})
        return results

    else:
        issue_comments_mean_std_SQL = s.sql.text("""
            SELECT
                repo_id,
                DATE_TRUNC(:group_by, daily) AS date,
                avg(total) AS average,
                stddev(total) AS standard_deviation
            FROM
                (SELECT
                    i.repo_id,
                    DATE_TRUNC('day', m.msg_timestamp) AS daily,
                    COUNT(*) AS total
                FROM issues i, issue_message_ref im, message m
                WHERE i.issue_id = im.issue_id
                AND i.pull_request IS NULL 
                AND im.msg_id = m.msg_id
                AND i.repo_id = :repo_id
                GROUP BY i.repo_id, daily
                ORDER BY i.repo_id) a
            GROUP BY repo_id, date
            ORDER BY date
        """)

        results = pd.read_sql(issue_comments_mean_std_SQL, self.database,
                              params={'repo_id': repo_id, 'group_by': group_by})
        return results

@register_metric()
def abandoned_issues(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
    if not begin_date:
        begin_date = '1970-1-1 00:00:01'
    if not end_date:
        end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    abandonedSQL = None

    if repo_id:
        abandonedSQL = s.sql.text(
            '''
            SELECT
	            updated_at,
	            issue_id
            FROM
	            issues
            WHERE
	            repo_id = :repo_id
	            AND issue_state = 'open'
	            AND DATE_PART('year',current_date) - DATE_PART('year', updated_at) >= 1
            GROUP BY
	            updated_at, issue_id
            ORDER BY 
                updated_at, issue_id
            '''
        )
    else:
        abandonedSQL = s.sql.text(
            '''
            SELECT
	            updated_at,
	            issue_id,
                repo_id
            FROM
	            issues
            WHERE
	            repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
	            AND issue_state = 'open'
	            AND DATE_PART('year',current_date) - DATE_PART('year', updated_at) >= 1
            GROUP BY
	            updated_at, issue_id, repo_id
            ORDER BY 
                updated_at, issue_id, repo_id
            '''
        )

    results = pd.read_sql(abandonedSQL, self.database, params={'repo_id': repo_id, 'repo_group_id': repo_group_id, 'period': period,
                                                                 'begin_date': begin_date, 'end_date': end_date})
    return results
