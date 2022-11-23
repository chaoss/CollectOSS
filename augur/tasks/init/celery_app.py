"""Defines the Celery app."""
from celery.signals import worker_process_init, worker_process_shutdown
import logging
from typing import List, Dict
import os
from celery import Celery
from celery import current_app 
from celery.signals import after_setup_logger
from sqlalchemy import create_engine, event


from augur.application.logs import TaskLogConfig
from augur.application.db.session import DatabaseSession
from augur.application.db.engine import get_database_string
from augur.tasks.init import get_redis_conn_values

logger = logging.getLogger(__name__)

start_tasks = ['augur.tasks.start_tasks']

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

git_tasks = ['augur.tasks.git.facade_tasks']

data_analysis_tasks = ['augur.tasks.data_analysis.message_insights.tasks',
                       'augur.tasks.data_analysis.clustering_worker.tasks',
                       'augur.tasks.data_analysis.discourse_analysis.tasks',
                       'augur.tasks.data_analysis.pull_request_analysis_worker.tasks']

materialized_view_tasks = ['augur.tasks.db.refresh_materialized_views']

if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
    tasks = start_tasks + github_tasks + git_tasks + materialized_view_tasks + data_analysis_tasks
else:
    tasks = start_tasks + github_tasks + git_tasks + materialized_view_tasks

redis_db_number, redis_conn_string = get_redis_conn_values()

task_annotations = {'*': {'rate_limit': '5/s'}}

# initialize the celery app
BROKER_URL = f'{redis_conn_string}{redis_db_number}'
BACKEND_URL = f'{redis_conn_string}{redis_db_number+1}'

celery_app = Celery('tasks', broker=BROKER_URL, backend=BACKEND_URL, include=tasks, 
                            CELERY_ANNOTATIONS=task_annotations, worker_pool_restarts=True)

celery_app.conf.task_routes = {
    'augur.tasks.git.facade_tasks.*': {'queue': 'cpu'}
}

#Setting to be able to see more detailed states of running tasks
celery_app.conf.task_track_started = True


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
    from augur.tasks.start_tasks import start_task

    with DatabaseSession(logger) as session:

        collection_interval = session.config.get_value('Tasks', 'collection_interval')
        logger.info(f"Scheduling collection every {collection_interval/60/60} hours")
        sender.add_periodic_task(collection_interval, start_task.s())


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

    from augur.application.db.engine import create_database_engine

    engine = create_database_engine()


@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    global engine
    if engine:
        logger.info('Closing database connectionn for worker')
        engine.dispose()

