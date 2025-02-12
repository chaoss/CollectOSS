from celery import chain
import logging 

def machine_learning_phase(repo_git, full_collection):
    from augur.tasks.data_analysis.clustering_worker.tasks import clustering_task
    from augur.tasks.data_analysis.discourse_analysis.tasks import discourse_analysis_task
    from augur.tasks.data_analysis.insight_worker.tasks import insight_task
    from augur.tasks.data_analysis.message_insights.tasks import message_insight_task
    from augur.tasks.data_analysis.pull_request_analysis_worker.tasks import pull_request_analysis_task

    logger = logging.getLogger(machine_learning_phase.__name__)

    ml_tasks = []
    ml_tasks.append(clustering_task.si(repo_git))
    ml_tasks.append(discourse_analysis_task.si(repo_git))
    ml_tasks.append(insight_task.si(repo_git))
    ml_tasks.append(message_insight_task.si(repo_git))
    #ml_tasks.append(pull_request_analysis_task.si(repo_git)) 
    
    logger.info(f"Machine learning sequence: {ml_tasks}")
    return chain(*ml_tasks)