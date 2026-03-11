from typing import List
from sqlalchemy import text

from augur.improved_collection.collection import AugurCollection
from augur.improved_collection.models import CollectionType
from augur.improved_collection.rabbit_client import RabbitClient


def queue_tasks_for_running_collections(rabbit_client: RabbitClient) -> int:
    collections = AugurCollection.get_running_collections()

    tasks_to_queue = []

    for collection in collections:
        ready_tasks = collection.get_ready_to_queue_tasks()
        for task in ready_tasks:
            tasks_to_queue.append((collection.id, task))

    print(f"[scheduler] Found {len(tasks_to_queue)} tasks ready to queue across {len(collections)} collections", flush=True)

    if tasks_to_queue:
        augur_collection = AugurCollection(rabbit_client)

        for collection_id, task in tasks_to_queue:
            collection = next(c for c in collections if c.id == collection_id)
            augur_collection.update_task_to_queued(
                task_run_id=task.id,
                collection_id=collection_id,
                repo_id=collection.repo_id,
                task_name=task.name,
                task_type=task.task_type
            )

    return len(tasks_to_queue)


def start_collection_on_new_repos() -> List[int]:
    repo_ids = AugurCollection.find_repos_needing_initial_collection()

    print(f"[scheduler] Found {len(repo_ids)} new repos to start collection on", flush=True)

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


def retry_collection_on_failed_repos(rabbit_client: RabbitClient, retry_hours: int = 24) -> int:
    failed_collection_dicts = AugurCollection.find_failed_collections(retry_hours)

    collection_ids = [row['collection_id'] for row in failed_collection_dicts]

    print(f"[scheduler] Found {len(collection_ids)} failed collections to retry", flush=True)

    augur_collection = AugurCollection(rabbit_client)
    retry_count = 0

    for collection_id in collection_ids:
        if augur_collection.retry_failed_collection(collection_id):
            retry_count += 1

    print(f"[scheduler] Retried {retry_count} failed collections", flush=True)
    return retry_count


def start_recollection_on_collected_repos(recollection_days: int = 7) -> List[int]:
    repo_ids = AugurCollection.find_repos_needing_recollection(recollection_days)

    print(f"[scheduler] Found {len(repo_ids)} repos needing recollection", flush=True)

    collection_ids = []
    for repo_id in repo_ids:
        collection_type = AugurCollection.get_collection_type_for_repo(repo_id)
        collection_id = AugurCollection.create_new_collection_from_most_recent_workflow(
            repo_id,
            collection_type=collection_type
        )
        if collection_id:
            collection_ids.append(collection_id)

    return collection_ids


def trueup_collection_states(rabbit_client: RabbitClient):
    collections = AugurCollection.get_running_collections()

    collections_to_complete = []
    collections_to_fail = []

    for collection in collections:
        if collection.should_be_marked_complete():
            collections_to_complete.append(collection.id)
            print(f"[scheduler] Collection {collection.id} should be marked complete: all {len(collection.tasks)} tasks are complete", flush=True)
        elif collection.should_be_marked_failed():
            collections_to_fail.append(collection.id)

    if collections_to_complete or collections_to_fail:
        augur_collection = AugurCollection(rabbit_client)

        for collection_id in collections_to_complete:
            augur_collection.update_collection_to_complete(collection_id=collection_id)

        for collection_id in collections_to_fail:
            augur_collection.update_collection_to_failed(collection_id=collection_id)

    print(f"[scheduler] Trued up collection states: {len(collections_to_complete)} completed, {len(collections_to_fail)} failed", flush=True)


def schedule_collection(rabbit_client: RabbitClient, retry_hours: int = 24, recollection_days: int = 7):
    print("[scheduler] Starting collection scheduling cycle", flush=True)

    new_collection_ids = start_collection_on_new_repos()
    print(f"[scheduler] Started {len(new_collection_ids)} new collections", flush=True)

    retry_collection_on_failed_repos(rabbit_client, retry_hours)

    recollection_ids = start_recollection_on_collected_repos(recollection_days)
    print(f"[scheduler] Started {len(recollection_ids)} recollections", flush=True)

    trueup_collection_states(rabbit_client)

    queued_count = queue_tasks_for_running_collections(rabbit_client)
    print(f"[scheduler] Queued {queued_count} tasks for execution", flush=True)

    print("[scheduler] Collection scheduling cycle complete", flush=True)
