"""
AugurCollection domain class for managing collection and task state transitions.

This class owns the responsibility for:
- Updating task states (Queued, Collecting, Complete, Failed)
- Updating collection states (Complete, Failed)
- Publishing events for all state transitions
"""

import logging
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from sqlalchemy import text

from augur.application.db.session import DatabaseSession
from augur.improved_collection.rabbit_client import RabbitClient
from augur.improved_collection.models import TaskRunState, CollectionType, TaskType

logger = logging.getLogger(__name__)


@dataclass
class TaskRunInfo:
    """Represents a task run with its dependencies."""
    id: int
    name: str
    task_type: TaskType
    state: TaskRunState
    start_date: Optional[datetime]
    dependency_states: Optional[List[TaskRunState]]
    
    def is_pending(self) -> bool:
        """Check if task is in Pending state."""
        return self.state == TaskRunState.PENDING
    
    def is_queued(self) -> bool:
        """Check if task is in Queued state."""
        return self.state == TaskRunState.QUEUED
    
    def is_collecting(self) -> bool:
        """Check if task is in Collecting state."""
        return self.state == TaskRunState.COLLECTING
    
    def is_complete(self) -> bool:
        """Check if task is in Complete state."""
        return self.state == TaskRunState.COMPLETE
    
    def is_failed(self) -> bool:
        """Check if task is in Failed state."""
        return self.state == TaskRunState.FAILED
    
    def all_dependencies_complete(self) -> bool:
        """Check if all dependencies are in Complete state."""
        if not self.dependency_states:
            return True
        return all(state == TaskRunState.COMPLETE for state in self.dependency_states)
    
    def is_ready_to_queue(self) -> bool:
        """Check if task is ready to be queued (pending with all deps complete)."""
        return self.is_pending() and self.all_dependencies_complete()


@dataclass
class CollectionRun:
    """Represents a collection run with all its tasks."""
    id: int
    repo_id: str
    workflow_id: int
    is_new_repo: bool
    tasks: List[TaskRunInfo]
    
    def get_queued_tasks(self) -> List[TaskRunInfo]:
        """Get all queued tasks."""
        return [task for task in self.tasks if task.is_queued()]
    
    def get_collecting_tasks(self) -> List[TaskRunInfo]:
        """Get all collecting tasks."""
        return [task for task in self.tasks if task.is_collecting()]
    
    def get_ready_to_queue_tasks(self) -> List[TaskRunInfo]:
        """Get all tasks that are ready to be queued."""
        return [task for task in self.tasks if task.is_ready_to_queue()]
    
    def all_tasks_complete(self) -> bool:
        """Check if all tasks in the collection are complete."""
        return len(self.tasks) > 0 and all(task.is_complete() for task in self.tasks)
    
    def has_failed_tasks(self) -> bool:
        """Check if collection has any failed tasks."""
        return any(task.is_failed() for task in self.tasks)
    
    def should_be_marked_complete(self) -> bool:
        """Check if collection should be marked as complete."""
        return self.all_tasks_complete()
    
    def should_be_marked_failed(self) -> bool:
        """Check if collection should be marked as failed.
        
        A collection should be failed if:
        - It has at least one failed task
        - No tasks are currently queued or collecting (nothing actively running)
        - No pending tasks are ready to queue (nothing can progress)
        """
        if not self.has_failed_tasks():
            return False
        
        # Check if there are any queued or collecting tasks (work in progress)
        if self.get_queued_tasks() or self.get_collecting_tasks():
            return False
        
        # If no tasks are ready to queue, nothing can progress
        return len(self.get_ready_to_queue_tasks()) == 0


class AugurCollection:
    """Domain class for managing collection and task lifecycle with event publishing."""
    
    def __init__(self, rabbit_client: Optional[RabbitClient] = None):
        """
        Initialize AugurCollection.
        
        Args:
            rabbit_client: Optional RabbitClient for publishing events.
                          If None, events will not be published (useful for testing).
        """
        self.rabbit_client = rabbit_client
        self.exchange = "augur.collection"
        self.source = "augur.collection.scheduler"
        self._topology_initialized = False
    
    def _ensure_topology_setup(self):
        """
        Ensure RabbitMQ topology is set up (called once on first publish).
        """
        if not self._topology_initialized and self.rabbit_client:
            self.setup_collection_topology()
            self._topology_initialized = True
    
    def _publish_event(self, event_type: str, routing_key: str, data: dict):
        """
        Publish an event to RabbitMQ.
        
        Args:
            event_type: CloudEvent type (e.g., 'TaskQueued')
            routing_key: Routing key for the message
            data: Event payload data
        """
        if self.rabbit_client:
            try:
                self.rabbit_client.publish(
                    exchange=self.exchange,
                    routing_key=routing_key,
                    data=data,
                    event_type=event_type,
                    source=self.source,
                    persistent=True
                )
                logger.debug(f"Published event {event_type} with routing key {routing_key}")
            except Exception as e:
                logger.error(f"Failed to publish event {event_type}: {e}")
        else:
            logger.debug(f"No RabbitClient configured, skipping event publish: {event_type}")
    
    def _publish_task_event(self, event_type: str, task_run_id: int, collection_id: int,
                           repo_id: str, task_name: str, task_type: TaskType,
                           state: str, stacktrace: Optional[str] = None):
        """
        Publish a task event to the appropriate exchange based on task type.
        
        Ensures topology is set up before publishing.
        
        Args:
            event_type: CloudEvent type (e.g., 'TaskQueued', 'TaskCompleted')
            task_run_id: ID of the task run
            collection_id: ID of the collection
            repo_id: Repository ID
            task_name: Name of the task
            task_type: Type of task (determines which exchange to publish to)
            state: Current state of the task
            stacktrace: Optional error stacktrace for failed tasks
        """
        # Ensure topology is set up
        self._ensure_topology_setup()
        
        # Determine exchange based on task type
        if task_type == TaskType.CORE:
            exchange = "augur.collection.core"
        elif task_type == TaskType.SECONDARY:
            exchange = "augur.collection.secondary"
        elif task_type == TaskType.FACADE:
            exchange = "augur.collection.facade"
        else:
            logger.error(f"Unknown task type: {task_type}")
            return
        
        # Build event data
        event_data = {
            "task_run_id": task_run_id,
            "collection_id": collection_id,
            "repo_id": repo_id,
            "task_name": task_name,
            "task_type": task_type.value,
            "state": state,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if stacktrace:
            event_data["stacktrace"] = stacktrace
        
        # Publish to appropriate exchange
        routing_key = f"{event_type}"
        
        if self.rabbit_client:
            try:
                self.rabbit_client.publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    data=event_data,
                    event_type=event_type,
                    source=self.source,
                    persistent=True
                )
                logger.debug(f"Published {event_type} to {exchange} with routing key {routing_key}")
            except Exception as e:
                logger.error(f"Failed to publish {event_type}: {e}")
        else:
            logger.debug(f"No RabbitClient configured, skipping event publish: {event_type}")
    
    def setup_collection_topology(self):
        """
        Declare RabbitMQ exchanges, queues, and bindings for the collection system.
        
        Creates:
        - Core exchange (topic) with Core queue bound to it
        - Secondary exchange (topic) with Secondary queue bound to it
        - Facade exchange (topic) with Facade queue bound to it
        
        Each queue is bound to its respective exchange with a wildcard routing key '#'
        to receive all messages published to that exchange.
        """
        if not self.rabbit_client:
            logger.warning("No RabbitClient configured, skipping topology setup")
            return
        
        try:
            # Core exchange and queue
            logger.info("Declaring Core exchange and queue")
            self.rabbit_client.configure_exchange(exchange="augur.collection.core", exchange_type="topic", durable=True)
            self.rabbit_client.configure_queue(queue="augur.collection.core", durable=True)
            self.rabbit_client.bind_queue(queue="augur.collection.core", exchange="augur.collection.core", routing_key="#")
            
            # Secondary exchange and queue
            logger.info("Declaring Secondary exchange and queue")
            self.rabbit_client.configure_exchange(exchange="augur.collection.secondary", exchange_type="topic", durable=True)
            self.rabbit_client.configure_queue(queue="augur.collection.secondary", durable=True)
            self.rabbit_client.bind_queue(queue="augur.collection.secondary", exchange="augur.collection.secondary", routing_key="#")
            
            # Facade exchange and queue
            logger.info("Declaring Facade exchange and queue")
            self.rabbit_client.configure_exchange(exchange="augur.collection.facade", exchange_type="topic", durable=True)
            self.rabbit_client.configure_queue(queue="augur.collection.facade", durable=True)
            self.rabbit_client.bind_queue(queue="augur.collection.facade", exchange="augur.collection.facade", routing_key="#")
            
            logger.info("Collection topology setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup collection topology: {e}")
            raise
    
    def update_task_to_queued(self, task_run_id: int, collection_id: int, 
                              repo_id: str, task_name: str, task_type: TaskType) -> bool:
        """
        Update a task to Queued state and publish a TaskQueued event.
        
        Args:
            task_run_id: ID of the task run to update
            collection_id: ID of the collection this task belongs to
            repo_id: Repository ID
            task_name: Name of the task
            task_type: Type of task (determines which exchange to publish to)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE task_runs
                    SET state = 'Queued'
                    WHERE id = :task_run_id
                """)
                session.execute_sql(update_sql.bindparams(task_run_id=task_run_id))
            
            logger.info(f"Updated task {task_name} (id: {task_run_id}) to Queued state")
            
            # Publish TaskQueued event
            self._publish_task_event(
                event_type="TaskQueued",
                task_run_id=task_run_id,
                collection_id=collection_id,
                repo_id=repo_id,
                task_name=task_name,
                task_type=task_type,
                state="Queued"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_run_id} to Queued: {e}")
            return False
    
    def update_task_to_collecting(self, task_run_id: int, collection_id: int,
                                   repo_id: str, task_name: str, task_type: TaskType) -> bool:
        """
        Update a task to Collecting state and publish a task.collecting event.
        
        Args:
            task_run_id: ID of the task run to update
            collection_id: ID of the collection this task belongs to
            repo_id: Repository ID
            task_name: Name of the task
            task_type: Type of task (determines which exchange to publish to)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE task_runs
                    SET state = 'Collecting', start_date = NOW()
                    WHERE id = :task_run_id
                """)
                session.execute_sql(update_sql.bindparams(task_run_id=task_run_id))
            
            logger.info(f"Updated task {task_name} (id: {task_run_id}) to Collecting state")
            
            # Publish task.collecting event
            self._publish_task_event(
                event_type="task.collecting",
                task_run_id=task_run_id,
                collection_id=collection_id,
                repo_id=repo_id,
                task_name=task_name,
                task_type=task_type,
                state="Collecting"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_run_id} to Collecting: {e}")
            return False
    
    def update_task_to_complete(self, task_run_id: int, collection_id: int,
                                repo_id: str, task_name: str, task_type: TaskType) -> bool:
        """
        Update a task to Complete state and publish a TaskCompleted event.
        
        Args:
            task_run_id: ID of the task run to update
            collection_id: ID of the collection this task belongs to
            repo_id: Repository ID
            task_name: Name of the task
            task_type: Type of task (determines which exchange to publish to)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE task_runs
                    SET state = 'Complete'
                    WHERE id = :task_run_id
                """)
                session.execute_sql(update_sql.bindparams(task_run_id=task_run_id))
            
            logger.info(f"Updated task {task_name} (id: {task_run_id}) to Complete state")
            
            # Publish TaskCompleted event
            self._publish_task_event(
                event_type="TaskCompleted",
                task_run_id=task_run_id,
                collection_id=collection_id,
                repo_id=repo_id,
                task_name=task_name,
                task_type=task_type,
                state="Complete"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_run_id} to Complete: {e}")
            return False
    
    def update_task_to_failed(self, task_run_id: int, collection_id: int,
                              repo_id: str, task_name: str, task_type: TaskType,
                              stacktrace: Optional[str] = None) -> bool:
        """
        Update a task to Failed state and publish a TaskFailed event.
        
        Args:
            task_run_id: ID of the task run to update
            collection_id: ID of the collection this task belongs to
            repo_id: Repository ID
            task_name: Name of the task
            task_type: Type of task (determines which exchange to publish to)
            stacktrace: Optional error stacktrace
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE task_runs
                    SET state = 'Failed', stacktrace = :stacktrace
                    WHERE id = :task_run_id
                """)
                session.execute_sql(update_sql.bindparams(
                    task_run_id=task_run_id,
                    stacktrace=stacktrace
                ))
            
            logger.info(f"Updated task {task_name} (id: {task_run_id}) to Failed state")
            
            # Publish TaskFailed event
            self._publish_task_event(
                event_type="TaskFailed",
                task_run_id=task_run_id,
                collection_id=collection_id,
                repo_id=repo_id,
                task_name=task_name,
                task_type=task_type,
                state="Failed",
                stacktrace=stacktrace
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task {task_run_id} to Failed: {e}")
            return False
    
    def update_collection_to_complete(self, collection_id: int) -> bool:
        """
        Update a collection to Complete state and publish a collection.completed event.
        
        Args:
            collection_id: ID of the collection to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE repo_collections
                    SET state = 'Complete', completed_on = NOW()
                    WHERE id = :collection_id
                """)
                session.execute_sql(update_sql.bindparams(collection_id=collection_id))
            
            logger.info(f"Updated collection {collection_id} to Complete state")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update collection {collection_id} to Complete: {e}")
            return False
    
    def update_collection_to_failed(self, collection_id: int) -> bool:
        """
        Update a collection to Failed state and publish a collection.failed event.
        
        Args:
            collection_id: ID of the collection to update
            repo_id: Repository ID
            workflow_id: Workflow ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                update_sql = text("""
                    UPDATE repo_collections
                    SET state = 'Failed', completed_on = NOW()
                    WHERE id = :collection_id
                """)
                session.execute_sql(update_sql.bindparams(collection_id=collection_id))
            
            logger.info(f"Updated collection {collection_id} to Failed state")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update collection {collection_id} to Failed: {e}")
            return False
    
    def retry_failed_task(self, task_run_id: int) -> bool:
        """
        Retry a single failed task by resetting it to Pending.
        Also updates the collection back to Collecting if it was Failed.
        Both updates happen in a single transaction.
        
        Args:
            task_run_id: ID of the failed task run to retry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                # Execute both updates in a single transaction
                with session.engine.begin() as connection:
                    # Reset the specific failed task to Pending
                    reset_task_sql = text("""
                        UPDATE task_runs
                        SET state = 'Pending', 
                            stacktrace = NULL,
                            start_date = NULL
                        WHERE id = :task_run_id
                        AND state = 'Failed'
                    """)
                    connection.execute(reset_task_sql.bindparams(task_run_id=task_run_id))
                    
                    # Update collection back to Collecting if it was Failed
                    # This uses the task's collection_record_id to find the collection
                    reset_collection_sql = text("""
                        UPDATE repo_collections
                        SET state = 'Collecting',
                            completed_on = NULL
                        WHERE id = (
                            SELECT collection_record_id 
                            FROM task_runs 
                            WHERE id = :task_run_id
                        )
                        AND state = 'Failed'
                    """)
                    connection.execute(reset_collection_sql.bindparams(task_run_id=task_run_id))
            
            logger.info(f"Reset failed task {task_run_id} for retry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry task {task_run_id}: {e}")
            return False
    
    def retry_failed_collection(self, collection_id: int) -> bool:
        """
        Retry a failed collection by resetting all failed tasks to Pending.
        Both the task and collection updates happen in a single transaction,
        so if either fails, both will be rolled back.
        
        Args:
            collection_id: ID of the failed collection to retry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with DatabaseSession(logger) as session:
                # Execute both updates in a single transaction
                with session.engine.begin() as connection:
                    # Reset failed tasks to Pending
                    reset_tasks_sql = text("""
                        UPDATE task_runs
                        SET state = 'Pending', 
                            stacktrace = NULL,
                            start_date = NULL
                        WHERE collection_record_id = :collection_id
                        AND state = 'Failed'
                    """)
                    connection.execute(reset_tasks_sql.bindparams(collection_id=collection_id))
                    
                    # Update collection back to Collecting
                    reset_collection_sql = text("""
                        UPDATE repo_collections
                        SET state = 'Collecting',
                            completed_on = NULL
                        WHERE id = :collection_id
                        AND state = 'Failed'
                    """)
                    connection.execute(reset_collection_sql.bindparams(collection_id=collection_id))
            
            logger.info(f"Reset failed collection {collection_id} for retry")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry collection {collection_id}: {e}")
            return False
    
    @staticmethod
    def get_running_collections() -> List[CollectionRun]:
        """Get all collection runs currently in 'Collecting' state with their tasks.
        
        Returns:
            List of CollectionRun objects, each containing their tasks and metadata.
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
                rc.is_new_repo,
                tr.id AS task_run_id,
                wt.task_name,
                wt.task_type,
                tr.state AS task_run_state,
                tr.start_date,
                -- Array of dependency task run states
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
            GROUP BY rc.id, rc.repo_id, rc.workflow_id, rc.is_new_repo, tr.id, wt.task_name, wt.task_type, tr.state, tr.start_date
            ORDER BY rc.id, tr.id;
        """)
        
        with DatabaseSession(logger) as session:
            result = session.fetchall_data_from_sql_text(get_tasks_for_collection_sql)
        
        # Group tasks by collection_id
        collections_dict = {}
        for row in result:
            collection_id = row['collection_id']
            
            if collection_id not in collections_dict:
                collections_dict[collection_id] = {
                    'collection_id': collection_id,
                    'repo_id': row['repo_id'],
                    'workflow_id': row['workflow_id'],
                    'is_new_repo': row['is_new_repo'],
                    'tasks': []
                }
            
            # Convert string states to enum
            task_state = TaskRunState(row['task_run_state'])
            task_type = TaskType(row['task_type'])
            dep_states = [TaskRunState(state) for state in row['depends_on_task_states']] if row['depends_on_task_states'] else None
            
            task = TaskRunInfo(
                id=row['task_run_id'],
                name=row['task_name'],
                task_type=task_type,
                state=task_state,
                start_date=row['start_date'],
                dependency_states=dep_states
            )
            collections_dict[collection_id]['tasks'].append(task)
        
        # Convert to CollectionRun objects
        return [
            CollectionRun(
                id=data['collection_id'],
                repo_id=data['repo_id'],
                workflow_id=data['workflow_id'],
                is_new_repo=data['is_new_repo'],
                tasks=data['tasks']
            )
            for data in collections_dict.values()
        ]
    
    @staticmethod
    def create_new_collection_from_most_recent_workflow(repo_id: str, collection_type: CollectionType = CollectionType.FULL, is_new_repo: bool = False) -> Optional[int]:
        """Create a new collection record and associated task runs for a repository.
        
        Args:
            repo_id: The repository ID to create a collection for.
            collection_type: Type of collection (full or incremental). Defaults to full.
            is_new_repo: Whether this is the first collection for a new repo. Defaults to False.
            
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
            INSERT INTO repo_collections (repo_id, workflow_id, origin, state, collection_type, is_new_repo)
            SELECT :repo_id, lw.workflow_id, 'automation', 'Collecting', :collection_type, :is_new_repo
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
                    create_new_collection_sql.bindparams(
                        repo_id=repo_id,
                        collection_type=collection_type.value,
                        is_new_repo=is_new_repo
                    )
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
    
    @staticmethod
    def find_repos_needing_initial_collection() -> List[str]:
        """Find repositories that have never been successfully collected.
        
        Returns:
            List of repo_ids that need initial collection.
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
        
        return [row['repo_id'] for row in result]
    
    @staticmethod
    def find_failed_collections(retry_hours: int) -> List[dict]:
        """Find failed collections that are ready to be retried.
        
        Args:
            retry_hours: Number of hours to wait before retrying a failed collection.
            
        Returns:
            List of dicts containing collection_id, repo_id, workflow_id, completed_on, state.
        """
        failed_sql = text("""    
        SELECT rc.id AS collection_id
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
        
        return [
            {
                'collection_id': row['collection_id'],
                'repo_id': row['repo_id'],
                'workflow_id': row['workflow_id'],
                'completed_on': row['completed_on'],
                'state': row['state']
            }
            for row in result
        ]
    
    @staticmethod
    def find_repos_needing_recollection(recollection_days: int) -> List[str]:
        """Find repositories whose last collection is older than specified days.
        
        Args:
            recollection_days: Number of days to wait before recollecting a repository.
            
        Returns:
            List of repo_ids that need recollection.
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
        
        return [row['repo_id'] for row in result]
    
    @staticmethod
    def get_collection_type_for_repo(repo_id: str) -> CollectionType:
        """Get the appropriate collection type for a repo based on its settings.
        
        Checks the force_full_collection flag in repo_collection_settings.
        If flag is TRUE, returns FULL and clears the flag.
        Otherwise returns INCREMENTAL.
        
        Args:
            repo_id: The repository ID to check.
            
        Returns:
            CollectionType.FULL if force_full_collection is set, otherwise INCREMENTAL.
        """
        check_flag_sql = text("""
            SELECT force_full_collection
            FROM repo_collection_settings
            WHERE repo_id = :repo_id
        """)
        
        try:
            with DatabaseSession(logger) as session:
                result = session.fetchall_data_from_sql_text(
                    check_flag_sql.bindparams(repo_id=repo_id)
                )
                
                if result and result[0]['force_full_collection']:
                    logger.info(f"Repo {repo_id} flagged for full collection")
                    # Clear the flag since we're about to create a full collection
                    AugurCollection.clear_force_full_collection(repo_id)
                    return CollectionType.FULL
                else:
                    return CollectionType.INCREMENTAL
                    
        except Exception as e:
            logger.error(f"Error checking force_full_collection for repo {repo_id}: {e}")
            # Default to incremental on error
            return CollectionType.INCREMENTAL
    
    @staticmethod
    def set_force_full_collection(repo_id: str) -> bool:
        """Set the force_full_collection flag for a repo.
        
        This will cause the next collection for this repo to be a full collection.
        
        Args:
            repo_id: The repository ID to flag.
            
        Returns:
            True if successful, False otherwise.
        """
        set_flag_sql = text("""
            INSERT INTO repo_collection_settings (repo_id, force_full_collection, updated_at)
            VALUES (:repo_id, TRUE, NOW())
            ON CONFLICT (repo_id) 
            DO UPDATE SET force_full_collection = TRUE, updated_at = NOW()
        """)
        
        try:
            with DatabaseSession(logger) as session:
                session.execute_sql(set_flag_sql.bindparams(repo_id=repo_id))
            
            logger.info(f"Set force_full_collection flag for repo {repo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set force_full_collection for repo {repo_id}: {e}")
            return False
    
    @staticmethod
    def clear_force_full_collection(repo_id: str) -> bool:
        """Clear the force_full_collection flag for a repo.
        
        Args:
            repo_id: The repository ID to clear the flag for.
            
        Returns:
            True if successful, False otherwise.
        """
        clear_flag_sql = text("""
            UPDATE repo_collection_settings
            SET force_full_collection = FALSE, updated_at = NOW()
            WHERE repo_id = :repo_id
        """)
        
        try:
            with DatabaseSession(logger) as session:
                session.execute_sql(clear_flag_sql.bindparams(repo_id=repo_id))
            
            logger.debug(f"Cleared force_full_collection flag for repo {repo_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear force_full_collection for repo {repo_id}: {e}")
            return False
