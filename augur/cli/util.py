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

from augur.cli import initialize_logging, pass_config, pass_application
from augur.cli.server import _broadcast_signal_to_processes

logger = logging.getLogger(__name__)

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

@cli.command('stop')
@initialize_logging
def stop_server():
    """
    Sends SIGTERM to all Augur server & worker processes
    """
    logger.warning("THIS COMMAND WILL BE DEPRECATED IN AUGUR v0.15.0")
    logger.warning("PLEASE USER augur backend kill INSTEAD.")
    _broadcast_signal_to_processes(attach_logger=True)

@cli.command('kill')
@initialize_logging
def kill_server():
    """
    Sends SIGKILL to all Augur server & worker processes
    """
    logger.warning("THIS COMMAND WILL BE DEPRECATED IN AUGUR v0.15.0")
    logger.warning("PLEASE USER augur backend kill INSTEAD.")
    _broadcast_signal_to_processes(signal=signal.SIGKILL, attach_logger=True)

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
