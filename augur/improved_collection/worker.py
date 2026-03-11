"""
Worker process that consumes task events from one of the three collection queues
(core, secondary, or facade) and processes them by transitioning task state
through Collecting → sleep → Complete.
"""

import logging
import signal
import sys
import time

from augur.application.db.lib import get_value
from augur.improved_collection.collection import AugurCollection
from augur.improved_collection.models import TaskType
from augur.improved_collection.rabbit_client import RabbitClient

logger = logging.getLogger(__name__)

_DEFAULT_COLLECTION_SLEEP_SECONDS = 45


def _configure_stdout_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)


def _make_handler(collection: AugurCollection, sleep_seconds: int):
    """Return an event handler that processes a task through its lifecycle."""

    def _handle_event(attributes: dict, data: dict):
        task_run_id = data.get("task_run_id")
        collection_id = data.get("collection_id")
        repo_id = data.get("repo_id")
        task_name = data.get("task_name", "unknown")
        task_type_value = data.get("task_type")

        try:
            task_type = TaskType(task_type_value)
        except (ValueError, TypeError):
            logger.error(f"Unknown task_type '{task_type_value}' for task_run_id={task_run_id}; skipping")
            return

        logger.info(f"Received task task_run_id={task_run_id} task={task_name} repo={repo_id}")

        collection.update_task_to_collecting(
            task_run_id=task_run_id,
            collection_id=collection_id,
            repo_id=repo_id,
            task_name=task_name,
            task_type=task_type,
        )

        logger.info(f"Sleeping {sleep_seconds}s for task_run_id={task_run_id}")
        time.sleep(sleep_seconds)

        collection.update_task_to_complete(
            task_run_id=task_run_id,
            collection_id=collection_id,
            repo_id=repo_id,
            task_name=task_name,
            task_type=task_type,
        )

        logger.info(f"Completed task_run_id={task_run_id}")

    return _handle_event


def run_worker(task_type: TaskType):
    """
    Start a blocking consumer for the given task type queue.

    Args:
        task_type: Which queue to consume from (CORE, SECONDARY, or FACADE).
    """
    _configure_stdout_logging()

    amqp_url = get_value("RabbitMQ", "connection_string")
    client = RabbitClient(amqp_url)

    try:
        sleep_seconds = int(get_value("Worker", "collection_sleep_seconds"))
    except Exception:
        sleep_seconds = _DEFAULT_COLLECTION_SLEEP_SECONDS

    collection = AugurCollection(rabbit_client=None)

    # TODO: Potentially move queue name resolution into thin module to reduce coupling to AugurCollection class
    queue = AugurCollection.get_queue_name(task_type)
    logger.info(f"Worker starting — queue={queue}, sleep_seconds={sleep_seconds}")

    # Register shutdown handlers so Ctrl-C / SIGTERM exit cleanly.
    def _shutdown(signum, frame):
        logger.info(f"Received {signal.Signals(signum).name} — stopping consumer")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    handler = _make_handler(collection, sleep_seconds)
    client.consume(queue=queue, handler=handler, auto_ack=False)


def main():
    """
    CLI entry point.

    Usage:
        python -m augur.improved_collection.worker <core|secondary|facade>
    """
    if len(sys.argv) != 2 or sys.argv[1] not in {t.value for t in TaskType}:
        print(f"Usage: {sys.argv[0]} <{'|'.join(t.value for t in TaskType)}>")
        sys.exit(1)

    task_type = TaskType(sys.argv[1])
    run_worker(task_type)


if __name__ == "__main__":
    main()
