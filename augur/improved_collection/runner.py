import logging
import signal
import sys
import time

logger = logging.getLogger(__name__)
_running = True

def _configure_stdout_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


def _handle_shutdown(signum, frame):
    global _running
    logger.info(f"Received {signal.Signals(signum).name} — shutting down after current tick")
    _running = False


def run_scheduler(interval_seconds: int):
    global _running
    _configure_stdout_logging()
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    logger.info(f"Improved collection scheduler starting — interval={interval_seconds}s")
    tick = 0
    while _running:
        tick += 1
        logger.info(f"[tick={tick}] Scheduler tick starting")
        try:
            from augur.improved_collection.scheduler import schedule_collection
            schedule_collection()
            logger.info(f"[tick={tick}] Scheduler tick complete")
        except Exception:
            logger.exception(f"[tick={tick}] schedule_collection() raised an unhandled exception — will retry")
        for _ in range(interval_seconds):
            if not _running:
                break
            time.sleep(1)
    logger.info("Improved collection scheduler shut down cleanly")
