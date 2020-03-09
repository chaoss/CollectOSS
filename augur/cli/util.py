#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
from subprocess import call
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

@cli.command('export-deps')
def export_deps():
    run_control_script("export_dependencies.sh")

@cli.command('kill', short_help='Kill Augur')
def kill_processes():
    """
    Kill running augur processes
    """
    run_control_script("kill_processes.sh")

@cli.command('list', short_help='List running Augur processes')
def list_processes():
    """
    List currently running augur processes
    """
    run_control_script("list_processes.sh")

@cli.command('status', short_help='List running Augur processes')
@click.option('--interactive', is_flag=True, help='Display all log files simultaneously with less')
def status(interactive):
    """
    List currently running augur processes
    """
    if not interactive:
        run_control_script("status.sh", "quick")
    else:
        run_control_script("status.sh", "interactive")

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

def run_control_script(script_name, options=None):
    script_path = "/augur/cli/scripts/" + script_name
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
    if options:
        call([f"./{script_path}", options])
    else:
        call([f"./{script_path}"])
