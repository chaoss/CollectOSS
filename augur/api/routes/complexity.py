#SPDX-License-Identifier: MIT
from flask import Response
import sqlalchemy as s
import pandas as pd
from augur.api.util import metric_metadata
import os
import requests

AUGUR_API_VERSION = 'api/unstable'

def create_routes(server):

    @server.app.route('/{}/complexity/project_languages'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_languages():
        project_languages_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.programming_language,
                    e.code_lines,
                    e.files
                FROM
                    augur_data.repo,
                (SELECT 
                    d.repo_id,
                    d.programming_language,
                    SUM(d.code_lines) AS code_lines,
                    COUNT(*)::int AS files
                FROM
                    (SELECT
                            augur_data.repo_labor.repo_id,
                            augur_data.repo_labor.programming_language,
                            augur_data.repo_labor.code_lines
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
                GROUP BY d.repo_id, d.programming_language) e
                WHERE augur_data.repo.repo_id = e.repo_id
                ORDER BY e.repo_id
        """)
        results = pd.read_sql(project_languages_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_files'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_files():
        project_files_sql = s.sql.text("""
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
        results = pd.read_sql(project_files_sql,  server.engine)
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
        comment_lines_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.comment_lines,
                    e.avg_comment_lines
                FROM
                    augur_data.repo,
                (SELECT 
                        d.repo_id,
                        SUM(d.comment_lines) AS comment_lines,
                        AVG(d.comment_lines)::INT AS avg_comment_lines
                    FROM
                        (SELECT
                                augur_data.repo_labor.repo_id,
                                augur_data.repo_labor.comment_lines
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
        results = pd.read_sql(comment_lines_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")

    @server.app.route('/{}/complexity/project_blank_lines'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_blank_lines():
        blank_lines_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.blank_lines,
                    e.avg_blank_lines
                FROM
                    augur_data.repo,
                (SELECT 
                        d.repo_id,
                        SUM(d.blank_lines) AS blank_lines,
                        AVG(d.blank_lines)::int AS avg_blank_lines
                    FROM
                        (SELECT
                                augur_data.repo_labor.repo_id,
                                augur_data.repo_labor.blank_lines
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
        results = pd.read_sql(blank_lines_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")
        

    @server.app.route('/{}/complexity/project_file_complexity'.format(AUGUR_API_VERSION), methods=["GET"])
    def get_project_file_complexity():
        project_file_complexity_sql = s.sql.text("""
            SELECT
                    e.repo_id,
                    augur_data.repo.repo_git,
                    augur_data.repo.repo_name,
                    e.sum_code_complexity,
                    e.average_code_complexity
                FROM
                    augur_data.repo,
                (SELECT 
                        d.repo_id,
                        SUM(d.code_complexity) AS sum_code_complexity,
                        AVG(d.code_complexity)::int AS average_code_complexity
                    FROM
                        (SELECT
                                augur_data.repo_labor.repo_id,
                                augur_data.repo_labor.code_complexity
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
        results = pd.read_sql(project_file_complexity_sql,  server.engine)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                    status=200,
                    mimetype="application/json")
    
