#SPDX-License-Identifier: MIT
"""
Augur library commands for controlling the backend components
"""
import os
import time
import subprocess
import click
import logging
import psutil
import signal
import uuid
import traceback

from augur.application.db.session import DatabaseSession
from augur.application.logs import AugurLogger
from augur.application.cli import test_connection, test_db_connection, with_database
from augur.application.cli._cli_util import _broadcast_signal_to_processes, raise_open_file_limit, clear_redis_caches, clear_rabbitmq_messages
from augur.application.db.lib import get_value

logger = AugurLogger("augur", reset_logfiles=True).get_logger()

@click.group('api', short_help='Commands for controlling the backend API server')
def cli():
    pass

@cli.command("start")
@click.option("--development", is_flag=True, default=False, help="Enable development mode")
@click.option('--port')
@test_connection
@test_db_connection
@with_database
@click.pass_context
def start(ctx, development, port):
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

    host = get_value("Server", "host")

    if not port:
        port = get_value("Server", "port")
        
    gunicorn_command = f"gunicorn -c {gunicorn_location} -b {host}:{port} augur.api.server:app --log-file gunicorn.log"
    server = subprocess.Popen(gunicorn_command.split(" "))

    time.sleep(3)
    logger.info('Gunicorn webserver started...')
    logger.info(f'Augur is running at: {"http" if development else "https"}://{host}:{port}')

    frontend_worker = f"celery -A augur.tasks.init.celery_app.celery_app worker -l info --concurrency=1 -n frontend:{uuid.uuid4().hex}@%h -Q frontend"
    frontend_worker_process = subprocess.Popen(frontend_worker.split(" "))

    try:
        server.wait()
    except KeyboardInterrupt:
        
        if server:
            logger.info("Shutting down server")
            server.terminate()

        logger.info("Shutting down frontend celery worker process")
        if frontend_worker_process:
            frontend_worker_process.terminate()

@cli.command('stop')
@with_database
@click.pass_context
def stop(ctx):
    """
    Sends SIGTERM to all Augur api processes
    """
    logger = logging.getLogger("augur.cli")

    augur_stop(signal.SIGTERM, logger, ctx.obj.engine)

@cli.command('kill')
@with_database
@click.pass_context
def kill(ctx):
    """
    Sends SIGKILL to all Augur api processes
    """
    logger = logging.getLogger("augur.cli")
    augur_stop(signal.SIGKILL, logger, ctx.obj.engine)

@cli.command('processes')
def processes():
    """
    Outputs the name/PID of all Augur api process"""
    augur_processes = get_augur_api_processes()
    for process in augur_processes:
        logger.info(f"Found process {process.pid}")

def augur_stop(signal, logger, engine):
    """
    Stops augur with the given signal, 
    and cleans up the api
    """

    augur_processes = get_augur_api_processes()
 
    _broadcast_signal_to_processes(augur_processes, logger=logger, broadcast_signal=signal)

    cleanup_after_api_halt(logger, engine)


def cleanup_after_api_halt(logger, engine):
    
    queues = ['frontend','celery']
    connection_string = get_value("RabbitMQ", "connection_string")

    clear_rabbitmq_messages(connection_string, queues, logger)
    clear_redis_caches(logger)

def get_augur_api_processes():
    augur_api_processes = []
    for process in psutil.process_iter(['cmdline', 'name', 'environ']):
        if process.info['cmdline'] is not None and process.info['environ'] is not None:
            try:
                if is_api_process(process):
                    augur_api_processes.append(process)
            except (KeyError, FileNotFoundError):
                pass
    return augur_api_processes

def is_api_process(process):

    command = ''.join(process.info['cmdline'][:]).lower()
    if os.getenv('VIRTUAL_ENV') in process.info['environ']['VIRTUAL_ENV'] and 'python' in command:
                    
        if process.pid != os.getpid():
            
            if ("augur.api.server:app" in command or 
                "augurbackendapi" in command or 
               ("augur.tasks.init.celery_app.celery_app" in command and "frontend" in command)):
                return True
            
    return False


