#SPDX-License-Identifier: MIT
"""
Metrics that provides data about issues & their associated activity
"""

import datetime
import sqlalchemy as s
import pandas as pd
from flask import current_app, request, jsonify

from augur.api.util import register_metric
from .util import get_repo_ids, UserGroupRequest, repo_metrics_route, group_metrics_route

from ...server import app

@repo_metrics_route('/metrics/issues-first-time-opened/repo/<int:repo_id>')
def issues_first_time_opened_repo(repo_id, period, begin_date, end_date):

    return get_issues_first_time_opened(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-first-time-opened/group/<string:group_name>')
def issues_first_time_opened_group(user_group_request, period, begin_date, end_date):

    return get_issues_first_time_opened(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-first-time-closed/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issues_first_time_closed(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-first-time-closed/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issues_first_time_closed(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-new/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_new_issues(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-new/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_new_issues(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-active/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_active_issues(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-active/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_active_issues(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-closed/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_closed_issues(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-closed/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_closed_issues(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-duration/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_duration(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-duration/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_duration(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-participants/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_participants(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-participants/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_participants(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-backlog/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_backlog(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-backlog/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_backlog(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-throughput/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_throughput(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-throughput/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_throughput(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-open-age/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_open_age(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-open-age/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_open_age(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)

@repo_metrics_route('/metrics/issues-closed-resolution-duration/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_closed_resolution_duration(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-closed-resolution-duration/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_closed_resolution_duration(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)

@repo_metrics_route('/metrics/issues-average-issue-resolution-time/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_closed_resolution_duration(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-average-issue-resolution-time/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_average_issue_resolution_time(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)


@repo_metrics_route('/metrics/issues-maintainer-response-duration/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_issue_maintainer_response_duration(repo_id=repo_id, period=period, begin_date=begin_date, end_date=end_date)

@group_metrics_route('/metrics/issues-maintainer-response-duration/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_issue_maintainer_response_duration(user_group_request=user_group_request, period=period, begin_date=begin_date, end_date=end_date)

# TODO: Look into what to do here. These routes only took in repo_id and repo_group_id
@repo_metrics_route('/metrics/open-issues-count/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_open_issue_count(repo_id=repo_id)

@group_metrics_route('/metrics/open-issues-count/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_open_issue_count(user_group_request=user_group_request)

@repo_metrics_route('/metrics/closed-issues-count/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_closed_issue_count(repo_id=repo_id)

@group_metrics_route('/metrics/closed-issues-count/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_closed_issue_count(user_group_request=user_group_request)

@repo_metrics_route('/metrics/abandoned-issues/repo/<int:repo_id>')
def issues_first_time_closed_repo(repo_id, period, begin_date, end_date):

    return get_abandoned_issues(repo_id=repo_id)

@group_metrics_route('/metrics/abandoned-issues/group/<string:group_name>')
def issues_first_time_closed_group(user_group_request, period, begin_date, end_date):

    return get_abandoned_issues(user_group_request=user_group_request)


# TODO: Look into how to handle these metrics that have a group by
@register_metric()
def issue_comments_mean(repo_group_id, repo_id=None, group_by='week'):
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

        with current_app.engine.connect() as conn:
            results = pd.read_sql(issue_comments_mean_std_SQL, conn,
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

        with current_app.engine.connect() as conn:
            results = pd.read_sql(issue_comments_mean_std_SQL, conn,
                                params={'repo_id': repo_id})
        return results

@register_metric()
def issue_comments_mean_std(repo_group_id, repo_id=None, group_by='week'):
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


        with current_app.engine.connect() as conn:
            results = pd.read_sql(issue_comments_mean_std_SQL, conn,
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

        with current_app.engine.connect() as conn:
            results = pd.read_sql(issue_comments_mean_std_SQL, conn,
                                params={'repo_id': repo_id, 'group_by': group_by})
        return results



def get_issues_first_time_opened(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

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
                    AND repo_id in :repo_ids
                    AND created_at BETWEEN :begin_date AND :end_date
                GROUP BY gh_user_id, repo_id
            ) as abc, repo
            WHERE repo.repo_id= abc.repo_id
            GROUP BY repo.repo_id, issue_date
            ORDER BY issue_date
        """)

        results = pd.read_sql(issueNewContributor, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issues_first_time_closed(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issuesClosedSQL = s.sql.text("""
            SELECT date_trunc(:period, new_date::DATE) AS issue_date,
                COUNT(cntrb_id),
                repo_name,
                repo_id
            FROM (
                    SELECT issue_events.cntrb_id, MIN(issue_events.created_at) AS new_date, repo_name, repo.repo_id as repo_id
                    FROM issue_events,
                        repo,
                        issues
                    WHERE repo.repo_id IN :repo_ids
                    AND action = 'closed'
                    AND repo.repo_id = issues.repo_id
                    AND issues.pull_request IS NULL 
                    AND issues.issue_id = issue_events.issue_id
                    And issue_events.created_at BETWEEN :begin_date AND :end_date
                    GROUP BY issue_events.cntrb_id, repo_name
                ) AS iss_close
            GROUP BY issue_date, repo_name
        """)
        with current_app.engine.connect() as conn:
            results = pd.read_sql(issuesClosedSQL, conn, params={'repo_ids': repo_ids, 'period': period,
                                                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_new_issues(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issues_new_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, issues.created_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN :repo_ids
            AND issues.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_new_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    


def get_active_issues(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issues_active_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, issue_events.created_at) as date,
                COUNT(issues.issue_id) AS issues
            FROM issues, repo, issue_events
            WHERE issues.issue_id = issue_events.issue_id
            AND issues.repo_id = repo.repo_id
            AND issues.repo_id IN :repo_ids
            AND issue_events.created_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            and issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_active_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_closed_issues(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issues_closed_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                date_trunc(:period, closed_at::DATE) as date,
                COUNT(issue_id) as issues
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN :repo_ids
            AND closed_at IS NOT NULL
            AND closed_at BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS') AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, date, repo_name
            ORDER BY issues.repo_id, date
        """)

        results = pd.read_sql(issues_closed_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_duration(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issue_duration_SQL = s.sql.text("""
            SELECT
                issues.repo_id,
                repo_name,
                issue_id,
                issues.created_at,
                issues.closed_at,
                (issues.closed_at - issues.created_at) AS duration
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN :repo_ids
            AND closed_at IS NOT NULL
            AND issues.pull_request IS NULL
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            ORDER BY repo_id, issue_id
        """)

        results = pd.read_sql(issue_duration_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_participants(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

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
            AND issues.repo_id IN :repo_ids
            AND issues.created_at
                BETWEEN to_timestamp(:begin_date, 'YYYY-MM-DD HH24:MI:SS')
                AND to_timestamp(:end_date, 'YYYY-MM-DD HH24:MI:SS')
            GROUP BY issues.repo_id, repo.repo_name, derived.issue_id, issues.created_at
            ORDER BY issues.repo_id, issues.created_at
        """)

        results = pd.read_sql(issue_participants_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_backlog(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        issue_backlog_SQL = s.sql.text("""
            SELECT issues.repo_id, repo_name, COUNT(issue_id) as issue_backlog
            FROM issues JOIN repo ON issues.repo_id = repo.repo_id
            WHERE issues.repo_id IN :repo_ids
            AND issue_state = 'open'
            AND issues.pull_request IS NULL
            GROUP BY issues.repo_id, repo_name
            ORDER BY issues.repo_id
        """)

        results = pd.read_sql(issue_backlog_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_throughput(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        # TODO: Check if "AND issues.pull_request IS NULL" is needed since prs are no longer stored in issues table
        issue_throughput_SQL = s.sql.text("""
            SELECT table1.repo_id, repo.repo_name, (tot1 / tot2) AS throughput
            FROM
                (SELECT repo_id, COUNT(issue_id)::REAL AS tot1
                FROM issues 
                WHERE issue_state='closed' 
                AND issues.pull_request IS NULL
                AND repo_id IN :repo_ids
                GROUP BY repo_id) AS table1,
                (SELECT repo_id, COUNT(issue_id)::REAL AS tot2
                FROM issues
                WHERE repo_id IN :repo_ids
                AND issues.pull_request IS NULL
                GROUP BY repo_id) AS table2,
                repo
            WHERE table1.repo_id = table2.repo_id
            AND table1.repo_id = repo.repo_id
        """)

        results = pd.read_sql(issue_throughput_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_open_age(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        openAgeSQL = s.sql.text("""
            SELECT  repo.repo_id, repo_name, issue_id, date_trunc(:period, issues.created_at ) as date, EXTRACT(DAY FROM NOW() - issues.created_at) AS open_date
            FROM issues,
                repo,
                repo_groups
            WHERE issue_state = 'open'
            AND issues.pull_request IS NULL
            AND issues.repo_id IN :repo_ids
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id, repo_name, issue_id, date, open_date
            ORDER BY open_date DESC
        """)

        results = pd.read_sql(openAgeSQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_issue_closed_resolution_duration(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

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
            AND issues.repo_id IN :repo_ids
            AND repo.repo_id = issues.repo_id
            AND issues.created_at BETWEEN :begin_date and :end_date
            GROUP BY repo.repo_id, repo.repo_name, gh_issue_number, issue_title, issues.created_at, issues.closed_at, DIFFDATE
            ORDER BY gh_issue_number
        """)

        results = pd.read_sql(issueSQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_average_issue_resolution_time(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        avg_issue_resolution_SQL = s.sql.text("""
        SELECT
            issues.repo_id,
            repo.repo_name,
            AVG(issues.closed_at - issues.created_at)::text AS avg_issue_resolution_time
        FROM issues JOIN repo ON issues.repo_id = repo.repo_id
        WHERE issues.repo_id IN :repo_ids
        AND closed_at IS NOT NULL
        AND pull_request IS NULL 
        GROUP BY issues.repo_id, repo.repo_name
        ORDER BY issues.repo_id
        """)

        results = pd.read_sql(avg_issue_resolution_SQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    
def get_issue_maintainer_response_duration(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

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
                            where repo.repo_id IN :repo_ids
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

        results = pd.read_sql(issuesSQL, conn,
                            params={'repo_ids': repo_ids, 'period': period,
                                    'begin_date': begin_date, 'end_date': end_date})
                
        return results
    

def get_open_issue_count(repo_id : int = None, user_group_request : UserGroupRequest = None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        openIssueCountSQL = s.sql.text("""
            SELECT rg_name, count(issue_id) AS open_count, date_trunc('week', issues.created_at) AS DATE
            FROM issues, repo, repo_groups
            WHERE issue_state = 'open'
            AND issues.repo_id IN :repo_ids
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo_groups.rg_name
            ORDER BY date
        """)

        results = pd.read_sql(openIssueCountSQL, conn, params={'repo_ids': repo_ids})
                
        return results
    

def get_closed_issue_count(repo_id : int = None, user_group_request : UserGroupRequest = None, period='day', begin_date=None, end_date=None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        closedIssueCountSQL = s.sql.text("""
            SELECT rg_name, count(issue_id) AS closed_count, date_trunc('week', issues.created_at) AS DATE
            FROM issues, repo, repo_groups
            WHERE issue_state = 'closed'
            AND issues.repo_id IN :repo_ids
            AND repo.repo_id = issues.repo_id
            AND repo.repo_group_id = repo_groups.repo_group_id
            AND issues.pull_request IS NULL 
            GROUP BY date, repo_groups.rg_name
            ORDER BY date
        """)

        results = pd.read_sql(closedIssueCountSQL, conn, params={'repo_ids': repo_ids})

                
        return results
    


def get_abandoned_issues(repo_id : int = None, user_group_request : UserGroupRequest = None):

    with current_app.engine.connect() as conn:
    
        repo_ids = get_repo_ids(conn, repo_id, user_group_request)

        abandonedSQL = s.sql.text(
            '''
            SELECT
	            updated_at,
	            issue_id,
                repo_id
            FROM
	            issues
            WHERE
	            repo_id IN :repo_ids
	            AND issue_state = 'open'
	            AND DATE_PART('year',current_date) - DATE_PART('year', updated_at) >= 1
            GROUP BY
	            updated_at, issue_id, repo_id
            ORDER BY 
                updated_at, issue_id, repo_id
            '''
        )

        results = pd.read_sql(abandonedSQL, conn, params={'repo_ids': repo_ids})
                
        return results
    
