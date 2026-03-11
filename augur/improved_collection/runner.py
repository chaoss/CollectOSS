import logging
import signal
import sys
import time

from augur.application.db.lib import get_value
from augur.improved_collection.rabbit_client import RabbitClient

logger = logging.getLogger(__name__)
_running = True

def _configure_stdout_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def _handle_shutdown(signum, frame):
    global _running
    print(f"Received {signal.Signals(signum).name} — shutting down after current tick", flush=True)
    _running = False


def run_scheduler(interval_seconds: int):
    global _running
    _configure_stdout_logging()
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    print(f"Improved collection scheduler starting — interval={interval_seconds}s", flush=True)

    amqp_url = get_value("RabbitMQ", "connection_string")
    rabbit_client = RabbitClient(amqp_url)

    tick = 0
    while _running:
        tick += 1
        print(f"[tick={tick}] Scheduler tick starting", flush=True)
        try:
            from augur.improved_collection.scheduler import schedule_collection
            schedule_collection(rabbit_client)
            print(f"[tick={tick}] Scheduler tick complete", flush=True)
        except Exception as e:
            import traceback
            print(f"[tick={tick}] schedule_collection() raised an unhandled exception — will retry", flush=True)
            traceback.print_exc()
        for _ in range(interval_seconds):
            if not _running:
                break
            time.sleep(1)
    print("Improved collection scheduler shut down cleanly", flush=True)
