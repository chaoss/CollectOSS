from __future__ import annotations
import logging
import sqlalchemy as s

from augur.tasks.init.celery_app import celery_app as celery
from augur.application.db.lib import execute_sql
from augur.tasks.git.util.facade_worker.facade_worker.config import FacadeHelper
from augur.tasks.git.util.facade_worker.facade_worker.rebuildcache import invalidate_caches, rebuild_unknown_affiliation_and_web_caches


@celery.task(bind=True)
def refresh_materialized_views(self):

    #self.logger = AugurLogger("data_collection_jobs").get_logger()

    engine = self.app.engine

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
        execute_sql(mv1_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv2_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv3_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv4_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv5_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv6_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv7_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv8_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv9_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv10_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv11_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv12_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    try: 
        execute_sql(mv13_refresh)
    except Exception as e: 
        logger.info(f"error is {e}")
        pass 

    #Now refresh facade tables
    #Use this class to get all the settings and 
    #utility functions for facade
    facade_helper = FacadeHelper(logger)

    if facade_helper.nuke_stored_affiliations:
        logger.error("Nuke stored affiliations is deprecated!")
        # deprecated because the UI component of facade where affiliations would be 
        # nuked upon change no longer exists, and this information can easily be derived 
        # from queries and materialized views in the current version of Augur.
        # This method is also a major performance bottleneck with little value.
    
    if not facade_helper.limited_run or (facade_helper.limited_run and facade_helper.fix_affiliations):
        logger.error("Fill empty affiliations is deprecated!")
        # deprecated because the UI component of facade where affiliations would need 
        # to be fixed upon change no longer exists, and this information can easily be derived 
        # from queries and materialized views in the current version of Augur.
        # This method is also a major performance bottleneck with little value.

    if facade_helper.force_invalidate_caches:
        try:
            invalidate_caches(facade_helper)
        except Exception as e:
            logger.info(f"error is {e}")
    
    if not facade_helper.limited_run or (facade_helper.limited_run and facade_helper.rebuild_caches):
        try:
            rebuild_unknown_affiliation_and_web_caches(facade_helper)
        except Exception as e:
            logger.info(f"error is {e}")




