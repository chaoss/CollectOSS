#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
import signal
from subprocess import call, run
import psutil
import click
import pandas as pd
import sqlalchemy as s

from augur.cli.configure import default_config
from augur.cli.db import get_db_connection

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

@cli.command('export-env')
@click.pass_context
def export_env(ctx):
    app = ctx.obj

    export_file = open(os.getenv('AUGUR_EXPORT_FILE', 'augur_export_env.sh'), 'w+')
    export_file.write('#!/bin/bash')
    export_file.write('\n')
    env_file = open(os.getenv('AUGUR_ENV_FILE', 'augur_env.txt'), 'w+')

    for env_var in app.env_config.items():
        export_file.write('export ' + env_var[0] + '="' + str(env_var[1]) + '"\n')
        env_file.write(env_var[0] + '=' + str(env_var[1]) + '\n')

    export_file.close()
    env_file.close()

@cli.command('kill', short_help='Kill Augur')
@click.pass_context
def kill_processes(ctx):
    """
    Kill running augur processes
    """
    processes = ctx.invoke(list_processes)
    for process in processes:
        process.send_signal(signal.SIGTERM)

@cli.command('list', short_help='List running Augur processes')
def list_processes():
    """
    List currently running augur processes
    """
    processes = []
    for process in psutil.process_iter(['cmdline', 'name', 'environ']):
        if process.info['cmdline'] is not None:
            if 'VIRTUAL_ENV' in list(process.info['environ'].keys()) and 'Python' in process.info['name']:
                if process.pid is not os.getpid():
                    print(process.pid, " ".join(process.info['cmdline'][1:]))
                    processes.append(process)
    return processes

@cli.command('status', short_help='List running Augur processes')
@click.option('--interactive', is_flag=True, help='Display all log files simultaneously with less')
def status(interactive):
    """
    List currently running augur processes
    """
    print(os.getcwd())
    # if not interactive:
    #     run_control_script("status.sh", "quick")
    # else:
    #     run_control_script("status.sh", "interactive")

@cli.command('repo-reset', short_help='Reset Repo Collection')
@click.pass_context
def repo_reset(ctx):
    """
    Reset the repo states to "New" in the database
    """
    app = ctx.obj
    db = get_db_connection(app)

    db.execute("UPDATE augur_data.repo SET repo_path = NULL, repo_name = NULL, repo_status = 'New'; TRUNCATE augur_data.commits CASCADE; ")

    print("Repos successfully reset.")
