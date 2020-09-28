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
from augur.cli.util import stop_processes
from augur.application import Application

logger = logging.getLogger("augur")

@click.command("run")
@click.option("--disable-housekeeper", is_flag=True, default=False, help="Turns off the housekeeper")
@click.option("--skip-cleanup", is_flag=True, default=False, help="Disables the old process cleanup that runs before Augur starts")
def cli(disable_housekeeper, skip_cleanup):
    """
    Start Augur's backend server
    """
    augur_app = Application()
    logger.info("Augur application initialized")
    logger.info(f"Using config file: {augur_app.config.config_file_location}")
    if not skip_cleanup:
        logger.debug("Cleaning up old Augur processes...")
        stop_processes()
        time.sleep(2)
    else:
        logger.debug("Skipping process cleanup")

    master = initialize_components(augur_app, disable_housekeeper)
    logger.info('Starting Gunicorn server in the background...')
    if not disable_housekeeper:
        logger.info('Housekeeper update process logs will now take over.')
    else:
        logger.info("Gunicorn server logs will be written to gunicorn.log")
        logger.info("Augur is still running...don't close this process!")
    Arbiter(master).run()

def initialize_components(augur_app, disable_housekeeper):
    master = None
    manager = None
    broker = None
    housekeeper = None
    worker_processes = []
    mp.set_start_method('forkserver', force=True)

    if not disable_housekeeper:
        logger.info("Booting manager")
        manager = mp.Manager()

        logger.info("Booting broker")
        broker = manager.dict()

        housekeeper = Housekeeper(broker=broker, augur_app=augur_app)

        controller = augur_app.config.get_section('Workers')

        for worker in controller.keys():
            if controller[worker]['switch']:
                for i in range(controller[worker]['workers']):
                    logger.info("Booting {} #{}".format(worker, i + 1))
                    worker_process = mp.Process(target=worker_start, name=f"{worker}_{i}", kwargs={'worker_name': worker, 'instance_number': i, 'worker_port': controller[worker]['port']}, daemon=True)
                    worker_processes.append(worker_process)
                    worker_process.start()

    augur_app.manager = manager
    augur_app.broker = broker
    augur_app.housekeeper = housekeeper

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

        logger.info("Shutdown started for this Gunicorn worker...")
        augur_app.shutdown()

        if worker_processes:
            for process in worker_processes:
                logger.debug("Shutting down worker process with pid: {}...".format(process.pid))
                process.terminate()

        if master is not None:
            logger.debug("Shutting down Gunicorn server")
            master.halt()

        logger.info("Shutdown complete")
        sys.exit(0)

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
        logger.debug(f"Gunicorn will start {self.options['workers']} worker processes")
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
