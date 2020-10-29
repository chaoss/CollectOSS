import base64
import sqlalchemy as s
import pandas as pd
import json
from flask import Response

def create_routes(server):

    @server.app.route('/{}/collection_status/commits'.format(server.api_version))
    def commit_collection_status(): #TODO: make this name automatic - wrapper?
        commit_collection_sql = s.sql.text("""
            SELECT
                repo_id,
                repo_path,
                repo_name,
                repo_git,
                repo_status
            FROM
                repo
            WHERE
                repo_status != 'Complete'
            UNION
            SELECT
                repo_id,
                repo_path,
                repo_name,
                repo_git,
                repo_status
            FROM
                repo
            WHERE
                repo_status = 'Complete'
        """)
        results = pd.read_sql(commit_collection_sql, server.augur_app.database)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/collection_status/issues'.format(server.api_version))
    def issue_collection_status(): #TODO: make this name automatic - wrapper?
        issue_collection_sql = s.sql.text("""
            SELECT
                *
            FROM
                (
                    ( SELECT repo_id, issues_enabled, COUNT ( * ) AS meta_count
                    FROM repo_info
                    WHERE issues_count != 0
                    GROUP BY repo_id, issues_enabled
                    ORDER BY repo_id ) zz
                    LEFT OUTER JOIN (
                    SELECT --A.repo_id,
                        A.repo_name,
                        b.issues_count,
                        d.repo_id AS issue_repo_id,
                        e.last_collected,
                                    f.most_recently_collected_issue,
                        COUNT ( * ) AS issue_count,
                        (
                        b.issues_count - COUNT ( * )) AS issues_missing,
                        ABS (
                        CAST (( COUNT ( * )) +1 AS DOUBLE PRECISION )  / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_abs,
                        (
                        CAST (( COUNT ( * )) +1 AS DOUBLE PRECISION )  / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_issues
                    FROM
                        augur_data.repo A,
                        augur_data.issues d,
                        augur_data.repo_info b,
                        ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e,
                        ( SELECT repo_id, MAX ( data_collection_date ) AS most_recently_collected_issue FROM issues GROUP BY repo_id ORDER BY repo_id ) f
                    WHERE
                        A.repo_id = b.repo_id
                                    AND lower(A.repo_git) like '%github.com%'
                        AND A.repo_id = d.repo_id
                        AND b.repo_id = d.repo_id
                        AND e.repo_id = A.repo_id
                        AND b.data_collection_date = e.last_collected
                        -- AND d.issue_id IS NULL
                        AND f.repo_id = A.repo_id
                                    and d.pull_request is NULL
                                    and b.issues_count is not NULL
                    GROUP BY
                        A.repo_id,
                        d.repo_id,
                        b.issues_count,
                        e.last_collected,
                        f.most_recently_collected_issue
                    ORDER BY ratio_abs
                    ) yy ON zz.repo_id = issue_repo_id
                ) D
            WHERE d.issues_enabled = 'true';
        """)
        results = pd.read_sql(issue_collection_sql, server.augur_app.database)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")

    @server.app.route('/{}/collection_status/pull_requests'.format(server.api_version))
    def pull_request_collection_status(): #TODO: make this name automatic - wrapper?
        pull_request_collection_sql = s.sql.text("""
            SELECT
                *
            FROM
                (
                SELECT
                    repo_info.repo_id,
                    repo.repo_name,
                    MAX ( pull_request_count ) AS max_pr_count,
                    COUNT ( * ) AS meta_count
                FROM
                    repo_info,
                    repo -- WHERE issues_enabled = 'true'
                WHERE
                    pull_request_count >= 1
                    AND repo.repo_id = repo_info.repo_id
                GROUP BY
                    repo_info.repo_id,
                    repo.repo_name
                ORDER BY
                    repo_info.repo_id,
                    repo.repo_name
                ) yy
                LEFT OUTER JOIN (
                SELECT -- A.repo_id,
                    --A.repo_name,
                    b.pull_request_count,
                    d.repo_id AS pull_request_repo_id,
                    e.last_collected,
                    f.last_pr_collected,
                    COUNT ( * ) AS pull_requests_collected,
                    ( b.pull_request_count - COUNT ( * ) ) AS pull_requests_missing,
                    ABS ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_abs,
                    ( CAST ( ( COUNT ( * ) ) + 1 AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION ) ) AS ratio_issues
                FROM
                    augur_data.repo A,
                    augur_data.pull_requests d,
                    augur_data.repo_info b,
                    ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e,
                    ( SELECT repo_id, MAX ( data_collection_date ) AS last_pr_collected FROM augur_data.pull_requests GROUP BY repo_id ORDER BY repo_id ) f
                WHERE
                    A.repo_id = b.repo_id
                    AND LOWER ( A.repo_git ) LIKE'%github.com%'
                    AND A.repo_id = d.repo_id
                    AND b.repo_id = d.repo_id
                    AND e.repo_id = A.repo_id
                    AND b.data_collection_date = e.last_collected
                    AND f.repo_id = A.repo_id -- AND d.pull_request_id IS NULL
                GROUP BY
                    A.repo_id,
                    d.repo_id,
                    b.pull_request_count,
                    e.last_collected,
                    f.last_pr_collected
                ORDER BY
                    ratio_abs desc
                ) zz ON yy.repo_id = pull_request_repo_id
            ORDER BY
                ratio_abs;
        """)
        results = pd.read_sql(pull_request_collection_sql, server.augur_app.database)
        data = results.to_json(orient="records", date_format='iso', date_unit='ms')
        return Response(response=data,
                        status=200,
                        mimetype="application/json")
