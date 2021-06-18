#SPDX-License-Identifier: MIT
"""
Handles global context, I/O, and configuration
"""

import os
from pathlib import Path
import logging
from logging import FileHandler, Formatter
import coloredlogs
import json
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import sqlalchemy as s
import psycopg2

from augur import ROOT_AUGUR_DIRECTORY
from augur.metrics import Metrics
from augur.config import AugurConfig
from augur.logging import AugurLogging

logger = logging.getLogger(__name__)

class Application():
    """Initalizes all classes from Augur using a config file or environment variables"""

    def __init__(self, given_config={}, disable_logs=False, offline_mode=False):
        """
        Reads config, creates DB session, and initializes cache
        """
        self.logging = AugurLogging(disable_logs=disable_logs)
        self.root_augur_dir = ROOT_AUGUR_DIRECTORY
        self.config = AugurConfig(self.root_augur_dir, given_config)

        # we need these for later
        self.housekeeper = None
        self.manager = None

        self.gunicorn_options = {
            'bind': '%s:%s' % (self.config.get_value("Server", "host"), self.config.get_value("Server", "port")),
            'workers': int(self.config.get_value('Server', 'workers')),
            'timeout': int(self.config.get_value('Server', 'timeout'))
        }
        self.logging.configure_logging(self.config)
        self.gunicorn_options.update(self.logging.gunicorn_logging_options)

        self.cache_config = {
            'cache.type': 'file',
            'cache.data_dir': 'runtime/cache/',
            'cache.lock_dir': 'runtime/cache/'
        }

        if not os.path.exists(self.cache_config['cache.data_dir']):
            os.makedirs(self.cache_config['cache.data_dir'])
        if not os.path.exists(self.cache_config['cache.lock_dir']):
            os.makedirs(self.cache_config['cache.lock_dir'])
        cache_parsed = parse_cache_config_options(self.cache_config)
        self.cache = CacheManager(**cache_parsed)

        if offline_mode is False:
            logger.debug("Running in online mode")
            self.database, self.operations_database, self.spdx_database = self._connect_to_database()

            self.metrics = Metrics(self)

    def _connect_to_database(self):
        user = self.config.get_value('Database', 'user')
        host = self.config.get_value('Database', 'host')
        port = self.config.get_value('Database', 'port')
        dbname = self.config.get_value('Database', 'name')

        database_connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, self.config.get_value('Database', 'password'), host, port, dbname
        )

        csearch_path_options = 'augur_data'

        engine = s.create_engine(database_connection_string, poolclass=s.pool.NullPool,
            connect_args={'options': f'-csearch_path={csearch_path_options}'}, pool_pre_ping=True)

        csearch_path_options += ',spdx'
        spdx_engine = s.create_engine(database_connection_string, poolclass=s.pool.NullPool,
            connect_args={'options': f'-csearch_path={csearch_path_options}'}, pool_pre_ping=True)

        helper_engine = s.create_engine(database_connection_string, poolclass=s.pool.NullPool,
            connect_args={'options': f'-csearch_path=augur_operations'}, pool_pre_ping=True)

        try:
            engine.connect().close()
            helper_engine.connect().close()
            spdx_engine.connect().close()
            logger.debug("Database connection successfully established")
            return engine, helper_engine, spdx_engine
        except s.exc.OperationalError as e:
            logger.error("Unable to connect to the database. Terminating...")
            raise(e)

    def shutdown(self):
        if self.logging.stop_event is not None:
            logger.debug("Stopping housekeeper logging listener...")
            self.logging.stop_event.set()

        if self.housekeeper is not None:
            logger.debug("Shutting down housekeeper updates...")
            self.housekeeper.shutdown_updates()
            self.housekeeper = None

        if self.manager is not None:
            logger.debug("Shutting down manager...")
            self.manager.shutdown()
            self.manager = None

