import sqlalchemy as s
import pandas as pd
from flask import Response

def create_routes(server):

    metrics = server.augur_app.metrics

    @server.app.route('/{}/repo-groups'.format(server.api_version))
    def get_all_repo_groups(): #TODO: make this name automatic - wrapper?
        repoGroupsSQL = s.sql.text("""
            SELECT *
            FROM repo_groups
            ORDER BY rg_name
        """)
        results = pd.read_sql(repoGroupsSQL, server.augur_app.database)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/repos'.format(server.api_version))
    def get_all_repos():
        drs = server.transform(metrics.get_all_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.update_metric_metadata(function=metrics.get_all_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    @server.app.route('/{}/repo-groups/<repo_group_id>/repos'.format(server.api_version))
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
                (select repo_id, COUNT ( commits.cmt_id ) AS commits_all_time from commits group by repo_id ) a on
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

        results = pd.read_sql(repos_in_repo_groups_SQL, server.augur_app.database, params={'repo_group_id': repo_group_id})
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/owner/<owner>/name/<repo>'.format(server.api_version))
    def get_repo_by_git_name(owner, repo):
        a = [owner, repo]
        gre = server.transform(metrics.get_repo_by_git_name, args = a)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/rg-name/<rg_name>/repo-name/<repo_name>'.format(server.api_version))
    def get_repo_by_name(rg_name, repo_name):
        arg = [rg_name, repo_name]
        gre = server.transform(metrics.get_repo_by_name, args=arg)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/rg-name/<rg_name>'.format(server.api_version))
    def get_group_by_name(rg_name):
        arg = [rg_name]
        res = server.transform(metrics.get_group_by_name, args=arg)
        return Response(response=res,
                        status=200,
                        mimetype="application/json")


    @server.app.route('/{}/dosocs/repos'.format(server.api_version))
    def get_repos_for_dosocs():
        res = server.transform(metrics.get_repos_for_dosocs)
        return Response(response=res,
                        status=200,
                        mimetype='application/json')

    server.add_standard_metric(metrics.get_issues, 'get-issues')

    server.add_standard_metric(metrics.aggregate_summary, 'aggregate-summary')