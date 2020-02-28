#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
import subprocess
import click

from augur.cli.configure import default_config

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

@cli.command('export-env')
@click.pass_context
def export_env(ctx):
    app = ctx.obj

    defaults = {
        "key": default_config['Database']['key'],
        "host": default_config['Database']['host'],
        "name": default_config['Database']['database'],
        "db_port": int(default_config['Database']['port']),
        "user": default_config['Database']['user'],
        "password": default_config['Database']['password'],
        "repo_directory": default_config['Workers']['facade_worker']['repo_directory'],
        "port": int(default_config['Server']['port'])
    }

    app.export_config(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY', default=defaults['key'])
    app.export_config(section='Server', name='port', environment_variable='AUGUR_PORT', default=defaults['port'])

    app.export_config(section='Database', name='host', environment_variable='AUGUR_DB_HOST', default=defaults['host'])
    app.export_config(section='Database', name='database', environment_variable='AUGUR_DB_NAME', default=defaults['name'])
    app.export_config(section='Database', name='port', environment_variable='AUGUR_DB_PORT', default=defaults['db_port'])
    app.export_config(section='Database', name='user', environment_variable='AUGUR_DB_USER', default=defaults['user'])
    app.export_config(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD', default=defaults['password'])
    app.export_config(section=None, name=None, environment_variable='AUGUR_FACADE_REPO_DIRECTORY', default=defaults['repo_directory'])


@cli.command('kill', short_help='Kill Augur')
def kill():
    """
    Kill running augur processes
    """
    run_control_script("../../util/scripts/control/augurkill.sh")

@cli.command('list', short_help='List running Augur processes')
def list():
    """
    List currently running augur processes
    """
    run_control_script("../../util/scripts/control/augur_processes.sh")

@cli.command('repo-reset', short_help='Reset Repo Collection')
def kill(app):
    """
    Reset the repo states to "New" in the database
    """
    run_control_script("../../util/scripts/control/repo-reset.sh")

def run_control_script(relative_script_path):
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    subprocess.call(relative_script_path)





