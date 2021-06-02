#SPDX-License-Identifier: MIT
import base64
import sqlalchemy as s
import pandas as pd
import json
from flask import Response

def create_routes(server):

    metrics = server.augur_app.metrics

    @server.app.route(f"/{server.api_version}/<license_id>/<spdx_binary>/<repo_group_id>/<repo_id>/license-files")
    def get_license_files(license_id, spdx_binary, repo_group_id, repo_id):
        arguments = [license_id, spdx_binary, repo_group_id, repo_id]
        license_files = server.transform(metrics.license_files, args=arguments)
        return Response(response=license_files,
                        status=200,
                        mimetype="application/json")

    @server.app.route(f"/{server.api_version}/repo-groups/<repo_group_id>/top-insights")
    def top_insights(repo_group_id):
        data = server.transform(metrics.top_insights, args=[repo_group_id])
        return Response(response=data,
                        status=200,
                        mimetype="application/json")