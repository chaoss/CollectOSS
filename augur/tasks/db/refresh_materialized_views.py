from __future__ import annotations
import logging
import sqlalchemy as s
from celery import signature
from celery import group, chain, chord, signature

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession


@celery.task
def refresh_materialized_views():

    logger = logging.getLogger(refresh_materialized_views.__name__)

    refresh_view_query = s.sql.text("""    
                REFRESH MATERIALIZED VIEW augur_data.api_get_all_repos_issues with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_commits_and_committers_daily_count with data;
                REFRESH MATERIALIZED VIEW augur_data.api_get_all_repos_commits with data;
                REFRESH MATERIALIZED VIEW augur_data.augur_new_contributors with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_contributor_actions with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_all with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_detail with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_new_contributors with data;
                REFRESH MATERIALIZED VIEW augur_data.explorer_libyear_summary with data;
    """)

    with DatabaseSession(logger) as session:

        session.execute_sql(refresh_view_query)