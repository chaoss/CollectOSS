#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_standard_metric(metrics.contributors, 'contributors')

    server.add_standard_metric(metrics.contributors_new, 'contributors-new')

    server.add_standard_metric(metrics.committers, 'committers')

    server.add_standard_metric(metrics.lines_changed_by_author,'lines-changed-by-author')

    server.add_standard_metric(metrics.top_committers, 'top-committers')

    server.add_standard_metric(metrics.contributors_code_development, 'contributors-code-development')