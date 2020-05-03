#SPDX-License-Identifier: MIT
from flask import Response

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_standard_metric(metrics.code_changes, 'code-changes')

    server.add_standard_metric(metrics.code_changes_lines, 'code-changes-lines')

    @server.app.route(f"/{server.api_version}/<license_id>/<spdx_binary>/<repo_group_id>/<repo_id>/license-files")
    def get_license_files(license_id, spdx_binary, repo_group_id, repo_id):
        arguments = [license_id, spdx_binary, repo_group_id, repo_id]
        license_files = server.transform(metrics.license_files, args=arguments)
        return Response(response=license_files,
                        status=200,
                        mimetype="application/json")
    server.update_metric_metadata(function=metrics.license_files, endpoint=f"/{server.api_version}/<license_id>/<spdx_binary>/<repo_group_id>/<repo_id>/license-files", metric_type='license')

    server.add_standard_metric(metrics.sbom_download, 'sbom-download')

    server.add_standard_metric(metrics.sub_projects, 'sub-projects')

    server.add_standard_metric(metrics.cii_best_practices_badge, 'cii-best-practices-badge')

    server.add_standard_metric(metrics.forks, 'forks')

    server.add_standard_metric(metrics.fork_count, 'fork-count')

    server.add_standard_metric(metrics.languages, 'languages')

    server.add_standard_metric(metrics.license_count, 'license-count')

    server.add_standard_metric(metrics.license_coverage, 'license-coverage')

    server.add_standard_metric(metrics.license_declared, 'license-declared')

    server.add_standard_metric(metrics.stars, 'stars')

    server.add_standard_metric(metrics.stars_count, 'stars-count')

    server.add_standard_metric(metrics.watchers, 'watchers')

    server.add_standard_metric(metrics.watchers_count, 'watchers-count')

    server.add_standard_metric(metrics.annual_lines_of_code_count_ranked_by_new_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-new-repo-in-repo-group')

    server.add_standard_metric(metrics.annual_lines_of_code_count_ranked_by_repo_in_repo_group,'annual-lines-of-code-count-ranked-by-repo-in-repo-group')

    server.add_standard_metric(metrics.lines_of_code_commit_counts_by_calendar_year_grouped,'lines-of-code-commit-counts-by-calendar-year-grouped')

    server.add_standard_metric(metrics.average_weekly_commits, 'average-weekly-commits')
