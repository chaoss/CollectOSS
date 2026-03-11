"""
Worker process that consumes task events from one of the three collection queues
(core, secondary, or facade) and prints them to stdout.
"""

import json
import logging
import signal
import sys

from augur.application.db.lib import get_value
from augur.improved_collection.collection import AugurCollection
from augur.improved_collection.models import TaskType
from augur.improved_collection.rabbit_client import RabbitClient

logger = logging.getLogger(__name__)


def _configure_stdout_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logging.getLogger().setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)


def _handle_event(attributes: dict, data: dict):
    """Handle an incoming task event by printing it to stdout."""
    print(
        json.dumps(
            {
                "cloudevent": {
                    "id": attributes.get("id"),
                    "type": attributes.get("type"),
                    "source": attributes.get("source"),
                    "time": attributes.get("time"),
                },
                "data": data,
            },
            indent=2,
            default=str,
        )
    )


def run_worker(task_type: TaskType):
    """
    Start a blocking consumer for the given task type queue.

    Args:
        task_type: Which queue to consume from (CORE, SECONDARY, or FACADE).
    """
    _configure_stdout_logging()

    amqp_url = get_value("RabbitMQ", "connection_string")
    client = RabbitClient(amqp_url)

    # TODO: Potentially move queue name resollution into thin module to reduce coupling to AugurCollection class
    queue = AugurCollection.get_queue_name(task_type)
    print(f"Worker starting — queue={queue}")

    # Register shutdown handlers so Ctrl-C / SIGTERM exit cleanly.
    def _shutdown(signum, frame):
        print(f"Received {signal.Signals(signum).name} — stopping consumer")
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    client.consume(queue=queue, handler=_handle_event, auto_ack=False)


def main():
    """
    CLI entry point.

    Usage:
        python -m augur.improved_collection.worker <core|secondary|facade>
    """
    print("Trying to start worker")
    if len(sys.argv) != 2 or sys.argv[1] not in {t.value for t in TaskType}:
        print(f"Usage: {sys.argv[0]} <{'|'.join(t.value for t in TaskType)}>")
        sys.exit(1)

    task_type = TaskType(sys.argv[1])
    run_worker(task_type)


if __name__ == "__main__":
    main()
