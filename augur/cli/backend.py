#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""

from copy import deepcopy
import os, time, atexit, subprocess, click, atexit, logging, sys
import psutil
import signal
import multiprocessing as mp
import gunicorn.app.base
from gunicorn.arbiter import Arbiter

from augur.cli import initialize_logging, pass_config, pass_application
from augur.housekeeper import Housekeeper
from augur.server import Server
from augur.application import Application
from augur.gunicorn import AugurGunicornApp

logger = logging.getLogger("augur")

@click.group('server', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    pass

@cli.command("start")
@click.option("--disable-housekeeper", is_flag=True, default=False, help="Turns off the housekeeper")
@click.option("--skip-cleanup", is_flag=True, default=False, help="Disables the old process cleanup that runs before Augur starts")
@click.option("--logstash", is_flag=True, default=False, help="Runs logstash to collect errors from logs")
@click.option("--logstash-with-cleanup", is_flag=True, default=False, help="Runs logstash to collect errors from logs and cleans all previously collected errors")
def start(disable_housekeeper, skip_cleanup, logstash, logstash_with_cleanup):
    """
    Start Augur's backend server
    """
    augur_app = Application()
    logger.info("Augur application initialized")
    logger.info(f"Using config file: {augur_app.config.config_file_location}")
    if not skip_cleanup:
        logger.debug("Cleaning up old Augur processes...")
        _broadcast_signal_to_processes()
        time.sleep(2)
    else:
        logger.debug("Skipping process cleanup")

    if logstash or logstash_with_cleanup:
        augur_home = os.getenv('ROOT_AUGUR_DIRECTORY', "")
        if logstash_with_cleanup:
            print("Cleaning old workers errors...")
            with open(augur_home + "/log_analysis/http/empty_index.html") as f:
                lines = f.readlines()
            with open(augur_home + "/log_analysis/http/index.html", "w") as f1:
                f1.writelines(lines)
            print("All previous workers errors got deleted.")

        elasticsearch_path = os.getenv('ELASTIC_SEARCH_PATH', "/usr/local/bin/elasticsearch")
        subprocess.Popen(elasticsearch_path)
        logstash_path = os.getenv('LOGSTASH_PATH', "/usr/local/bin/logstash")
        subprocess.Popen([logstash_path, "-f", augur_home + "/log_analysis/logstash-filter.conf"])

    master = initialize_components(augur_app, disable_housekeeper)

    logger.info('Starting Gunicorn webserver...')
    logger.info(f'Augur is running at: http://127.0.0.1:{augur_app.config.get_value("Server", "port")}')
    logger.info('Gunicorn server logs & errors will be written to logs/gunicorn.log')
    logger.info('Housekeeper update process logs will now take over.')
    Arbiter(master).run()

@cli.command('stop')
@initialize_logging
def stop():
    """
    Sends SIGTERM to all Augur server & worker processes
    """
    _broadcast_signal_to_processes(given_logger=logging.getLogger("augur.cli"))

@cli.command('kill')
@initialize_logging
def kill():
    """
    Sends SIGKILL to all Augur server & worker processes
    """
    _broadcast_signal_to_processes(signal=signal.SIGKILL, given_logger=logging.getLogger("augur.cli"))

@cli.command('export-env')
@pass_config
def export_env(config):
    """
    Exports your GitHub key and database credentials
    """

    export_file = open(os.getenv('AUGUR_EXPORT_FILE', 'augur_export_env.sh'), 'w+')
    export_file.write('#!/bin/bash')
    export_file.write('\n')
    env_file = open(os.getenv('AUGUR_ENV_FILE', 'docker_env.txt'), 'w+')

    for env_var in config.get_env_config().items():
        if "LOG" not in env_var[0]:
            logger.info(f"Exporting {env_var[0]}")
            export_file.write('export ' + env_var[0] + '="' + str(env_var[1]) + '"\n')
            env_file.write(env_var[0] + '=' + str(env_var[1]) + '\n')

    export_file.close()
    env_file.close()

@cli.command('repo-reset')
@pass_application
def repo_reset(augur_app):
    """
    Refresh repo collection to force data collection
    """
    augur_app.database.execute("UPDATE augur_data.repo SET repo_path = NULL, repo_name = NULL, repo_status = 'New'; TRUNCATE augur_data.commits CASCADE; ")

    logger.info("Repos successfully reset")

@cli.command('processes')
@initialize_logging
def processes():
    """
    Outputs the name/PID of all Augur server & worker processes"""
    logger = logging.getLogger("augur.cli")
    processes = get_augur_processes()
    for process in processes:
        logger.info(f"Found process {process.pid}")

def get_augur_processes():
    processes = []
    for process in psutil.process_iter(['cmdline', 'name', 'environ']):
        if process.info['cmdline'] is not None and process.info['environ'] is not None:
            try:
                if os.getenv('VIRTUAL_ENV') in process.info['environ']['VIRTUAL_ENV'] and 'python' in ''.join(process.info['cmdline'][:]).lower():
                    if process.pid != os.getpid():
                        processes.append(process)
            except KeyError:
                pass
    return processes

def _broadcast_signal_to_processes(signal=signal.SIGTERM, given_logger=None):
    if given_logger is None:
        _logger = logger
    else:
        _logger = given_logger
    processes = get_augur_processes()
    if processes != []:
        for process in processes:
            if process.pid != os.getpid():
                logger.info(f"Stopping process {process.pid}")
                try:
                    process.send_signal(signal)
                except psutil.NoSuchProcess as e:
                    pass

def initialize_components(augur_app, disable_housekeeper):
    master = None
    manager = None
    broker = None
    housekeeper = None
    worker_processes = []
    mp.set_start_method('forkserver', force=True)

    if not disable_housekeeper:

        manager = mp.Manager()
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
