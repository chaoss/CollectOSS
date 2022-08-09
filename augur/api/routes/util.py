#SPDX-License-Identifier: MIT
import base64
import sqlalchemy as s
import pandas as pd
import json
from flask import Response
import logging

from augur.application.db.session import DatabaseSession
from augur.application.logs import AugurLogger

logger = AugurLogger("augur").get_logger()
session = DatabaseSession(logger)
augur_config = session.config
engine = session.engine

AUGUR_API_VERSION = 'api/unstable'

def create_routes(server):

    server.app.route('/{}/repo-groups'.format(AUGUR_API_VERSION))
    def get_all_repo_groups(): #TODO: make this name automatic - wrapper?
        repoGroupsSQL = s.sql.text("""
            SELECT *
            FROM repo_groups
            ORDER BY rg_name
        """)
        results = pd.read_sql(repoGroupsSQL,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/repos'.format(AUGUR_API_VERSION))
    def get_all_repos():

        get_all_repos_sql = s.sql.text("""
            SELECT
                repo.repo_id,
                repo.repo_name,
                repo.description,
                repo.repo_git AS url,
                repo.repo_status,
                a.commits_all_time,
                b.issues_all_time ,
                rg_name,
                repo.repo_group_id
            FROM
                repo
                left outer join
                (select * from api_get_all_repos_commits ) a on
                repo.repo_id = a.repo_id
                left outer join
                (select * from api_get_all_repos_issues) b
                on
                repo.repo_id = b.repo_id
                JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
            order by repo_name
        """)
        results = pd.read_sql(get_all_repos_sql,  server.engine)
        results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])

        b64_urls = []
        for i in results.index:
            b64_urls.append(base64.b64encode((results.at[i, 'url']).encode()))
        results['base64_url'] = b64_urls

        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/repo-groups/<repo_group_id>/repos'.format(AUGUR_API_VERSION))
    def get_repos_in_repo_group(repo_group_id):
        repos_in_repo_groups_SQL = s.sql.text("""
            SELECT
                repo.repo_id,
                repo.repo_name,
                repo.description,
                repo.repo_git AS url,
                repo.repo_status,
                a.commits_all_time,
                b.issues_all_time
            FROM
                repo
                left outer join
                (select repo_id, COUNT ( distinct commits.cmt_commit_hash ) AS commits_all_time from commits group by repo_id ) a on
                repo.repo_id = a.repo_id
                left outer join
                (select repo_id, count ( issues.issue_id) as issues_all_time from issues where issues.pull_request IS NULL group by repo_id) b
                on
                repo.repo_id = b.repo_id
                JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
            WHERE
                repo_groups.repo_group_id = :repo_group_id
            ORDER BY repo.repo_git
        """)

        results = pd.read_sql(repos_in_repo_groups_SQL, server.engine, params={'repo_group_id': repo_group_id})
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/owner/<owner>/repo/<repo>'.format(AUGUR_API_VERSION))
    def get_repo_by_git_name(owner, repo):

        get_repo_by_git_name_sql = s.sql.text("""
            SELECT repo.repo_id, repo.repo_group_id, rg_name
            FROM repo JOIN repo_groups ON repo_groups.repo_group_id = repo.repo_group_id
            WHERE repo_name = :repo AND repo_path LIKE :owner
            GROUP BY repo_id, rg_name
        """)

        results = pd.read_sql(get_repo_by_git_name_sql, server.engine, params={'owner': '%{}_'.format(owner), 'repo': repo,})
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/rg-name/<rg_name>/repo-name/<repo_name>'.format(AUGUR_API_VERSION))
    def get_repo_by_name(rg_name, repo_name):

        get_repo_by_name_sql = s.sql.text("""
            SELECT repo_id, repo.repo_group_id, repo_git as url
            FROM repo, repo_groups
            WHERE repo.repo_group_id = repo_groups.repo_group_id
            AND LOWER(rg_name) = LOWER(:rg_name)
            AND LOWER(repo_name) = LOWER(:repo_name)
        """)
        results = pd.read_sql(get_repo_by_name_sql, server.engine, params={'rg_name': rg_name, 'repo_name': repo_name})
        results['url'] = results['url'].apply(lambda datum: datum.split('//')[1])
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/rg-name/<rg_name>'.format(AUGUR_API_VERSION))
    def get_group_by_name(rg_name):
        groupSQL = s.sql.text("""
            SELECT repo_group_id, rg_name
            FROM repo_groups
            WHERE lower(rg_name) = lower(:rg_name)
        """)
        results = pd.read_sql(groupSQL, server.engine, params={'rg_name': rg_name})
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    server.app.route('/{}/dosocs/repos'.format(AUGUR_API_VERSION))
    def get_repos_for_dosocs():
        get_repos_for_dosocs_SQL = s.sql.text("""
            SELECT b.repo_id, CONCAT(a.value || b.repo_group_id || chr(47) || b.repo_path || b.repo_name) AS path
            FROM settings a, repo b
            WHERE a.setting='repo_directory'
        """)

        results = pd.read_sql(get_repos_for_dosocs_SQL,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype='application/json')

    server.app.route('/{}/repo-groups/<repo_group_id>/get-issues'.format(AUGUR_API_VERSION))
    server.app.route('/{}/repos/<repo_id>/get-issues'.format(AUGUR_API_VERSION))
    def get_issues(repo_group_id, repo_id=None):
        if not repo_id:
            get_issues_sql = s.sql.text("""
                SELECT issue_title,
                    issues.issue_id,
                    issues.repo_id,
                    issues.html_url,
                    issue_state                                 AS STATUS,
                    issues.created_at                           AS DATE,
                    count(issue_events.event_id),
                    MAX(issue_events.created_at)                AS LAST_EVENT_DATE,
                    EXTRACT(DAY FROM NOW() - issues.created_at) AS OPEN_DAY
                FROM issues,
                    issue_events
                WHERE issues.repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id = :repo_group_id)
                AND issues.issue_id = issue_events.issue_id
                AND issues.pull_request is NULL
                GROUP BY issues.issue_id
                ORDER by OPEN_DAY DESC
            """)
            results = pd.read_sql(get_issues_sql, server.engine, params={'repo_group_id': repo_group_id})
        else:
            get_issues_sql = s.sql.text("""
                SELECT issue_title,
                    issues.issue_id,
                    issues.repo_id,
                    issues.html_url,
                    issue_state                                 AS STATUS,
                    issues.created_at                           AS DATE,
                    count(issue_events.event_id),
                    MAX(issue_events.created_at)                AS LAST_EVENT_DATE,
                    EXTRACT(DAY FROM NOW() - issues.created_at) AS OPEN_DAY,
                    repo_name
                FROM issues JOIN repo ON issues.repo_id = repo.repo_id, issue_events
                WHERE issues.repo_id = :repo_id
                AND issues.pull_request IS NULL
                AND issues.issue_id = issue_events.issue_id
                GROUP BY issues.issue_id, repo_name
                ORDER by OPEN_DAY DESC
            """)
            results = pd.read_sql(get_issues_sql, server.engine, params={'repo_id': repo_id})
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype='application/json')

    server.app.route('/{}/api-port'.format(AUGUR_API_VERSION))
    def api_port():
        response = {'port': augur_config.get_value('Server', 'port')}
        return Response(response=json.dumps(response),
                        status=200,
                        mimetype="application/json")
