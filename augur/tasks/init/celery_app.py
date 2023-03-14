"""Defines the Celery app."""
from celery.signals import worker_process_init, worker_process_shutdown, eventlet_pool_started, eventlet_pool_preshutdown, eventlet_pool_postshutdown
import logging
from typing import List, Dict
import os
from celery import Celery
from celery import current_app 
from celery.signals import after_setup_logger
from sqlalchemy import create_engine, event


from augur.application.logs import TaskLogConfig
from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
from augur.application.config import AugurConfig
from augur.application.db.engine import get_database_string
from augur.tasks.init import get_redis_conn_values, get_rabbitmq_conn_string
from augur.application.db.models import CollectionStatus

class CollectionState(Enum):
    SUCCESS = "Success"
    PENDING = "Pending"
    ERROR = "Error"
    COLLECTING = "Collecting"
    INITIALIZING = "Initializing"
    UPDATE = "Update"
    FAILED_CLONE = "Failed Clone"


logger = logging.getLogger(__name__)

start_tasks = ['augur.tasks.start_tasks',
                'augur.tasks.data_analysis',
                'augur.tasks.util.collection_util']

github_tasks = ['augur.tasks.github.contributors.tasks',
                'augur.tasks.github.issues.tasks',
                'augur.tasks.github.pull_requests.tasks',
                'augur.tasks.github.events.tasks',
                'augur.tasks.github.messages.tasks',
                'augur.tasks.github.facade_github.tasks',
                'augur.tasks.github.releases.tasks',
                'augur.tasks.github.repo_info.tasks',
                'augur.tasks.github.detect_move.tasks',
                'augur.tasks.github.pull_requests.files_model.tasks',
                'augur.tasks.github.pull_requests.commits_model.tasks']

git_tasks = ['augur.tasks.git.facade_tasks',
            'augur.tasks.git.dependency_tasks.tasks',
            'augur.tasks.git.dependency_libyear_tasks.tasks']

data_analysis_tasks = ['augur.tasks.data_analysis.message_insights.tasks',
                       'augur.tasks.data_analysis.clustering_worker.tasks',
                       'augur.tasks.data_analysis.discourse_analysis.tasks',
                       'augur.tasks.data_analysis.pull_request_analysis_worker.tasks',
                       'augur.tasks.data_analysis.insight_worker.tasks']

materialized_view_tasks = ['augur.tasks.db.refresh_materialized_views']

if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
    tasks = start_tasks + github_tasks + git_tasks + materialized_view_tasks + data_analysis_tasks
else:
    tasks = start_tasks + github_tasks + git_tasks + materialized_view_tasks

redis_db_number, redis_conn_string = get_redis_conn_values()

# initialize the celery app
BROKER_URL = get_rabbitmq_conn_string()#f'{redis_conn_string}{redis_db_number}'
BACKEND_URL = f'{redis_conn_string}{redis_db_number+1}'


class AugurTask(celery.Task):
    def task_failed_util(self,exc,traceback,task_id,args, kwargs, einfo):

        from augur.tasks.init.celery_app import engine

        logger = logging.getLogger(task_failed_util.__name__)

        # log traceback to error file
        logger.error(f"Task {task_id} raised exception: {exc}\n{traceback}")

        with DatabaseSession(logger,engine) as session:
            core_id_match = CollectionStatus.core_task_id == task_id
            secondary_id_match = CollectionStatus.secondary_task_id == task_id
            facade_id_match = CollectionStatus.facade_task_id == task_id

            query = session.query(CollectionStatus).filter(or_(core_id_match,secondary_id_match,facade_id_match))

            try:
                collectionRecord = execute_session_query(query,'one')
            except:
                #Exit if we can't find the record.
                return

            if collectionRecord.core_task_id == task_id:
                # set status to Error in db
                collectionRecord.core_status = CollectionState.ERROR.value
                collectionRecord.core_task_id = None


            if collectionRecord.secondary_task_id == task_id:
                # set status to Error in db
                collectionRecord.secondary_status = CollectionState.ERROR.value
                collectionRecord.secondary_task_id = None


            if collectionRecord.facade_task_id == task_id:
                #Failed clone is differant than an error in collection.
                if collectionRecord.facade_status != CollectionState.FAILED_CLONE.value or collectionRecord.facade_status != CollectionState.UPDATE.value:
                    collectionRecord.facade_status = CollectionState.ERROR.value

                collectionRecord.facade_task_id = None

            session.commit()




celery_app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL, include=tasks, task_cls='augur.tasks.init.celery_app:AugurTask')

# define the queues that tasks will be put in (by default tasks are put in celery queue)
celery_app.conf.task_routes = {
    'augur.tasks.start_tasks.*': {'queue': 'scheduling'},
    'augur.tasks.util.collection_util.*': {'queue': 'scheduling'},
    'augur.tasks.github.pull_requests.commits_model.tasks.*': {'queue': 'secondary'},
    'augur.tasks.github.pull_requests.files_model.tasks.*': {'queue': 'secondary'},
    'augur.tasks.github.pull_requests.tasks.collect_pull_request_reviews': {'queue': 'secondary'},
    'augur.tasks.git.dependency_tasks.tasks.*': {'queue': 'secondary'}
}

#Setting to be able to see more detailed states of running tasks
celery_app.conf.task_track_started = True

#ignore task results by default
##celery_app.conf.task_ignore_result = True

# store task erros even if the task result is ignored
celery_app.conf.task_store_errors_even_if_ignored = True

# set task default rate limit
celery_app.conf.task_default_rate_limit = '5/s'

# set tasks annotations for rate limiting specific tasks
celery_app.conf.task_annotations = None

# allow workers to be restarted remotely
celery_app.conf.worker_pool_restarts = True



def split_tasks_into_groups(augur_tasks: List[str]) -> Dict[str, List[str]]:
    """Split tasks on the celery app into groups.

    Args:
        augur_tasks: list of tasks specified in augur

    Returns
        The tasks so that they are grouped by the module they are defined in
    """
    grouped_tasks = {}

    for task in augur_tasks: 
        task_divided = task.split(".")

        try:
            grouped_tasks[task_divided[-2]].append(task_divided[-1])
        except KeyError:
            grouped_tasks[task_divided[-2]] = [task_divided[-1]]
    
    return grouped_tasks




@celery_app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup task scheduler.

    Note:
        This is where all task scedules are defined and added the celery beat

    Args:
        app: Celery app

    Returns
        The tasks so that they are grouped by the module they are defined in
    """
    from augur.tasks.start_tasks import augur_collection_monitor
    from augur.tasks.start_tasks import non_repo_domain_tasks
    
    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        config = AugurConfig(logger, session)

        print(augur_collection_monitor)

        collection_interval = config.get_value('Tasks', 'collection_interval')
        logger.info(f"Scheduling collection every {collection_interval/60} minutes")
        sender.add_periodic_task(collection_interval, augur_collection_monitor.s())

        #Do longer tasks less often
        non_domain_collection_interval = collection_interval * 300
        logger.info(f"Scheduling non-repo-domain collection every {non_domain_collection_interval/60} minutes")
        sender.add_periodic_task(non_domain_collection_interval, non_repo_domain_tasks.s())


@after_setup_logger.connect
def setup_loggers(*args,**kwargs):
    """Override Celery loggers with our own."""

    all_celery_tasks = list(current_app.tasks.keys())

    augur_tasks = [task for task in all_celery_tasks if 'celery.' not in task]
    
    TaskLogConfig(split_tasks_into_groups(augur_tasks))


engine = None
@worker_process_init.connect
def init_worker(**kwargs):

    global engine

    from augur.application.db.engine import DatabaseEngine
    from sqlalchemy.pool import NullPool, StaticPool

    engine = DatabaseEngine(poolclass=StaticPool).engine


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global engine
    if engine:
        logger.info('Closing database connectionn for worker')
        engine.dispose()


