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

# from augur import ROOT_AUGUR_DIRECTORY
from api.metrics import Metrics
from augur_config import AugurConfig
from tasks.task_session import TaskSession
from augur_db.engine import engine
from augur_logging import AugurLogger


# from augur.logging import AugurLogging

logger = AugurLogger("application", base_log_dir="/Users/andrew_brain/Augur/augur/logs/").get_logger()

class Application():
    """Initalizes all classes from Augur using a config file or environment variables"""

    def __init__(self, given_config={}, disable_logs=False, offline_mode=False):
        """
        Reads config, creates DB session, and initializes cache
        """
        # self.logging = AugurLogging(disable_logs=disable_logs)
        session = TaskSession(logger)
        self.config = AugurConfig(session)

        # self.root_augur_dir = ROOT_AUGUR_DIRECTORY
        # self.config = AugurConfig(self.root_augur_dir, given_config)

        # # we need these for later
        # self.housekeeper = None
        # self.manager = None

        # SSL is a little convoluted because old installations will not have any value
        # for the 'Server', 'ssl' variable. So, if it doesn't exist that's one condition, 
        # and if it exists and is false, that's the same result, but another condition.
        # Only if it exists and is true are the pem keys loaded. 
        # They should be copied from certbot into augur's ssl directory. 

        if self.config.get_value('Server', 'ssl'): 

            if self.config.get_value('Server', 'ssl') is True: 

                self.gunicorn_options = {
                    'bind': '%s:%s' % (self.config.get_value("Server", "host"), self.config.get_value("Server", "port")),
                    'workers': int(self.config.get_value('Server', 'workers')),
                    'timeout': int(self.config.get_value('Server', 'timeout')),
                    'certfile': str(self.config.get_value('Server', 'ssl_cert_file')),
                    'keyfile': str(self.config.get_value('Server', 'ssl_key_file'))
                }
            else: 
                self.gunicorn_options = {
                    'bind': '%s:%s' % (self.config.get_value("Server", "host"), self.config.get_value("Server", "port")),
                    'workers': int(self.config.get_value('Server', 'workers')),
                    'timeout': int(self.config.get_value('Server', 'timeout'))
                }
        else: 
            self.gunicorn_options = {
                'bind': '%s:%s' % (self.config.get_value("Server", "host"), self.config.get_value("Server", "port")),
                'workers': int(self.config.get_value('Server', 'workers')),
                'timeout': int(self.config.get_value('Server', 'timeout'))
            }
        

        # self.logging.configure_logging(self.config)
        # self.gunicorn_options.update(self.logging.gunicorn_logging_options)

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

            # this engine is used by the routes in the routes folder 
            self.database = engine
            # self.database, self.operations_database, self.spdx_database = engine, engine, engine
            self.metrics = Metrics()

