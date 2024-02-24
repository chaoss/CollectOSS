from __future__ import annotations
import logging
import sqlalchemy as s
from celery import signature
from celery import group, chain, chord, signature

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.session import DatabaseSession
from augur.application.logs import AugurLogger


@celery.task
def refresh_materialized_views():

    #self.logger = AugurLogger("data_collection_jobs").get_logger()

    from augur.application.db import get_engine
    engine = get_engine()

    logger = logging.getLogger(refresh_materialized_views.__name__)
    #self.logger = logging.getLogger(refresh_materialized_views.__name__)

    mv1_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.api_get_all_repo_prs with data;
                COMMIT; 
    """)

    mv2_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.api_get_all_repos_commits with data;
                COMMIT; 
    """)

    mv3_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.api_get_all_repos_issues with data;
                COMMIT; 
    """)

    mv4_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.augur_new_contributors with data;
                COMMIT; 
    """)
    mv5_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_commits_and_committers_daily_count with data;
                COMMIT; 
    """)

    mv6_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_new_contributors with data;
                COMMIT; 
    """)

    mv7_refresh = s.sql.text("""    
                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_entry_list with data;
                COMMIT; 
    """)

    mv8_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_contributor_actions with data;
                COMMIT; 
    """)

    mv9_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_user_repos with data;
                COMMIT; 
    """)

    mv10_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_pr_response_times with data;
                COMMIT; 
    """)

    mv11_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_pr_assignments with data;
                COMMIT; 
    """)

    mv12_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_issue_assignments with data;
                COMMIT; 
    """)

    mv13_refresh = s.sql.text("""    

                REFRESH MATERIALIZED VIEW concurrently augur_data.explorer_pr_response with data;
                COMMIT; 
    """)

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv1_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv2_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv3_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv4_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv5_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv6_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv7_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv8_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv9_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv10_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv11_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv12_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        with DatabaseSession(logger, engine) as session:
            session.execute_sql(mv13_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 





