#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_repo_group_metric(metrics.top_insights, 'top-insights')
