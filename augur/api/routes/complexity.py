#SPDX-License-Identifier: MIT
from flask import Response
import sqlalchemy as s
import pandas as pd
from augur.api.util import metric_metadata
import json
import os
import requests

AUGUR_API_VERSION = 'api/unstable'

def create_routes(server):

    @server.app.route('/{}/complexity/project_languages'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_languages():
        return Response(response="[{'repo_name': 'augur', languages: { 'python': 100 }}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_files'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_files():
        project_lines_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.files
                FROM
                    augur_data.repo,
                (SELECT 
                        d.repo_id,
                        count(*) AS files                        
                    FROM
                        (SELECT
                                augur_data.repo_labor.repo_id
                            FROM
                                augur_data.repo_labor,
                                ( SELECT 
                                        augur_data.repo_labor.repo_id,
                                        MAX ( data_collection_date ) AS last_collected
                                    FROM 
                                        augur_data.repo_labor
                                    GROUP BY augur_data.repo_labor.repo_id) recent 
                            WHERE
                                augur_data.repo_labor.repo_id = recent.repo_id
                                AND augur_data.repo_labor.data_collection_date > recent.last_collected - (5 * interval '1 minute')) d
                    GROUP BY d.repo_id) e
                WHERE augur_data.repo.repo_id = e.repo_id
                ORDER BY e.repo_id
        """)
        results = pd.read_sql(project_lines_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_lines():
        project_lines_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.total_lines,
                    e.average_lines
                FROM
                    augur_data.repo,
                (SELECT 
                        d.repo_id,
                        SUM(d.total_lines) AS total_lines,
                        AVG(d.total_lines)::INT AS average_lines
                    FROM
                        (SELECT
                                augur_data.repo_labor.repo_id,
                                augur_data.repo_labor.total_lines
                            FROM
                                augur_data.repo_labor,
                                ( SELECT 
                                        augur_data.repo_labor.repo_id,
                                        MAX ( data_collection_date ) AS last_collected
                                    FROM 
                                        augur_data.repo_labor
                                    GROUP BY augur_data.repo_labor.repo_id) recent 
                            WHERE
                                augur_data.repo_labor.repo_id = recent.repo_id
                                AND augur_data.repo_labor.data_collection_date > recent.last_collected - (5 * interval '1 minute')) d
                    GROUP BY d.repo_id) e
                WHERE augur_data.repo.repo_id = e.repo_id
                ORDER BY e.repo_id   
        """)
        results = pd.read_sql(project_lines_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_comment_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_comment_lines():
        return Response(response="[{'repo_name': 'augur', 'comment_lines': 10000}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_blank_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_blank_lines():
        return Response(response="[{'repo_name': 'augur', 'blank_lines': 10000}]",
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_file_complexity'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_file_complexity():
        return Response(response="[{'repo_name': 'augur', 'file_complexity': 100}]",
                    status=200,
                    mimetype="application/json")
    
