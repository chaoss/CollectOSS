#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
import subprocess
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

    app.export_config(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY', default=default_config['Database']['key'])
    app.export_config(section='Server', name='port', environment_variable='AUGUR_PORT', default=int(default_config['Server']['port']))
    app.export_config(section='Database', name='host', environment_variable='AUGUR_DB_HOST', default=default_config['Database']['host'])
    app.export_config(section='Database', name='database', environment_variable='AUGUR_DB_NAME', default=default_config['Database']['database'])
    app.export_config(section='Database', name='port', environment_variable='AUGUR_DB_PORT', default=int(default_config['Database']['port']))
    app.export_config(section='Database', name='user', environment_variable='AUGUR_DB_USER', default=default_config['Database']['user'])
    app.export_config(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD', default=default_config['Database']['password'])
    app.export_config(section=None, name=None, environment_variable='AUGUR_FACADE_REPO_DIRECTORY', default=default_config['Workers']['facade_worker']['repo_directory'])


@cli.command('kill', short_help='Kill Augur')
def kill():
    """
    Kill running augur processes
    """
    run_control_script("../../scripts/control/kill.sh")

@cli.command('list', short_help='List running Augur processes')
def list():
    """
    List currently running augur processes
    """
    run_control_script("../../scripts/control/processes.sh")

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

def run_control_script(relative_script_path):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    subprocess.call(relative_script_path)
