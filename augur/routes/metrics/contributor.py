#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_repo_group_metric(metrics.contributors, 'contributors')

    server.add_repo_metric(metrics.contributors, 'contributors')

    server.add_repo_group_metric(metrics.contributors_new, 'contributors-new')

    server.add_repo_metric(metrics.contributors_new, 'contributors-new')

    server.add_repo_metric(metrics.committers, 'committers')

    server.add_repo_group_metric(metrics.committers, 'committers')

    server.add_repo_metric(metrics.lines_changed_by_author,'lines-changed-by-author')

    server.add_repo_group_metric(metrics.lines_changed_by_author,'lines-changed-by-author')

    server.add_repo_group_metric(metrics.top_committers, 'top-committers')

    server.add_repo_metric(metrics.top_committers, 'top-committers')

    server.add_repo_group_metric(metrics.contributors_code_development, 'contributors-code-development')

    server.add_repo_metric(metrics.contributors_code_development, 'contributors-code-development')