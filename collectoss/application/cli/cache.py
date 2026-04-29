#SPDX-License-Identifier: MIT
"""
CollectOSS library commands redis
"""
import click

from collectoss.tasks.init.redis_connection import get_redis_connection
from collectoss.application.logs import SystemLogger
from collectoss.application.cli import test_connection, test_db_connection 

logger = SystemLogger("collectoss").get_logger()

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
            redis_conn = get_redis_connection()
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

    redis_conn = get_redis_connection()
    redis_conn.flushdb()
