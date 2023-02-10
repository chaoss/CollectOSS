from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo 
from augur.application.db.util import execute_session_query
from celery import group, chain, chord, signature
from augur.tasks.init.celery_app import celery_app as celery
import logging 

def machine_learning_phase():
    from augur.tasks.data_analysis.clustering_worker.tasks import clustering_model
    from augur.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker import contributor_breadth_model
    from augur.tasks.data_analysis.discourse_analysis.tasks import discourse_analysis_model
    from augur.tasks.data_analysis.insight_worker.tasks import insight_model
    from augur.tasks.data_analysis.message_insights.tasks import message_insight_model
    from augur.tasks.data_analysis.pull_request_analysis_worker.tasks import pull_request_analysis_model

    from augur.tasks.init.celery_app import engine

    logger = logging.getLogger(machine_learning_phase.__name__)

    ml_tasks = []
    ml_tasks.append(clutering_task.si())
    ml_tasks.append(discourse_analysis_task.si())
    ml_tasks.append(insight_task.si())
    ml_tasks.append(message_insight_task.si())
    ml_tasks.append(pull_request_analysis_task.si()) 
        
    return ml_tasks