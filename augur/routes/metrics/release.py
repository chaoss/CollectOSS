#SPDX-License-Identifier: MIT

def create_routes(server):

    metrics = server.augur_app.metrics

    server.add_standard_metric(metrics.releases, 'releases')