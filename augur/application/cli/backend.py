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
import sys
import subprocess


from augur.tasks.start_tasks import start_task
from augur.tasks.github.issue_tasks import process_contributors
from augur.api.application import Application
from augur.api.gunicorn import AugurGunicornApp
from augur.tasks.init.redis_connection import redis_connection 
from augur.application.db.models import Repo
from augur.tasks.util.task_session import TaskSession
from augur.application.logs import AugurLogger
# from augur.server import Server
from celery import chain, signature



logger = AugurLogger("backend", base_log_dir="/Users/andrew_brain/Augur/augur/logs/").get_logger()

@click.group('server', short_help='Commands for controlling the backend API server & data collection workers')
def cli():
    pass

@cli.command("start")
@click.option("--disable-collection", is_flag=True, default=False, help="Turns off data collection workers")
def start(disable_collection):
    """
    Start Augur's backend server
    """

    logger.info("Starting workers")
    if not disable_collection:

        session = TaskSession(logger)

        repos = session.query(Repo).all()

        repos_to_collect = []
        repo_task_list = []

        logger.info("Repos available for collection")
        print_repos(repos)
        # while True:
        #     try:
        #         user_input = int(input("Please select a repo to collect: "))

        #         if user_input < 0 or user_input > len(repos)-1:
        #             print(f"Invalid input please input an integer between 0 and {len(repos)-1}")
        #             continue

        #         repo = repos[user_input]
        #         break

        #     except (IndexError, ValueError):
        #         print(f"Invalid input please input an integer between 0 and {len(repos)-1}")

        # start_task.s(repo.repo_git).apply_async()


        # if len(repos) > 1:

        #     exclude_input = str(input("Would you like to exclude any repos from collection [y/N]: ")).lower()

        #     if exclude_input == "y":
        #         remove_repos(repos)
        #         print("\n\nRepos after removing some")
        #         print_repos(repos)

        # if len(repos) > 1:

        #     order_input = str(input("Would you like to specify an order the repos are collected [y/N]: ")).lower()

        #     if order_input == "y":
        #         repos = order_repos(repos)
        #         print("\n\n Repo order after reordering")
        #         print_repos(repos)


        repo_task_list = [start_task.si(repo.repo_git) for repo in repos] + [process_contributors.si(),]

        repos_chain = chain(repo_task_list)

        logger.info(repos_chain)

        repos_chain.apply_async()

    augur_app = Application()
    logger.info("Augur application initialized")

    augur_gunicorn_app = AugurGunicornApp(augur_app.gunicorn_options, augur_app=augur_app)

    logger.info('Starting Gunicorn webserver...')
    logger.info(f'Augur is running at: http://127.0.0.1:{augur_app.config.get_value("Server", "port")}')
    logger.info('Gunicorn server logs & errors will be written to logs/gunicorn.log')
    logger.info('Housekeeper update process logs will now take over.')

    gunicorn_arbiter = Arbiter(augur_gunicorn_app)

    atexit._clear()
    atexit.register(exit, gunicorn_arbiter)

    gunicorn_arbiter.run()



@cli.command('stop')
def stop():
    """
    Sends SIGTERM to all Augur server & worker processes
    """
    _broadcast_signal_to_processes(given_logger=logging.getLogger("augur.cli"))

@cli.command('kill')
def kill():
    """
    Sends SIGKILL to all Augur server & worker processes
    """
    _broadcast_signal_to_processes(signal=signal.SIGKILL, given_logger=logging.getLogger("augur.cli"))

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
def repo_reset(augur_app):
    """
    Refresh repo collection to force data collection
    """
    augur_app.database.execute("UPDATE augur_data.repo SET repo_path = NULL, repo_name = NULL, repo_status = 'New'; TRUNCATE augur_data.commits CASCADE; ")

    logger.info("Repos successfully reset")

@cli.command('processes')

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



def print_repos(repos):

    for index, repo in enumerate(repos):

        repo_git = repo.repo_git
        print(f"\t{index}: {repo_git}")

def remove_repos(repos):

    print("Note: To remove multiple repos at once use the python slice syntax")
    print("For example '0:3' removes repo 0, 1, and 2")

    while True:
        if len(repos) == 1:
            print("Only one repo left returning..")
            return

        print_repos(repos)
        user_input = input("To exit enter: -1. Enter index of repo or slice to remove multiple: ")

        if user_input == "-1":
            break

        if ":" in user_input:
            user_slice = slice(*map(lambda x: int(x.strip()) if x.strip() else None, user_input.split(':')))
            try:
                del repos[user_slice]
            except IndexError:
                print("Invalid input. Please input a number or slice")
                continue

        else: 
            try:
                user_input = int(user_input)
            except ValueError:
                print("Invalid input. Please input a number or slice")
                continue

            try:
                del repos[user_input]
            except IndexError:
                print("Invalid input. Please input a number or slice")
                continue


def order_repos(repos):

    ordered_repos = []

    print("\n\nPlease enter a comma indicating the order the repos should be collected")
    print("If you would like to order some of them but randomize the rest just enter the order you would like and the rest will be randomized")
    print("For example with 5 repos '3,4' would collect repo 3, then 4, and then repos 1, 2, and 5 would be randomly ordered")
    print_repos(repos)

    while True:
        user_input = input("Order input: ")        

        # creates a list of indexes in the order that the user wanted
        ordered_index_strings = user_input.split(",")

        try:
            # convert list of strings to integers
            ordered_index_ints = [int(i) for i in ordered_index_strings]
        except ValueError:
            print("Invalid input. Please input a comma separated list indicating the order")
            continue

        invalid_entry = False
        for index in ordered_index_ints:
            try:
                repos[index]
            except IndexError:
                print(f"Invalid entry: {index}. Make sure your input is a comma separated list")
                invalid_entry = True

        if invalid_entry:
            continue

        break

    # adds all the other indexes the user did not specify an order for
    for index in range(0, len(repos)):

        if index in ordered_index_ints:
            continue

        ordered_index_ints.append(index)

    # converts list of indexes into list of repo git urls
    repo_git_urls = [repos[index] for index in ordered_index_ints]

    return repo_git_urls

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


def exit(gunicorn_arbiter):

    logger.info("Flushing redis cache")
    redis_connection.flushdb()

    logger.info(f"gunicorn_arbiter: {gunicorn_arbiter}")

    if gunicorn_arbiter is not None:
        logger.info("Shutting down Gunicorn server")
        gunicorn_arbiter.halt()

    logger.info("Shutdown complete")
    sys.exit(0)
