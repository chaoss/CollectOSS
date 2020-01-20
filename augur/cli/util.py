#SPDX-License-Identifier: MIT
"""
Miscellaneous Augur library commands for controlling the backend components
"""

import os
import subprocess
import click

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

@cli.command('shell', short_help='Drop into a shell')
def shell(app):
    app.shell()

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





