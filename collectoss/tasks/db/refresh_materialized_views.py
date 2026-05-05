from __future__ import annotations
import logging
import sqlalchemy as s

from collectoss.tasks.init.celery_app import celery_app as celery
from collectoss.application.db.materialized_views import MATERIALIZED_VIEWS, get_refresh_sql
from collectoss.tasks.git.util.facade_worker.facade_worker.config import FacadeHelper
from collectoss.tasks.git.util.facade_worker.facade_worker.rebuildcache import invalidate_caches, rebuild_unknown_affiliation_and_web_caches


@celery.task(bind=True)
def refresh_materialized_views(self):

    logger = logging.getLogger(refresh_materialized_views.__name__)

    # REFRESH MATERIALIZED VIEW CONCURRENTLY cannot run inside a transaction
    # block, so we use an autocommit connection rather than execute_sql().
    failed_views = []
    with self.app.engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for view in MATERIALIZED_VIEWS:
            view_fqn = f"{view['schema']}.{view['name']}"
            logger.info(f"Refreshing materialized view: {view_fqn}")
            try:
                conn.execute(s.sql.text(get_refresh_sql(view, concurrently=True)))
            except Exception as e:
                logger.warning(f"Concurrent refresh failed for {view_fqn}, trying non-concurrent: {e}")
                try:
                    conn.execute(s.sql.text(get_refresh_sql(view, concurrently=False)))
                except Exception as e2:
                    logger.error(f"Non-concurrent refresh also failed for {view_fqn}: {e2}")
                    failed_views.append(view_fqn)

    if failed_views:
        raise RuntimeError(
            f"{len(failed_views)} materialized view(s) failed to refresh: {failed_views}"
        )

    #Now refresh facade tables
    #Use this class to get all the settings and
    #utility functions for facade
    facade_helper = FacadeHelper(logger)

    if facade_helper.nuke_stored_affiliations:
        logger.error("Nuke stored affiliations is deprecated!")
        # deprecated because the UI component of facade where affiliations would be
        # nuked upon change no longer exists, and this information can easily be derived
        # from queries and materialized views in the current version of CollectOSS.
        # This method is also a major performance bottleneck with little value.

    if not facade_helper.limited_run or (facade_helper.limited_run and facade_helper.fix_affiliations):
        logger.error("Fill empty affiliations is deprecated!")
        # deprecated because the UI component of facade where affiliations would need
        # to be fixed upon change no longer exists, and this information can easily be derived
        # from queries and materialized views in the current version of CollectOSS.
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
