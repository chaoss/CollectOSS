#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_repo_group_metric(metrics.code_changes, 'code-changes')

    server.add_repo_metric(metrics.code_changes, 'code-changes')

    server.add_repo_group_metric(metrics.code_changes_lines, 'code-changes-lines')

    server.add_repo_metric(metrics.code_changes_lines, 'code-changes-lines')

    server.add_license_metric(metrics.license_files, 'license-files')

    server.add_repo_metric(metrics.sbom_download, 'sbom-download')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_group_route(repo_group_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'period': period,
    #               'begin_date': begin_date, 'end_date': end_date}

    #     data = server.transform(metrics.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/repo/<repo_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_route(repo_group_id, repo_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'repo_id': repo_id,
    #               'period': period, 'begin_date': begin_date,
    #               'end_date': end_date}

    #     data = server.transform(metrics.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    server.add_repo_group_metric(metrics.sub_projects, 'sub-projects')

    server.add_repo_metric(
        metrics.sub_projects, 'sub-projects')

    server.add_repo_group_metric(metrics.cii_best_practices_badge, 'cii-best-practices-badge')

    server.add_repo_metric(metrics.cii_best_practices_badge, 'cii-best-practices-badge')

    server.add_repo_group_metric(metrics.forks, 'forks')

    server.add_repo_metric(metrics.forks, 'forks')

    server.add_repo_group_metric(metrics.fork_count, 'fork-count')

    server.add_repo_metric(metrics.fork_count, 'fork-count')

    server.add_repo_group_metric(metrics.languages, 'languages')

    server.add_repo_metric(metrics.languages, 'languages')

    server.add_repo_group_metric(metrics.license_count, 'license-count')

    server.add_repo_metric(metrics.license_count, 'license-count')

    server.add_repo_metric(metrics.license_coverage, 'license-coverage')

    server.add_repo_group_metric(metrics.license_coverage, 'license-coverage')

    server.add_repo_metric(metrics.license_declared, 'license-declared')

    server.add_repo_group_metric(metrics.license_declared, 'license-declared')

    server.add_repo_group_metric(metrics.stars, 'stars')

    server.add_repo_metric(metrics.stars, 'stars')

    server.add_repo_group_metric(metrics.stars_count, 'stars-count')

    server.add_repo_metric(metrics.stars_count, 'stars-count')

    server.add_repo_group_metric(metrics.watchers, 'watchers')

    server.add_repo_metric(metrics.watchers, 'watchers')

    server.add_repo_group_metric(metrics.watchers_count, 'watchers-count')

    server.add_repo_metric(metrics.watchers_count, 'watchers-count')

    server.add_repo_group_metric(metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')

    server.add_repo_metric(metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')

    server.add_repo_group_metric(metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-repo-in-repo-group')

    server.add_repo_metric(metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-repo-in-repo-group')

    server.add_repo_metric(metrics.lines_of_code_commit_counts_by_calendar_year_grouped,'lines-of-code-commit-counts-by-calendar-year-grouped')

    server.add_metric(metrics.average_weekly_commits, 'average-weekly-commits')

    server.add_repo_metric(metrics.average_weekly_commits, 'average-weekly-commits')

    server.add_repo_group_metric(metrics.average_weekly_commits, 'average-weekly-commits')
    
