from flask import Response

def create_routes(server):

    metrics = server.augur_app.metrics

    @server.app.route('/{}/repo-groups'.format(server.api_version))
    def get_repo_groups(): #TODO: make this name automatic - wrapper?
        drs = server.transform(metrics.repo_groups)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.update_metric_metadata(function=metrics.repo_groups, endpoint='/{}/repo-groups'.format(server.api_version), metric_type='git')

    @server.app.route('/{}/repos'.format(server.api_version))
    def downloaded_repos():
        drs = server.transform(metrics.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.update_metric_metadata(function=metrics.downloaded_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    server.add_repo_group_metric(metrics.repos_in_repo_groups, 'repos')

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

    server.add_repo_group_metric(metrics.get_issues, 'get-issues')
    server.add_repo_metric(metrics.get_issues, 'get-issues')

    server.add_repo_group_metric(metrics.aggregate_summary, 'aggregate-summary')

    server.add_repo_metric(metrics.aggregate_summary, 'aggregate-summary')