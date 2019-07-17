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

    # broker_switch = app.read_config('Controller', 'broker', 'AUGUR_BROKER', 0)
    # housekeeper_switch = app.read_config('Controller', 'housekeeper', 'AUGUR_HOUSEKEEPER', 0)
    github_worker_switch = app.read_config('Workers', 'github_worker', 'AUGUR_GH_WORKER', {"switch": 0})['switch']
    repo_info_worker_switch = app.read_config('Workers', 'repo_info_worker', 'AUGUR_INFO_WORKER', {"switch": 0})['switch']
    insight_worker_switch = app.read_config('Workers', 'insight_worker', 'AUGUR_INSIGHT_WORKER', {"switch": 0})['switch']
    controller = {
        # 'broker': broker_switch,
        # 'housekeeper': housekeeper_switch,
        'github_worker': github_worker_switch,
        'repo_info_worker': repo_info_worker_switch,
        'insight_worker': insight_worker_switch
    }
    # logger.info("Worker specs ('1' for components that are set to automatically boot): {}".format(str(controller)))
    manager = None
    broker = None
    housekeeper = None
    
    # if controller['broker'] == 1:
    logger.info("Booting broker and its manager")
    manager = mp.Manager()
    broker = manager.dict()
        # broker['worker_pids'] = manager.list()
        
    # if controller['housekeeper'] == 1:
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

    worker_pids = []
    process = subprocess.Popen(['ps', '-a'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, notused = process.communicate()
    # data = [(int(p), c) for p, c in [x.rstrip('\n').split(' ', 1) \
    #     for x in os.popen('ps h -eo pid:1,command')]]
    # for p in psutil.process_iter():
    #     logger.info(p)
    #     if 'nginx' in p.name() or 'nginx' in ' '.join(p.cmdline()):
    #         p.terminate()
    #         p.wait()
    try:
        for line in stdout.splitlines():
        # for line in data:
            logger.info(line)
            pid, cmdline = line.split(' ', 1)
            logger.info("HERE {}".format(type(cmdline)))
            if 'github_worker' in cmdline and github_worker_switch == 1:
                # logger.info(cmdline)
                logger.info("Killing: {}".format(line))
            if 'repo_info_worker' in cmdline and repo_info_worker_switch == 1:
                # logger.info(cmdline)
                logger.info("Killing: {}".format(line))
            if 'insight_worker' in cmdline and insight_worker_switch == 1:
                # logger.info(cmdline)
                logger.info("Killing: {}".format(line))
    except:
        pass

    if github_worker_switch == 1:
        gh_pids = get_process_id("/bin/sh -c cd workers/augur_worker_github && github_worker")
        worker_pids += gh_pids
        if len(gh_pids) > 0:
            worker_pids.append(gh_pids[0] + 1)
            gh_pids.append(gh_pids[0] + 1)
            logger.info("Found github worker pids: {}".format(gh_pids))
            for pid in gh_pids:
                try:
                    os.kill(pid, 9)
                except:
                    logger.info("Worker process {} already killed".format(pid))

        logger.info("Booting github worker")
        github_worker = mp.Process(target=github_worker_start, args=(), daemon=True)
        github_worker.start()
        time.sleep(2.5)

    if controller['repo_info_worker'] == 1:
        ri_pids = get_process_id("/bin/sh -c cd workers/gh_repo_info_worker && repo_info_worker")
        worker_pids += ri_pids
        if len(ri_pids) > 0:
            worker_pids.append(ri_pids[0] + 1)
            ri_pids.append(ri_pids[0] + 1)
            logger.info("Found repo info worker pids: {}".format(ri_pids))
            for pid in ri_pids:
                try:
                    os.kill(pid, 9)
                except:
                    logger.info("Worker process {} already killed".format(pid))

        logger.info("Booting repo_info worker")
        repo_info_worker = mp.Process(target=repo_info_worker_start, args=(), daemon=True)
        repo_info_worker.start()
        time.sleep(2.5)

    if controller['insight_worker'] == 1:
        insight_pids = get_process_id("/bin/sh -c cd workers/insight_worker && insight_worker")
        worker_pids += insight_pids
        if len(insight_pids) > 0:
            worker_pids.append(insight_pids[0] + 1)
            insight_pids.append(insight_pids[0] + 1)
            logger.info("Found repo info worker pids: {}".format(insight_pids))
            for pid in insight_pids:
                try:
                    os.kill(pid, 9)
                except:
                    logger.info("Worker process {} already killed".format(pid))

        logger.info("Booting insight worker")
        insight_worker = mp.Process(target=insight_worker_start, args=(), daemon=True)
        insight_worker.start()
        time.sleep(2.5)


    @atexit.register
    def exit():
        try:
            for pid in worker_pids:
                os.kill(pid, 9)
        except:
            logger.info("Worker process {} already killed".format(pid))
        if master is not None:
            master.halt()
        logger.info("Shutting down app updates...")
        app.shutdown_updates()
        logger.info("Finalizing config...")
        app.finalize_config()
        logger.info("Shutting down housekeeper updates...")
        if housekeeper is not None:
            housekeeper.shutdown_updates()

        if github_worker_switch == 1:
            logger.info("Shutting down github worker...")
            github_worker.terminate()
        if repo_info_worker_switch == 1:
            logger.info("Shutting down github worker...")
            repo_info_worker.terminate()
        if insight_worker_switch == 1:
            logger.info("Shutting down github worker...")
            insight_worker.terminate()
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

def github_worker_start():
    logger.info("Booting github worker")
    process = subprocess.Popen("cd workers/augur_worker_github && github_worker", shell=True)

def repo_info_worker_start():
    logger.info("Booting repo_info worker")
    process = subprocess.Popen("cd workers/gh_repo_info_worker && repo_info_worker", shell=True)

def insight_worker_start():
    logger.info("Booting insight worker")
    process = subprocess.Popen("cd workers/insight_worker && insight_worker", shell=True)
