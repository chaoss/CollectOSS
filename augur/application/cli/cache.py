#SPDX-License-Identifier: MIT
"""
Augur library commands redis
"""
import click

from augur.tasks.init.redis_connection import redis_connection as redis_conn
from augur.application.logs import AugurLogger
from augur.application.cli import test_connection, test_db_connection 

logger = AugurLogger("augur").get_logger()

@click.group('redis', short_help='Commands for managing redis cache')
def cli():
    """Placehodler func."""

@cli.command("clear-all")
@test_connection
@test_db_connection
def clear_all():
    """Clears all redis caches on a redis instance."""

    while True:

        user_input = str(input("Warning this will clear all redis databases on your redis cache!\nWould you like to proceed? [y/N]"))

        if not user_input:
            logger.info("Exiting")
            return
        
        if user_input in ("y", "Y", "Yes", "yes"):
            logger.info("Clearing call redis databases")
            redis_conn.flushall()
            return

        elif user_input in ("n", "N", "no", "NO"):
            logger.info("Exiting")
            return
        else:
            logger.error("Invalid input")

@cli.command("clear")
@test_connection
@test_db_connection
def clear():
    """Clears the redis cache specified in the config"""

    print("Clearing redis cache that is specified in the config")
    redis_conn.flushdb()
