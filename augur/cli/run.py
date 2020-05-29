#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

from copy import deepcopy
import os, time, atexit, subprocess, click, atexit
import multiprocessing as mp
import gunicorn.app.base
from gunicorn.arbiter import Arbiter
from augur.housekeeper.housekeeper import Housekeeper

from augur import logger
from augur.server import Server
from augur.runtime import pass_application
from augur.cli.util import kill_processes

import time

@click.command("run")
@click.option("--disable-housekeeper", is_flag=True, default=False, help="Turns off the housekeeper")
@click.option("--skip-cleanup", is_flag=True, default=False, help="Disables the old process cleanup that runs before Augur starts")
@click.pass_context
def cli(ctx, disable_housekeeper, skip_cleanup):
    """
    Start Augur's backend server
    """
    if not skip_cleanup:
        logger.info("Cleaning up old Augur processes. Just a moment please...")
        ctx.invoke(kill_processes)
        time.sleep(2)
    else:
        logger.info("Skipping cleanup processes...")

    logger.info('Initialzing...')
    master = initialize_components(ctx.obj, disable_housekeeper)
    logger.info('Starting server...')
    Arbiter(master).run()

def initialize_components(augur_app, disable_housekeeper):
    master = None
    manager = None
    broker = None
    housekeeper = None
    worker_processes = []

    mp.set_start_method('forkserver', force=True)
    logger.info("Booting broker and its manager...")
    manager = mp.Manager()
    broker = manager.dict()

    atexit.register(exit, worker_processes, master, housekeeper, manager)

    if not disable_housekeeper:
        logger.info("Booting housekeeper...")
        jobs = deepcopy(augur_app.read_config('Housekeeper', 'jobs'))
        housekeeper = Housekeeper(
                jobs,
                broker,
                broker_host=augur_app.read_config('Server', 'host'),
                broker_port=augur_app.read_config('Server', 'port'),
                user=augur_app.read_config('Database', 'user'),
                password=augur_app.read_config('Database', 'password'),
                host=augur_app.read_config('Database', 'host'),
                port=augur_app.read_config('Database', 'port'),
                dbname=augur_app.read_config('Database', 'name')
            )
        logger.info("Housekeeper has finished booting.")

        controller = augur_app.read_config('Workers')

        for worker in controller.keys():
            if controller[worker]['switch']:
                logger.info("Your config has the option set to automatically boot {} instances of the {}".format(controller[worker]['workers'], worker))
                for i in range(controller[worker]['workers']):
                    logger.info("Booting {} #{}".format(worker, i + 1))
                    worker_process = mp.Process(target=worker_start, kwargs={'worker_name': worker, 'instance_number': i, 'worker_port': controller[worker]['port']}, daemon=True)
                    worker_process.start()
                    worker_processes.append(worker_process)

    host = augur_app.read_config('Server', 'host')
    port = augur_app.read_config('Server', 'port')
    workers = int(augur_app.read_config('Server', 'workers'))
    timeout = int(augur_app.read_config('Server', 'timeout'))
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': workers,
        'accesslog': '-',
        'access_log_format': '%(h)s - %(t)s - %(r)s',
        'timeout': timeout
    }
    return AugurGunicornApp(options, manager=manager, broker=broker, housekeeper=housekeeper, augur_app=augur_app)

def worker_start(worker_name=None, instance_number=0, worker_port=None):
    try:
        time.sleep(120 * instance_number)
        destination = subprocess.DEVNULL
        try:
            destination = open("workers/{}/worker_{}.log".format(worker_name, worker_port), "a+")
        except IOError as e:
            logger.error("Error opening log file for auto-started worker {}: {}".format(worker_name, e))
        process = subprocess.Popen("cd workers/{} && {}_start".format(worker_name,worker_name), shell=True, stdout=destination, stderr=subprocess.STDOUT)
        logger.info("{} #{} booted.".format(worker_name,instance_number+1))
    except KeyboardInterrupt as e:
        pass

def exit(worker_processes, master, housekeeper, manager):
    if worker_processes:
        for process in worker_processes:
            logger.info("Shutting down worker process with pid: {}...".format(process.pid))
            process.terminate()

    if master is not None:
        logger.info("Shutting down Gunicorn server...")
        master.halt()

    if housekeeper is not None:
        logger.info("Shutting down housekeeper updates...")
        housekeeper.shutdown_updates()

    if manager is not None:
        logger.info("Shutting down manager...")
        manager.shutdown()
    
    logger.info("Killing main augur process with PID: {}".format(os.getpid()))
    os._exit(0)

class AugurGunicornApp(gunicorn.app.base.BaseApplication):
    """
    Loads configurations, initializes Gunicorn, loads server
    """

    def __init__(self, options=None, manager=None, broker=None, housekeeper=None, augur_app=None):
        self.options = options or {}
        self.manager = manager
        self.broker = broker
        self.housekeeper = housekeeper
        self.augur_app = augur_app
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
            self.server = Server(manager=self.manager, broker=self.broker, housekeeper=self.housekeeper, augur_app=self.augur_app)
        return self.server.app
