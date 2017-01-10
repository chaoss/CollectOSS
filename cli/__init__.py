import click
import datetime
from ghdata.ghdata import GHData

# Flags and Initialization
@click.group()
@click.option('--username', prompt=True, help='Save output to file. Prints to STDOUT by default.')
@click.password_option()
@click.option('--file', help='Save output to file. Prints to STDOUT by default.')
@click.option('--format', default='csv', help='\'json\' or \'csv\'')
@click.option('--start', default='beginning', help='Earliest date to appear in the data dump. \'beginning\' includes all data (default).')
@click.option('--end', default='now', help='Last date to appear in the data dump. \'now\' includes current data from GitHub API (default).')
@click.option('--now', help='Ignore GHTorrent and only interact with the GitHub API. Overrides start-date/end-date.')
@click.pass_context
def cli(ctx, username, password, file, filetype, start, end, now):
    ctx.client = GHData(username, password)
    ctx.file = file
    ctx.format = filetype
    ctx.start = start
    ctx.end = end
    ctx.now = now

# Get data about a user
@click.command()
@click.argument('username', default='')
@click.pass_context
def user(ctx, username):
    print(ctx.client.user(username, ctx.start, ctx.end))


if __name__ == '__main__':
    cli(obj={})