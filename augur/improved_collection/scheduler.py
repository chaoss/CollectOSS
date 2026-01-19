from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import logging
from sqlalchemy import text

from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine

logger = logging.getLogger(__name__)


@dataclass
class TaskRunInfo:
    """Represents a task run with its dependencies for a collection."""
    collection_id: int
    repo_id: str
    workflow_id: int
    task_run_id: int
    workflow_task_id: int
    task_name: str
    task_run_state: str
    start_date: Optional[datetime]
    depends_on_task_ids: Optional[List[int]]
    depends_on_task_states: Optional[List[str]]


@dataclass
class NewRepoInfo:
    """Represents a repository that needs collection started."""
    repo_id: str


@dataclass
class FailedCollectionInfo:
    """Represents a failed collection that can be retried."""
    collection_id: int
    repo_id: str
    workflow_id: int
    completed_on: Optional[datetime]
    state: str


@dataclass
class RecollectionRepoInfo:
    """Represents a repository that needs recollection."""
    repo_id: str


@dataclass
class NewCollectionResult:
    """Represents the result of creating a new collection."""
    collection_record_id: int
    workflow_task_id: int
    state: str


def get_collection_info_for_running_collections() -> List[TaskRunInfo]:
    """Get all task run information for collections currently in 'Collecting' state.
    
    Returns:
        List of TaskRunInfo objects containing task details and their dependencies.
    """
    get_tasks_for_collection_sql = text("""
        WITH collecting_collections AS (
            SELECT *
            FROM repo_collections
            WHERE state = 'Collecting'
        )
        SELECT
            rc.id AS collection_id,
            rc.repo_id,
            rc.workflow_id,
            tr.id AS task_run_id,
            tr.workflow_task_id,
            wt.task_name,
            tr.state AS task_run_state,
            tr.start_date,
            -- Array of dependency task ids
            array_agg(wd.depends_on_workflow_task_id) FILTER (WHERE wd.depends_on_workflow_task_id IS NOT NULL) AS depends_on_task_ids,
            -- Array of dependency task run states (join to get states)
            array_agg(dep_tr.state) FILTER (WHERE dep_tr.state IS NOT NULL) AS depends_on_task_states
        FROM collecting_collections rc
        JOIN task_runs tr
            ON tr.collection_record_id = rc.id
        JOIN workflow_tasks wt
            ON wt.id = tr.workflow_task_id
        LEFT JOIN workflow_dependencies wd
            ON wd.workflow_task_id = wt.id
        LEFT JOIN task_runs dep_tr
            ON dep_tr.collection_record_id = rc.id
        AND dep_tr.workflow_task_id = wd.depends_on_workflow_task_id
        GROUP BY rc.id, rc.repo_id, rc.workflow_id, tr.id, tr.workflow_task_id, wt.task_name, tr.state, tr.start_date
        ORDER BY rc.id, tr.workflow_task_id;
    """)
    
    with DatabaseSession(logger) as session:
        result = session.fetchall_data_from_sql_text(get_tasks_for_collection_sql)
        
    return [
        TaskRunInfo(
            collection_id=row['collection_id'],
            repo_id=row['repo_id'],
            workflow_id=row['workflow_id'],
            task_run_id=row['task_run_id'],
            workflow_task_id=row['workflow_task_id'],
            task_name=row['task_name'],
            task_run_state=row['task_run_state'],
            start_date=row['start_date'],
            depends_on_task_ids=row['depends_on_task_ids'],
            depends_on_task_states=row['depends_on_task_states']
        )
        for row in result
    ]


def queue_tasks_for_running_collections():
    """Queue tasks that are ready to run for all active collections.
    
    A task is ready to run if:
    - It's in 'Pending' state
    - All its dependencies are in 'Complete' state
    
    Tasks are updated to 'Queued' state, and workers will update them to 
    'Collecting' when they actually start processing.
    """
    collection_info = get_collection_info_for_running_collections()
    
    tasks_to_queue = []
    
    for task_info in collection_info:
        # Only consider pending tasks
        if task_info.task_run_state != 'Pending':
            continue
            
        # Check if all dependencies are complete
        if task_info.depends_on_task_states:
            all_deps_complete = all(
                state == 'Complete' for state in task_info.depends_on_task_states
            )
            if not all_deps_complete:
                continue
        
        # Task is ready to queue
        tasks_to_queue.append(task_info)
    
    logger.info(f"Found {len(tasks_to_queue)} tasks ready to queue")
    
    # TODO: Use domain class to publish rabbit messages for these tasks
    # Update task states to 'Queued' - workers will update to 'Collecting' when they pick them up
    if tasks_to_queue:
        with DatabaseSession(logger) as session:
            for task in tasks_to_queue:
                update_sql = text("""
                    UPDATE task_runs
                    SET state = 'Queued'
                    WHERE id = :task_run_id
                """)
                session.execute_sql(update_sql.bindparams(task_run_id=task.task_run_id))
                
                logger.info(
                    f"Queued task {task.task_name} (id: {task.task_run_id}) "
                    f"for collection {task.collection_id}"
                )
    
    return tasks_to_queue


def start_collection_on_new_repos() -> List[int]:
    """Start collection on repositories that have never been collected.
    
    Returns:
        List of collection IDs that were created.
    """
    new_repo_sql = text("""    
    SELECT DISTINCT rc.repo_id
    FROM repo_collections rc
    LEFT JOIN task_runs tr 
        ON tr.collection_record_id = rc.id
    GROUP BY rc.repo_id
    HAVING COUNT(*) = 0
    OR NOT EXISTS (
        SELECT 1
        FROM repo_collections rc2
        JOIN task_runs tr2 ON tr2.collection_record_id = rc2.id
        WHERE rc2.repo_id = rc.repo_id
            AND tr2.state = 'Complete'
   );""")
    
    with DatabaseSession(logger) as session:
        result = session.fetchall_data_from_sql_text(new_repo_sql)
    
    new_repos = [NewRepoInfo(repo_id=row['repo_id']) for row in result]
    
    logger.info(f"Found {len(new_repos)} new repos to start collection on")
    
    collection_ids = []
    for repo in new_repos:
        collection_id = create_new_collection_from_most_recent_workflow(repo.repo_id)
        if collection_id:
            collection_ids.append(collection_id)
    
    return collection_ids

def retry_collection_on_failed_repos(retry_hours: int = 24):
    """Retry collection on repositories whose last collection failed.
    
    Args:
        retry_hours: Number of hours to wait before retrying a failed collection.
        
    Returns:
        List of new collection IDs that were created for retry.
    """
    failed_sql = text("""    
    SELECT rc.id AS collection_id,
        rc.repo_id,
        rc.workflow_id,
        rc.completed_on,
        rc.state
    FROM repo_collections rc
    JOIN (
        -- Get the last collection for each repo
        SELECT repo_id, MAX(id) AS last_collection_id
        FROM repo_collections
        GROUP BY repo_id
    ) lc ON rc.id = lc.last_collection_id
    WHERE rc.state = 'Failed'
    AND rc.completed_on < NOW() - INTERVAL ':retry_hours HOURS';
  """)
    
    with DatabaseSession(logger) as session:
        result = session.fetchall_data_from_sql_text(
            failed_sql.bindparams(retry_hours=retry_hours)
        )
    
    failed_collections = [
        FailedCollectionInfo(
            collection_id=row['collection_id'],
            repo_id=row['repo_id'],
            workflow_id=row['workflow_id'],
            completed_on=row['completed_on'],
            state=row['state']
        )
        for row in result
    ]
    
    logger.info(f"Found {len(failed_collections)} failed collections to retry")
    
    # TODO: Rather than creating a new collection,
    # I would like to figure out a way to restart each of the failed tasks so they are collected again
    # collection_ids = []
    # for failed in failed_collections:
    #     collection_id = create_new_collection_from_most_recent_workflow(failed.repo_id)
    #     if collection_id:
    #         collection_ids.append(collection_id)
    

def start_recollection_on_collected_repos(recollection_days: int = 7) -> List[int]:
    """Start recollection on repositories whose last collection is older than specified days.
    
    Args:
        recollection_days: Number of days to wait before recollecting a repository.
        
    Returns:
        List of new collection IDs that were created for recollection.
    """
    recollection_sql = text("""    
    SELECT rc.repo_id
    FROM repo_collections rc
    JOIN (
        SELECT repo_id, MAX(completed_on) AS last_completed
        FROM repo_collections
        WHERE completed_on IS NOT NULL
        GROUP BY repo_id
    ) lc ON rc.repo_id = lc.repo_id AND rc.completed_on = lc.last_completed
    WHERE rc.completed_on < NOW() - INTERVAL ':recollection_days DAYS';
   """)
    
    with DatabaseSession(logger) as session:
        result = session.fetchall_data_from_sql_text(
            recollection_sql.bindparams(recollection_days=recollection_days)
        )
    
    recollection_repos = [
        RecollectionRepoInfo(repo_id=row['repo_id']) for row in result
    ]
    
    logger.info(f"Found {len(recollection_repos)} repos needing recollection")
    
    collection_ids = []
    for repo in recollection_repos:
        collection_id = create_new_collection_from_most_recent_workflow(repo.repo_id)
        if collection_id:
            collection_ids.append(collection_id)
    
    return collection_ids
   


def create_new_collection_from_most_recent_workflow(repo_id: str) -> Optional[int]:
    """Create a new collection record and associated task runs for a repository.
    
    Args:
        repo_id: The repository ID to create a collection for.
        
    Returns:
        The collection ID if successful, None otherwise.
    """
    create_new_collection_sql = text("""
    WITH latest_workflow AS (
        SELECT id AS workflow_id
        FROM workflows
        ORDER BY id DESC
        LIMIT 1
    ),
    new_collection AS (
        INSERT INTO repo_collections (repo_id, workflow_id, origin, state)
        SELECT :repo_id, lw.workflow_id, 'automation', 'Collecting'
        FROM latest_workflow lw
        RETURNING id AS collection_id, workflow_id
    )
    INSERT INTO task_runs (collection_record_id, workflow_task_id, state)
    SELECT nc.collection_id, wt.id, 'Pending'
    FROM new_collection nc
    JOIN workflow_tasks wt
    ON wt.workflow_id = nc.workflow_id
    RETURNING collection_record_id, workflow_task_id, state;
    """)
    
    try:
        with DatabaseSession(logger) as session:
            result = session.fetchall_data_from_sql_text(
                create_new_collection_sql.bindparams(repo_id=repo_id)
            )
        
        if result:
            collection_id = result[0]['collection_record_id']
            logger.info(
                f"Created new collection {collection_id} for repo {repo_id} "
                f"with {len(result)} task runs"
            )
            return collection_id
        else:
            logger.warning(f"No workflow found to create collection for repo {repo_id}")
            return None
            
    except Exception as e:
        logger.error(f"Error creating collection for repo {repo_id}: {e}")
        return None

def trueup_collection_states():
    """
    Defensive method to ensure no collections are stuck in a collecting state. 
    Generally these states should be updated by the task completed and failed events
    but in case they are not, this method will update them.
    It marks collection as failed if they have a failed task run and no runnable tasks remain.
    It marks collection as complete if all tasks are complete and no runnable tasks remain.
    """
    collection_info = get_collection_info_for_running_collections()
    
    # Group tasks by collection_id
    collections = {}
    for task in collection_info:
        if task.collection_id not in collections:
            collections[task.collection_id] = []
        collections[task.collection_id].append(task)
    
    collections_to_complete = []
    collections_to_fail = []
    
    for collection_id, tasks in collections.items():
        task_states = [task.task_run_state for task in tasks]
        
        # Check if all tasks are complete
        if all(state == 'Complete' for state in task_states):
            collections_to_complete.append(collection_id)
            continue
        
        # Check if any task has failed and no tasks are pending or collecting
        has_failed = any(state == 'Failed' for state in task_states)
        has_runnable = any(state in ('Pending', 'Collecting') for state in task_states)
        
        if has_failed and not has_runnable:
            # Check if remaining pending tasks have failed dependencies
            all_blocked = True
            for task in tasks:
                if task.task_run_state == 'Pending':
                    # Check if dependencies allow this task to run
                    if task.depends_on_task_states:
                        if not any(state == 'Failed' for state in task.depends_on_task_states):
                            all_blocked = False
                            break
            
            if all_blocked:
                collections_to_fail.append(collection_id)
    
    # Update collection states
    if collections_to_complete or collections_to_fail:
        with DatabaseSession(logger) as session:
            for collection_id in collections_to_complete:
                update_sql = text("""
                    UPDATE repo_collections
                    SET state = 'Complete', completed_on = NOW()
                    WHERE id = :collection_id
                """)
                session.execute_sql(update_sql.bindparams(collection_id=collection_id))
                logger.info(f"Marked collection {collection_id} as Complete")
            
            for collection_id in collections_to_fail:
                update_sql = text("""
                    UPDATE repo_collections
                    SET state = 'Failed', completed_on = NOW()
                    WHERE id = :collection_id
                """)
                session.execute_sql(update_sql.bindparams(collection_id=collection_id))
                logger.info(f"Marked collection {collection_id} as Failed")
    
    logger.info(
        f"Trued up collection states: {len(collections_to_complete)} completed, "
        f"{len(collections_to_fail)} failed"
    )

def schedule_collection(retry_hours: int = 24, recollection_days: int = 7):
    """Main scheduler function that orchestrates all collection scheduling activities.
    
    Args:
        retry_hours: Hours to wait before retrying failed collections.
        recollection_days: Days to wait before recollecting completed repositories.
    """
    logger.info("Starting collection scheduling cycle")
    
    # Start collections on new repos
    new_collection_ids = start_collection_on_new_repos()
    logger.info(f"Started {len(new_collection_ids)} new collections")
    
    # Retry failed collections
    retry_collection_ids = retry_collection_on_failed_repos(retry_hours)
    logger.info(f"Retried {len(retry_collection_ids)} failed collections")
    
    # Start recollection on old repos
    recollection_ids = start_recollection_on_collected_repos(recollection_days)
    logger.info(f"Started {len(recollection_ids)} recollections")

    # True up collection states
    trueup_collection_states()

    # Run this last so tasks for new collections are queued
    queued_tasks = queue_tasks_for_running_collections()
    logger.info(f"Queued {len(queued_tasks)} tasks for execution")
    
    logger.info("Collection scheduling cycle complete")



