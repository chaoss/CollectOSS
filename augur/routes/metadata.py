#SPDX-License-Identifier: MIT
from flask import Response
from flask import request
import datetime
import base64
import sqlalchemy as s
import pandas as pd
from augur.util import metric_metadata
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import os
import requests

def create_routes(server):

    @server.app.route('/{}/metadata/repo_info'.format(server.api_version))
    def get_repo_info():
        repo_info_sql = s.sql.text("""
            SELECT
                repo.repo_git,
                repo.repo_name,
                repo.repo_id,
                repo_info.default_branch,
                repo_info.license,
                repo_info.fork_count,
                repo_info.watchers_count,
                repo_info.stars_count,
                repo_info.committers_count,
                repo_info.open_issues,
                repo_info.issues_count,
                repo_info.issues_closed,
                repo_info.pull_request_count,
                repo_info.pull_requests_open,
                repo_info.pull_requests_closed,
                repo_info.pull_requests_merged 
            FROM
                repo_info,
                repo,
                ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e 
            WHERE
                repo_info.repo_id = repo.repo_id 
                AND e.repo_id = repo_info.repo_id 
                AND e.last_collected = repo_info.data_collection_date 
            ORDER BY
                repo.repo_name;
        """)
        results = pd.read_sql(repo_info_sql, server.augur_app.database)
        data = results.to_json(orient="columns", date_format='iso', date_unit='ms')
        parsed_data = json.loads(data)
        return Response(response=parsed_data,
                    status=200,
                    mimetype="application/json")