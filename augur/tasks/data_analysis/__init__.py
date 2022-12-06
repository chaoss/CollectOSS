from augur.tasks.data_analysis.clustering_worker.tasks import clustering_model
from augur.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker import contributor_breadth_model
from augur.tasks.data_analysis.discourse_analysis.tasks import discourse_analysis_model
from augur.tasks.data_analysis.insight_worker.tasks import insight_model
from augur.tasks.data_analysis.message_insights.tasks import message_insight_model
from augur.tasks.data_analysis.pull_request_analysis_worker.tasks import pull_request_analysis_model
from augur.application.db.session import DatabaseSession
from augur.application.db.models import Repo 
from augur.application.db.util import execute_session_query
from celery import group, chain, chord, signature

def machine_learning_phase(logger):

    with DatabaseSession(logger) as session:
        query = session.query(Repo)
        repos = execute_session_query(query, 'all')

    ml_tasks = []
    clustering_tasks = []
    discourse_tasks = []
    insight_tasks = []
    message_insights_tasks = []
    pull_request_analysis_tasks = []
    for repo in repos:
        clustering_tasks.append(clustering_model.si(repo.repo_git))
        discourse_tasks.append(discourse_analysis_model.si(repo.repo_git))
        insight_tasks.append(insight_model.si(repo.repo_git))
        message_insights_tasks.append(message_insight_model.si(repo.repo_git))
        pull_request_analysis_tasks.append(pull_request_analysis_model.si(repo.repo_git))   

    ml_tasks.extend(insight_tasks)
    ml_tasks.extend(discourse_tasks)
    ml_tasks.extend(message_insights_tasks)
    ml_tasks.extend(pull_request_analysis_tasks)
    ml_tasks.extend(clustering_tasks) 
        
    task_chain = chain(*ml_tasks)

    return task_chain