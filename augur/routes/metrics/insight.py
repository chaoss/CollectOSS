#SPDX-License-Identifier: MIT
from flask import Response

def create_routes(server):

    metrics = server.augur_app.metrics

    @server.app.route(f"/{server.api_version}/repo-groups/<repo_group_id>/top-insights")
    def top_insights(repo_group_id):
        data = server.transform(metrics.top_insights, args=[repo_group_id])
        return Response(response=data,
                        status=200,
                        mimetype="application/json")
