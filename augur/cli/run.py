import click
import os
import sys
from augur.runtime import pass_application
from augur.util import logger
from augur.server import Server
import gunicorn.app.base
from gunicorn.six import iteritems
from gunicorn.arbiter import Arbiter
import multiprocessing as mp
from augur.housekeeper.housekeeper import Housekeeper
import sched
import os
import time
import sys
import atexit
import click
import subprocess
# import psutil

class AugurGunicornApp(gunicorn.app.base.BaseApplication):
    """
    Loads configurations, initializes Gunicorn, loads server
    """

    def __init__(self, options=None, manager=None, broker=None, housekeeper=None):
        self.options = options or {}
        self.manager = manager
        self.broker = broker
        self.housekeeper = housekeeper
        super(AugurGunicornApp, self).__init__()
        # self.cfg.pre_request.set(pre_request)

    def load_config(self):
        """
        Sets the values for configurations
        """
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        """
        Returns the loaded server
        """
        server = Server(manager=self.manager, broker=self.broker, housekeeper=self.housekeeper)
        return server.app

@click.command('run', short_help='Run the Augur server')
@pass_application
def cli(app):

    def get_process_id(name):
        """Return process ids found by name or command
        """
        child = subprocess.Popen(['pgrep', '-f', name], stdout=subprocess.PIPE, shell=False)
        response = child.communicate()[0]
        return [int(pid) for pid in response.split()]

    mp.set_start_method('forkserver', force=True)
    app.schedule_updates()
    master = None

    broker_switch = app.read_config('Controller', 'broker', 'AUGUR_BROKER', 0)
    housekeeper_switch = app.read_config('Controller', 'housekeeper', 'AUGUR_HOUSEKEEPER', 0)
    github_worker_switch = app.read_config('Controller', 'github_worker', 'AUGUR_GH_WORKER', 0)
    controller = {
        'broker': broker_switch,
        'housekeeper': housekeeper_switch,
        'github_worker': github_worker_switch,
    }

    logger.info("Controller specs ('1' for components that are set to automatically boot): {}".format(str(controller)))

    manager = None
    broker = None
    housekeeper = None
    
    if controller['broker'] == 1:
        logger.info("Booting broker and its manager")
        manager = mp.Manager()
        broker = manager.dict()
        # broker['worker_pids'] = manager.list()
        
    if controller['housekeeper'] == 1:
        logger.info("Booting housekeeper")
        jobs = app.read_config('Housekeeper', 'jobs', 'AUGUR_JOBS', [])
        housekeeper = Housekeeper(
                jobs,
                broker,
                broker_port=app.read_config('Server', 'port', 'AUGUR_PORT', '5000'),
                user=app.read_config('Database', 'user', 'AUGUR_DB_USER', 'root'),
                password=app.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password'),
                host=app.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1'),
                port=app.read_config('Database', 'port', 'AUGUR_DB_PORT', '3306'),
                dbname=app.read_config('Database', 'database', 'AUGUR_DB_NAME', 'msr14')
            )

    if controller['github_worker'] == 1:
        gh_pids = get_process_id("/bin/sh -c cd workers/augur_worker_github && github_worker")
        logger.info(gh_pids)
        if len(gh_pids) > 0:
            gh_pids.append(gh_pids[0] + 1)
            for pid in gh_pids:
                try:
                    os.kill(pid, 9)
                except:
                    logger.info("Worker process {} already killed".format(pid))

        # proc_iter = psutil.process_iter(attrs=["pid", "name", "cmdline"])
        # past_worker = any("/bin/sh -c cd workers/augur_worker_github && github_worker" in p.info["cmdline"] for p in proc_iter)
        # logger.info(str(past_worker))

        logger.info("Booting github worker")
        logger.info("abt to call method")
        up = mp.Process(target=worker_start, args=(), daemon=True)
        up.start()

    @atexit.register
    def exit():
        # try:
        #     for pid in broker['worker_pids']:
        #         os.kill(pid, 9)
        # except:
        #     logger.info("Worker process {} already killed".format(pid))
        if master is not None:
            master.halt()
        logger.info("Shutting down app updates...")
        app.shutdown_updates()
        logger.info("Finalizing config...")
        app.finalize_config()
        logger.info("Shutting down housekeeper updates...")
        if housekeeper is not None:
            housekeeper.shutdown_updates()

        if controller['github_worker'] == 1:
            for pid in gh_pids:
                try:
                    os.kill(pid, 9)
                    logger.info("killed worker process {}".format(pid))
                except:
                    logger.info("Worker process {} already killed".format(pid))
            # logger.info("You had the github_worker startup enabled, please allow ~30 seconds for its processes to shutdown before running 'make dev' again")
            logger.info("Shutting down github worker...")

            up.terminate()
        # if hasattr(manager, "shutdown"):
            # wait for the spawner and the worker threads to go down
            # 
        if manager is not None:
            manager.shutdown()
            # check if it is still alive and kill it if necessary
            # if manager._process.is_alive():
            manager._process.terminate()
        
        
        # Prevent multiprocessing's atexit from conflicting with gunicorn
        # logger.info("killing self: {}".format(os.getpid()))
        # os.kill(os.getpid(), 9)
        # os._exit(0)


    host = app.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = app.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    workers = int(app.read_config('Server', 'workers', 'AUGUR_WORKERS', mp.cpu_count()))
    options = {
        'bind': '%s:%s' % (host, port),
        'workers': workers,
        'accesslog': '-',
        'access_log_format': '%(h)s - %(t)s - %(r)s',
    }
    logger.info('Starting server...')
    master = Arbiter(AugurGunicornApp(options, manager=manager, broker=broker, housekeeper=housekeeper)).run()

def worker_start():
    logger.info("Booting github worker")
    process = subprocess.Popen("cd workers/augur_worker_github && github_worker", shell=True)
