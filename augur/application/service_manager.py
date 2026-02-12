import sys
import os
import subprocess
from augur.application.logs import AugurLogger

logger = AugurLogger("augur_servicemanager").get_logger()


class AugurServiceManager:
    def __init__(self, ctx, pidfile, disable_collection):
        self.ctx = ctx
        self.pidfile = pidfile
        self.disable_collection = disable_collection
        self.server = None
        self.processes = []
        self.celery_beat_process = None
        self.keypub = None
        self.shutting_down = False

    def shutdown_signal_handler(self, signum, frame):
        if self.shutting_down:
            return
        
        self.shutting_down = True
        logger.info(f"Received signal {signum}, shutting down gracefully")

        # Stop server
        if self.server:
            logger.info("Stopping server")
            self.server.terminate()
            try:
                self.server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Server did not terminate in time, killing")
                self.server.kill()

        # Stop celery workers
        logger.info("Stopping celery workers")
        for p in self.processes:
            if p and p.poll() is None:
                p.terminate()
        
        # Wait for workers to terminate
        for p in self.processes:
            if p:
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Worker {p.pid} did not terminate in time, killing")
                    p.kill()

        # Stop celery beat
        if self.celery_beat_process:
            logger.info("Stopping celery beat")
            self.celery_beat_process.terminate()
            try:
                self.celery_beat_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                logger.warning("Celery beat did not terminate in time, killing")
                self.celery_beat_process.kill()

        # Cleanup collection resources
        if not self.disable_collection:
            try:
                if self.keypub:
                    self.keypub.shutdown()
                cleanup_collection_status_and_rabbit(logger, self.ctx.obj.engine)
            except Exception as e:
                logger.debug(f"Error during collection cleanup: {e}")

        # Remove pidfile
        if os.path.exists(self.pidfile):
            try:
                os.unlink(self.pidfile)
            except OSError as e:
                logger.error(f"Could not remove pidfile {self.pidfile}: {e}")

        sys.exit(0)
