#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""
import resource
import os
import time
import subprocess
import click
import logging
import psutil
import signal
import sys
from redis.exceptions import ConnectionError as RedisConnectionError
from celery import chain, signature, group
import uuid
import traceback
from urllib.parse import urlparse
from datetime import datetime

from augur import instance_id
from augur.tasks.start_tasks import augur_collection_monitor, CollectionState, create_collection_status_records
from augur.tasks.git.facade_tasks import clone_repos
from augur.tasks.data_analysis.contributor_breadth_worker.contributor_breadth_worker import contributor_breadth_model
from augur.tasks.init.redis_connection import redis_connection 
from augur.application.db.models import Repo, CollectionStatus, UserRepo
from augur.application.db.session import DatabaseSession
from augur.application.db.util import execute_session_query
from augur.application.logs import AugurLogger
from augur.application.config import AugurConfig
from augur.application.cli import test_connection, test_db_connection 
import sqlalchemy as s
from sqlalchemy import or_, and_


logger = AugurLogger("augur", reset_logfiles=True).get_logger()



@click.group('server', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    pass

@cli.command("start")
@click.option("--disable-collection", is_flag=True, default=False, help="Turns off data collection workers")
@click.option("--development", is_flag=True, default=False, help="Enable development mode, implies --disable-collection")
@click.option('--port')
@test_connection
@test_db_connection
def start(disable_collection, development, port):
    """Start Augur's backend server."""

    try:
        if os.environ.get('AUGUR_DOCKER_DEPLOY') != "1":
            raise_open_file_limit(100000)
    except Exception as e: 
        logger.error(
                    ''.join(traceback.format_exception(None, e, e.__traceback__)))
        
        logger.error("Failed to raise open file limit!")
        raise e
    
    if development:
        os.environ["AUGUR_DEV"] = "1"
        logger.info("Starting in development mode")

    try:
        gunicorn_location = os.getcwd() + "/augur/api/gunicorn_conf.py"
    except FileNotFoundError:
        logger.error("\n\nPlease run augur commands in the root directory\n\n")

    with DatabaseSession(logger) as db_session:
        config = AugurConfig(logger, db_session)
        host = config.get_value("Server", "host")

        if not port:
            port = config.get_value("Server", "port")
        
        worker_vmem_cap = config.get_value("Celery", 'worker_process_vmem_cap')

    gunicorn_command = f"gunicorn -c {gunicorn_location} -b {host}:{port} augur.api.server:app --log-file gunicorn.log"
    server = subprocess.Popen(gunicorn_command.split(" "))

    time.sleep(3)
    logger.info('Gunicorn webserver started...')
    logger.info(f'Augur is running at: {"http" if development else "https"}://{host}:{port}')

    processes = start_celery_worker_processes(float(worker_vmem_cap), disable_collection)

    if os.path.exists("celerybeat-schedule.db"):
            logger.info("Deleting old task schedule")
            os.remove("celerybeat-schedule.db")

    celery_beat_process = None
    celery_command = "celery -A augur.tasks.init.celery_app.celery_app beat -l debug"
    celery_beat_process = subprocess.Popen(celery_command.split(" "))    

    if not disable_collection:

        with DatabaseSession(logger) as session:

            clean_collection_status(session)
            assign_orphan_repos_to_default_user(session)
        
        create_collection_status_records.si().apply_async()
        time.sleep(3)

        contributor_breadth_model.si().apply_async()

        # start cloning repos when augur starts
        clone_repos.si().apply_async()

        augur_collection_monitor.si().apply_async()
        
    else:
        logger.info("Collection disabled")   
    
    try:
        server.wait()
    except KeyboardInterrupt:
        
        if server:
            logger.info("Shutting down server")
            server.terminate()

        logger.info("Shutting down all celery worker processes")
        for p in processes:
            if p:
                p.terminate()

        if celery_beat_process:
            logger.info("Shutting down celery beat process")
            celery_beat_process.terminate()

        if not disable_collection:

            try:
                cleanup_after_collection_halt(logger)
            except RedisConnectionError:
                pass

def start_celery_worker_processes(vmem_cap_ratio, disable_collection=False):

    #Calculate process scaling based on how much memory is available on the system in bytes.
    #Each celery process takes ~500MB or 500 * 1024^2 bytes

    process_list = []

    #Cap memory usage to 30% of total virtual memory
    available_memory_in_bytes = psutil.virtual_memory().total * vmem_cap_ratio
    available_memory_in_megabytes = available_memory_in_bytes / (1024 ** 2)
    max_process_estimate = available_memory_in_megabytes // 500
    sleep_time = 0

    #Get a subset of the maximum procesess available using a ratio, not exceeding a maximum value
    def determine_worker_processes(ratio,maximum):
        return max(min(round(max_process_estimate * ratio),maximum),1)
    
    frontend_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency=1 -n frontend:{uuid.uuid4().hex}@%h -Q frontend"
    max_process_estimate -= 1
    process_list.append(subprocess.Popen(frontend_worker.split(" ")))
    sleep_time += 6

    if not disable_collection:

        #2 processes are always reserved as a baseline.
        scheduling_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency=2 -n scheduling:{uuid.uuid4().hex}@%h -Q scheduling"
        max_process_estimate -= 2
        process_list.append(subprocess.Popen(scheduling_worker.split(" ")))
        sleep_time += 6

        #60% of estimate, Maximum value of 45
        core_num_processes = determine_worker_processes(.6, 45)
        logger.info(f"Starting core worker processes with concurrency={core_num_processes}")
        core_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency={core_num_processes} -n core:{uuid.uuid4().hex}@%h"
        process_list.append(subprocess.Popen(core_worker.split(" ")))
        sleep_time += 6

        #20% of estimate, Maximum value of 25
        secondary_num_processes = determine_worker_processes(.2, 25)
        logger.info(f"Starting secondary worker processes with concurrency={secondary_num_processes}")
        secondary_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency={secondary_num_processes} -n secondary:{uuid.uuid4().hex}@%h -Q secondary"
        process_list.append(subprocess.Popen(secondary_worker.split(" ")))
        sleep_time += 6

        #15% of estimate, Maximum value of 20
        facade_num_processes = determine_worker_processes(.2, 20)
        logger.info(f"Starting facade worker processes with concurrency={facade_num_processes}")
        facade_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency={facade_num_processes} -n facade:{uuid.uuid4().hex}@%h -Q facade"
        
        process_list.append(subprocess.Popen(facade_worker.split(" ")))
        sleep_time += 6

    time.sleep(sleep_time)

    return process_list


@cli.command('stop')
def stop():
    """
    Sends SIGTERM to all Augur server & worker processes
    """
    logger = logging.getLogger("augur.cli")

    augur_stop(signal.SIGTERM, logger)

@cli.command('kill')
def kill():
    """
    Sends SIGKILL to all Augur server & worker processes
    """
    logger = logging.getLogger("augur.cli")
    augur_stop(signal.SIGKILL, logger)


def augur_stop(signal, logger):
    """
    Stops augur with the given signal, 
    and cleans up collection if it was running
    """

    augur_processes = get_augur_processes()
    # if celery is running, run the cleanup function
    process_names = [process.name() for process in augur_processes]

    _broadcast_signal_to_processes(augur_processes, broadcast_signal=signal, given_logger=logger)

    if "celery" in process_names:
        cleanup_after_collection_halt(logger)


def cleanup_after_collection_halt(logger):
    clear_redis_caches()
    connection_string = ""
    with DatabaseSession(logger) as session:
        config = AugurConfig(logger, session)
        connection_string = config.get_section("RabbitMQ")['connection_string']

        clean_collection_status(session)

    clear_rabbitmq_messages(connection_string)

def clear_redis_caches():
    """Clears the redis databases that celery and redis use."""

    logger.info("Flushing all redis databases this instance was using")
    celery_purge_command = "celery -A augur.tasks.init.celery_app.celery_app purge -f"
    subprocess.call(celery_purge_command.split(" "))
    redis_connection.flushdb()

def clear_all_message_queues(connection_string):
    queues = ['celery','secondary','scheduling','facade']

    virtual_host_string = connection_string.split("/")[-1]

    #Parse username and password with urllib
    parsed = urlparse(connection_string)

    for q in queues:
        curl_cmd = f"curl -i -u {parsed.username}:{parsed.password} -XDELETE http://localhost:15672/api/queues/{virtual_host_string}/{q}"
        subprocess.call(curl_cmd.split(" "),stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def clear_rabbitmq_messages(connection_string):
    #virtual_host_string = connection_string.split("/")[-1]

    logger.info("Clearing all messages from celery queue in rabbitmq")
    from augur.tasks.init.celery_app import celery_app
    celery_app.control.purge()

    clear_all_message_queues(connection_string)
    #rabbitmq_purge_command = f"sudo rabbitmqctl purge_queue celery -p {virtual_host_string}"
    #subprocess.call(rabbitmq_purge_command.split(" "))

#Make sure that database reflects collection status when processes are killed/stopped.
def clean_collection_status(session):
    session.execute_sql(s.sql.text("""
        UPDATE augur_operations.collection_status 
        SET core_status='Pending',core_task_id = NULL
        WHERE core_status='Collecting' AND core_data_last_collected IS NULL;

        UPDATE augur_operations.collection_status
        SET core_status='Success',core_task_id = NULL
        WHERE core_status='Collecting' AND core_data_last_collected IS NOT NULL;

        UPDATE augur_operations.collection_status 
        SET secondary_status='Pending',secondary_task_id = NULL
        WHERE secondary_status='Collecting' AND secondary_data_last_collected IS NULL;

        UPDATE augur_operations.collection_status 
        SET secondary_status='Success',secondary_task_id = NULL
        WHERE secondary_status='Collecting' AND secondary_data_last_collected IS NOT NULL;

        UPDATE augur_operations.collection_status 
        SET facade_status='Update', facade_task_id=NULL
        WHERE facade_status LIKE '%Collecting%' and facade_data_last_collected IS NULL;

        UPDATE augur_operations.collection_status 
        SET facade_status='Success', facade_task_id=NULL
        WHERE facade_status LIKE '%Collecting%' and facade_data_last_collected IS NOT NULL;

        UPDATE augur_operations.collection_status
        SET facade_status='Pending', facade_task_id=NULL
        WHERE facade_status='Failed Clone' OR facade_status='Initializing';
    """))
    #TODO: write timestamp for currently running repos.

def assign_orphan_repos_to_default_user(session):
    query = s.sql.text("""
        SELECT repo_id FROM repo WHERE repo_id NOT IN (SELECT repo_id FROM augur_operations.user_repos)
    """)

    repos = session.execute_sql(query).fetchall()

    for repo in repos:
        UserRepo.insert(session,repo[0],1)


@cli.command('export-env')
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
@test_connection
@test_db_connection
def repo_reset(augur_app):
    """
    Refresh repo collection to force data collection
    """
    augur_app.database.execute(s.sql.text("""
        UPDATE augur_operations.collection_status 
        SET core_status='Pending',core_task_id = NULL, core_data_last_collected = NULL;

        UPDATE augur_operations.collection_status 
        SET secondary_status='Pending',secondary_task_id = NULL, secondary_data_last_collected = NULL;

        UPDATE augur_operations.collection_status 
        SET facade_status='Pending', facade_task_id=NULL, facade_data_last_collected = NULL;

        TRUNCATE augur_data.commits CASCADE;
        """))

    logger.info("Repos successfully reset")

@cli.command('processes')
def processes():
    """
    Outputs the name/PID of all Augur server & worker processes"""
    augur_processes = get_augur_processes()
    for process in augur_processes:
        logger.info(f"Found process {process.pid}")

def get_augur_processes():
    augur_processes = []
    for process in psutil.process_iter(['cmdline', 'name', 'environ']):
        if process.info['cmdline'] is not None and process.info['environ'] is not None:
            try:
                if os.getenv('VIRTUAL_ENV') in process.info['environ']['VIRTUAL_ENV'] and 'python' in ''.join(process.info['cmdline'][:]).lower():
                    if process.pid != os.getpid():
                        augur_processes.append(process)
            except (KeyError, FileNotFoundError):
                pass
    return augur_processes

def _broadcast_signal_to_processes(processes, broadcast_signal=signal.SIGTERM, given_logger=None):
    if given_logger is None:
        _logger = logger
    else:
        _logger = given_logger
    for process in processes:
        if process.pid != os.getpid():
            logger.info(f"Stopping process {process.pid}")
            try:
                process.send_signal(broadcast_signal)
            except psutil.NoSuchProcess:
                pass


def raise_open_file_limit(num_files):
    """
    sets number of open files soft limit 
    """
    current_soft, current_hard = resource.getrlimit(resource.RLIMIT_NOFILE)

    # if soft is already greater than the requested amount then don't change it
    if current_soft > num_files:
        return

    # if the requested amount is greater than the hard limit then set the hard limit to the num_files value
    if current_hard <= num_files:
        current_hard = num_files

    resource.setrlimit(resource.RLIMIT_NOFILE, (num_files, current_hard))

    return

# def initialize_components(augur_app, disable_housekeeper):
#     master = None
#     manager = None
#     broker = None
#     housekeeper = None
#     worker_processes = []
#     mp.set_start_method('forkserver', force=True)

#     if not disable_housekeeper:

#         manager = mp.Manager()
#         broker = manager.dict()
#         housekeeper = Housekeeper(broker=broker, augur_app=augur_app)

#         controller = augur_app.config.get_section('Workers')
#         for worker in controller.keys():
#             if controller[worker]['switch']:
#                 for i in range(controller[worker]['workers']):
#                     logger.info("Booting {} #{}".format(worker, i + 1))
#                     worker_process = mp.Process(target=worker_start, name=f"{worker}_{i}", kwargs={'worker_name': worker, 'instance_number': i, 'worker_port': controller[worker]['port']}, daemon=True)
#                     worker_processes.append(worker_process)
#                     worker_process.start()

#     augur_app.manager = manager
#     augur_app.broker = broker
#     augur_app.housekeeper = housekeeper

#     atexit._clear()
#     atexit.register(exit, augur_app, worker_processes, master)
#     return AugurGunicornApp(augur_app.gunicorn_options, augur_app=augur_app)

# def worker_start(worker_name=None, instance_number=0, worker_port=None):
#     try:
#         time.sleep(30 * instance_number)
#         destination = subprocess.DEVNULL
#         process = subprocess.Popen("cd workers/{} && {}_start".format(worker_name,worker_name), shell=True, stdout=destination, stderr=subprocess.STDOUT)
#         logger.info("{} #{} booted.".format(worker_name,instance_number+1))
#     except KeyboardInterrupt as e:
#         pass
