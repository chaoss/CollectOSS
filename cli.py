import click
import os
import datetime
from ghdata import GHData

client = None

# Flags and Initialization
@click.group()
@click.option('--token', help='GitHub personal access token')
@click.option('--username', help='GitHub username (if not using tokens)')
@click.option('--password', help='GitHub password (if not using tokens)')
@click.option('--file', type=click.File('wb'), help='output file')
@click.option('--format', 'dataformat', default='csv', help='\'json\' or \'csv\'')
@click.option('--start', default='beginning', help='Date from which to gather historical data for \'beginning\' includes all data (default).')
@click.option('--end', default='now', help='Last date to appear in the data dump. \'now\' includes current data from GitHub API (default).')
@click.option('--now', help='Ignore GHTorrent and only interact with the GitHub API. Overrides start/end.')
@click.pass_context
def cli(ctx, token, username, password, file, dataformat, start, end, now):
    """Tool to gather data about GitHub repositories.

    Export the environment variable GITHUB_TOKEN to avoid having to pass it each time.
    To generate a personal access token, go here: https://github.com/settings/tokens/new
    """
    global client
    if (token):
        client = GHData(token)
    if (username and password):
        client = GHData(username, password)
    ctx.obj['file'] = file
    ctx.obj['format'] = dataformat
    ctx.obj['start'] = start
    ctx.obj['end'] = end
    ctx.obj['now'] = now

# Get data about a user
@cli.command()
@click.argument('username', default='')
@click.pass_context
def user(ctx, username):
    if (username is ''):
        print(client.user(start=ctx.obj['start'], end=ctx.obj['end']))
    else:
        print(client.user(username=username, start=ctx.obj['start'], end=ctx.obj['end']))

if __name__ == '__main__':
    cli(obj={}, auto_envvar_prefix='GITHUB')