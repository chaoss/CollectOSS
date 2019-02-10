import click
import os
import sys
from augur.runtime import pass_application
from augur.util import logger

@click.group('util', short_help='Miscellaneous utilities')
def cli():
    pass

@cli.command('shell', short_help='Drop into a shell')
@pass_application
def shell(app):
    app.shell()

@cli.command('edit-config', short_help='Edit your config file')
@pass_application
def edit_config(app):
    """
    Edit your config file
    """
    click.edit(filename=app._config_file_path)


@cli.command('python-location', short_help='Print the location of the interpreter that is running this')
def interpreter():
    """
    Print the location of the interpreter that is running this
    """
    print(sys.executable)


@cli.command('except', short_help='Test logging and raise an exception')
@pass_application
def excpt(app):
    """
    Print the location of the interpreter that is running this
    """
    print('Logging tests... ', file=sys.stderr)
    app.log.info('Hello')
    app.log.warn('Things are looking scary')
    app.log.error('Things are bad!')
    app.log.fatal('Now I am dying')
    print('Exception handling...', file=sys.stderr)
    raise Exception('is dead')


@cli.command('upgrade', short_help='Upgrade Augur')
@click.option('--from-directory', '-f', type=click.Path(), help='Upgrade from a provided directroy rather than git.')
@pass_application
def upgrade(app, from_directory):
    """
    Print the location of the interpreter that is running this
    """
    app.log.info(pyrcss.util.self_upgrade(from_directory=from_directory, dry_run=True))
    pyrcss.util.self_upgrade(from_directory=from_directory)


@cli.command('test', short_help='Test Augur')
@click.option('--from-directory', '-f', type=click.Path(), help='Upgrade from a provided directroy rather than git.')
@pass_application
def test(app, from_directory):
    """
    Print the location of the interpreter that is running this
    """
    app.log.info(pyrcss.util.run_tests(from_directory=from_directory, dry_run=True))
    pyrcss.util.run_tests(from_directory=from_directory)