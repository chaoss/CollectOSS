#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

from copy import deepcopy
import os, time, atexit, subprocess, click, atexit, logging, sys
import multiprocessing as mp
import gunicorn.app.base
from gunicorn.arbiter import Arbiter

from augur.housekeeper import Housekeeper
from augur.server import Server
from augur.cli.util import kill_processes
from augur.cli import pass_config, pass_application

logger = logging.getLogger("augur")

@click.command("run")
@click.option("--disable-housekeeper", is_flag=True, default=False, help="Turns off the housekeeper")
@click.option("--skip-cleanup", is_flag=True, default=False, help="Disables the old process cleanup that runs before Augur starts")
@pass_application
@click.pass_context
def cli(ctx, augur_app, disable_housekeeper, skip_cleanup):
    """
    Start Augur's backend server
    """
    if not skip_cleanup:
        logger.info("Cleaning up old Augur processes...")
        ctx.invoke(kill_processes)
        time.sleep(2)
    else:
        logger.info("Skipping cleanup...")

    master = initialize_components(augur_app, disable_housekeeper)
    logger.info('Starting Gunicorn server in the background...')
    logger.info('Housekeeper update process logs will now take over.')
    Arbiter(master).run()

def initialize_components(augur_app, disable_housekeeper):
    logger.info('Initializing...')
    master = None
    manager = None
    broker = None
    housekeeper = None
    worker_processes = []
    mp.set_start_method('forkserver', force=True)

    if not disable_housekeeper:
        logger.info("Booting broker and its manager...")
        manager = mp.Manager()
        broker = manager.dict()

        logger.info("Booting housekeeper...")
        housekeeper = Housekeeper(broker=broker, augur_app=augur_app)

        controller = augur_app.config.get_section('Workers')

        for worker in controller.keys():
            if controller[worker]['switch']:
                logger.debug("Your config has the option set to automatically boot {} instances of the {}".format(controller[worker]['workers'], worker))
                for i in range(controller[worker]['workers']):
                    logger.info("Booting {} #{}".format(worker, i + 1))
                    worker_process = mp.Process(target=worker_start, kwargs={'worker_name': worker, 'instance_number': i, 'worker_port': controller[worker]['port']}, daemon=True)
                    worker_processes.append(worker_process)
                    worker_process.start()

    augur_app.manager = manager
    augur_app.broker = broker
    augur_app.housekeeper = housekeeper

    # TODO: don't use gunicorn and multiprocessing in the same process...?
    atexit._clear()
    atexit.register(exit, augur_app, worker_processes, master)
    return AugurGunicornApp(augur_app.gunicorn_options, augur_app=augur_app)

def worker_start(worker_name=None, instance_number=0, worker_port=None):
    try:
        time.sleep(30 * instance_number)
        destination = subprocess.DEVNULL
        process = subprocess.Popen("cd workers/{} && {}_start".format(worker_name,worker_name), shell=True, stdout=destination, stderr=subprocess.STDOUT)
        logger.info("{} #{} booted.".format(worker_name,instance_number+1))
    except KeyboardInterrupt as e:
        pass

def exit(augur_app, worker_processes, master):

    logger.info("Beginning shutdown process")
    if augur_app.logging.stop_event is not None:
        augur_app.logging.stop_event.set()

    if worker_processes:
        for process in worker_processes:
            logger.debug("Shutting down worker process with pid: {}...".format(process.pid))
            process.terminate()

    if master is not None:
        logger.debug("Shutting down Gunicorn server...")
        master.halt()
        master = None

    if augur_app.housekeeper is not None:
        logger.debug("Shutting down housekeeper updates...")
        augur_app.housekeeper.shutdown_updates()
        augur_app.housekeeper = None

    if augur_app.manager is not None:
        logger.debug("Shutting down manager...")
        augur_app.manager.shutdown()
        augur_app.manager = None

    logger.info("Stopping main Augur process with PID: {}".format(os.getpid()))

class AugurGunicornApp(gunicorn.app.base.BaseApplication):
    """
    Loads configurations, initializes Gunicorn, loads server
    """

    def __init__(self, options={}, augur_app=None):
        self.options = options
        self.augur_app = augur_app
        self.manager = self.augur_app.manager
        self.broker = self.augur_app.broker
        self.housekeeper = self.augur_app.housekeeper
        self.server = None
        super(AugurGunicornApp, self).__init__()

    def load_config(self):
        """
        Sets the values for configurations
        """
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def get_augur_app(self):
        """
        Returns the loaded server
        """
        self.load()
        return self.server.augur_app

    def load(self):
        """
        Returns the loaded server
        """
        if self.server is None:
            try:
                self.server = Server(augur_app=self.augur_app)
            except Exception as e:
                logger.error(f"An error occured when Gunicorn tried to load the server: {e}")
        return self.server.app
