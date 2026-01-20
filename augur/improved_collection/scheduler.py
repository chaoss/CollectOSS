from typing import List
import logging
from sqlalchemy import text

from augur.improved_collection.collection import AugurCollection
from augur.improved_collection.models import CollectionType

logger = logging.getLogger(__name__)


def queue_tasks_for_running_collections() -> int:
    """Queue tasks that are ready to run for all active collections.
    
    Uses CollectionRun helper methods to identify tasks ready for queueing.
    Tasks are updated to 'Queued' state, and workers will update them to 
    'Collecting' when they actually start processing.
    
    Returns:
        Number of tasks queued.
    """
    collections = AugurCollection.get_running_collections()
    
    tasks_to_queue = []
    
    for collection in collections:

        ready_tasks = collection.get_ready_to_queue_tasks()
        
        for task in ready_tasks:
            tasks_to_queue.append((collection.id, task))
    
    logger.info(f"Found {len(tasks_to_queue)} tasks ready to queue across {len(collections)} collections")
    
    # Update task states to 'Queued' using AugurCollection domain class
    # Workers will update to 'Collecting' when they pick them up
    if tasks_to_queue:
        augur_collection = AugurCollection()
        
        for collection_id, task in tasks_to_queue:
            # Get repo_id from the collection
            collection = next(c for c in collections if c.id == collection_id)
            
            augur_collection.update_task_to_queued(
                task_run_id=task.id,
                collection_id=collection_id,
                repo_id=collection.repo_id,
                task_name=task.name
            )
    
    return len(tasks_to_queue)


def start_collection_on_new_repos() -> List[int]:
    """Start collection on repositories that have never been collected.
    
    Returns:
        List of collection IDs that were created.
    """
    repo_ids = AugurCollection.find_repos_needing_initial_collection()
    
    logger.info(f"Found {len(repo_ids)} new repos to start collection on")
    
    collection_ids = []
    for repo_id in repo_ids:
        collection_id = AugurCollection.create_new_collection_from_most_recent_workflow(
            repo_id,
            collection_type=CollectionType.FULL,
            is_new_repo=True
        )
        if collection_id:
            collection_ids.append(collection_id)
    
    return collection_ids

def retry_collection_on_failed_repos(retry_hours: int = 24) -> int:
    """Retry collection on repositories whose last collection failed.
    
    Resets failed tasks back to Pending and collection back to Collecting
    so they can be picked up by the scheduler again.
    
    Args:
        retry_hours: Number of hours to wait before retrying a failed collection.
        
    Returns:
        Number of collections that were retried.
    """
    failed_collection_dicts = AugurCollection.find_failed_collections(retry_hours)
    
    collection_ids = [row['collection_id'] for row in failed_collection_dicts]
    
    logger.info(f"Found {len(collection_ids)} failed collections to retry")
    
    augur_collection = AugurCollection()
    retry_count = 0
    
    for collection_id in collection_ids:
        if augur_collection.retry_failed_collection(collection_id):
            retry_count += 1
    
    logger.info(f"Retried {retry_count} failed collections")
    return retry_count

def start_recollection_on_collected_repos(recollection_days: int = 7) -> List[int]:
    """Start recollection on repositories whose last collection is older than specified days.
    
    Checks the force_full_collection flag for each repo to determine if it should be
    a full collection or incremental collection.
    
    Args:
        recollection_days: Number of days to wait before recollecting a repository.
        
    Returns:
        List of new collection IDs that were created for recollection.
    """
    repo_ids = AugurCollection.find_repos_needing_recollection(recollection_days)
    
    logger.info(f"Found {len(repo_ids)} repos needing recollection")
    
    collection_ids = []
    for repo_id in repo_ids:
        # Check if this repo needs a full collection
        collection_type = AugurCollection.get_collection_type_for_repo(repo_id)
        
        collection_id = AugurCollection.create_new_collection_from_most_recent_workflow(
            repo_id,
            collection_type=collection_type
        )
        if collection_id:
            collection_ids.append(collection_id)
    
    return collection_ids


def trueup_collection_states():
    """
    Defensive method to ensure no collections are stuck in a collecting state. 
    Generally these states should be updated by the task completed and failed events
    but in case they are not, this method will update them.
    
    Uses CollectionRun helper methods to determine if collections should be 
    marked as complete or failed.
    """
    collections = AugurCollection.get_running_collections()
    
    collections_to_complete = []
    collections_to_fail = []
    
    for collection in collections:
        # Use helper methods to check collection state
        if collection.should_be_marked_complete():
            collections_to_complete.append(collection.id)
            logger.debug(
                f"Collection {collection.id} should be marked complete: "
                f"all {len(collection.tasks)} tasks are complete"
            )
        elif collection.should_be_marked_failed():
            collections_to_fail.append(collection.id)
    
    # Update collection states using AugurCollection domain class
    if collections_to_complete or collections_to_fail:
        augur_collection = AugurCollection()
        
        for collection_id in collections_to_complete:
            
            augur_collection.update_collection_to_complete(
                collection_id=collection_id
            )
        
        for collection_id in collections_to_fail:
            
            augur_collection.update_collection_to_failed(
                collection_id=collection_id,
            )
    
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
    retry_collection_on_failed_repos(retry_hours)
    
    # Start recollection on old repos
    recollection_ids = start_recollection_on_collected_repos(recollection_days)
    logger.info(f"Started {len(recollection_ids)} recollections")

    # True up collection states
    trueup_collection_states()

    # Run this last so tasks for new collections are queued
    queued_count = queue_tasks_for_running_collections()
    logger.info(f"Queued {queued_count} tasks for execution")
    
    logger.info("Collection scheduling cycle complete")



