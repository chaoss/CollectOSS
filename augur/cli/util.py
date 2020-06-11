#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
import signal
import logging
from subprocess import call, run

import psutil
import click
import pandas as pd
import sqlalchemy as s

from augur.cli import pass_config, pass_application

logger = logging.getLogger("augur.cli")

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

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
        export_file.write('export ' + env_var[0] + '="' + str(env_var[1]) + '"\n')
        env_file.write(env_var[0] + '=' + str(env_var[1]) + '\n')

    export_file.close()
    env_file.close()

@cli.command('kill')
@pass_config
def kill_processes(config):
    """
    Terminates all currently running backend Augur processes, including any workers. Will only work in a virtual environment.    
    """
    processes = get_augur_processes()
    if processes != []:
        for process in processes:
            if process.pid != os.getpid():
                # logger.info(f"Killing {process.pid}: {' '.join(process.info['cmdline'][1:])}")
                logger.info(f"Killing process {process.pid}")
                try:
                    process.send_signal(signal.SIGTERM)
                except psutil.NoSuchProcess as e:
                    pass

@cli.command('list',)
@pass_config
def list_processes(config):
    """
    Outputs the name and process ID (PID) of all currently running backend Augur processes, including any workers. Will only work in a virtual environment.    
    """
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

@cli.command('repo-reset')
@pass_application
def repo_reset(augur_app):
    """
    Refresh repo collection to force data collection
    """
    augur_app.database.execute("UPDATE augur_data.repo SET repo_path = NULL, repo_name = NULL, repo_status = 'New'; TRUNCATE augur_data.commits CASCADE; ")

    logger.info("Repos successfully reset")
