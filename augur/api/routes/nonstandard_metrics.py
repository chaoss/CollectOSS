#SPDX-License-Identifier: MIT
import base64
import sqlalchemy as s
import pandas as pd
from flask import Response

from augur.api.metrics.repo_meta import license_files
from augur.api.metrics.insight import top_insights

from augur.api.routes import AUGUR_API_VERSION
from ..server import app, route_transform


@app.route(f"/{AUGUR_API_VERSION}/<license_id>/<spdx_binary>/<repo_group_id>/<repo_id>/license-files")
def get_license_files(license_id, spdx_binary, repo_group_id, repo_id):
    arguments = [license_id, spdx_binary, repo_group_id, repo_id]
    license_files = route_transform(license_files, args=arguments)
    return Response(response=license_files,
                    status=200,
                    mimetype="application/json")

@app.route(f"/{AUGUR_API_VERSION}/repo-groups/<repo_group_id>/top-insights")
def top_insights(repo_group_id):
    data = route_transform(top_insights, args=[repo_group_id])
    return Response(response=data,
                    status=200,
                    mimetype="application/json")
