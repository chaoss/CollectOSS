#SPDX-License-Identifier: MIT
"""
Handles global context, I/O, and configuration
"""

import os
import time
import multiprocessing as mp
import logging
import coloredlogs
import json
import pkgutil
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
import sqlalchemy as s
import psycopg2

from augur import logger
from augur.metrics import Metrics
from augur.cli.configure import default_config

class Application():
    """Initalizes all classes from Augur using a config file or environment variables"""

    def __init__(self):
        """
        Reads config, creates DB session, and initializes cache
        """
        self.default_config_file_name = 'augur.config.json'
        self.default_config = default_config
        self.config = None
        self.env_config = {}
        self.root_augur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self._using_default_config = True

        self.config_file_path = self._discover_config_file()

        if self.config_file_path:
            self._load_config_from_file()
            if self.config:
                self._using_default_config = False

        if self._using_default_config is True:
            self.config = default_config

        self.load_env_configuration()

        log_level = self.read_config("Development", "log_level")
        if log_level == "quiet":
            logger.disabled = True
        else:
            logger.setLevel(log_level)
        self.logger = logger

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

        self.database = self._connect_to_database()
        self.spdx_db = self._connect_to_database(include_spdx=True)

        self.metrics = Metrics(self)

    def _discover_config_file(self):
        config_file_path = None
        default_config_path = self.root_augur_dir + '/' + self.default_config_file_name

        config_locations = [self.default_config_file_name, default_config_path
         , f"/opt/augur/{self.default_config_file_name}"]
        if os.getenv('AUGUR_CONFIG_FILE') is not None:
            config_file_path = os.getenv('AUGUR_CONFIG_FILE', None)
        else:
            for location in config_locations:
                try:
                    f = open(location, "r+")
                    config_file_path = os.path.abspath(location)
                    f.close()
                    break
                except FileNotFoundError:
                    pass
        return config_file_path

    def _load_config_from_file(self):
        try:
            with open(self.config_file_path, 'r+') as config_file_handle:
                self.config = json.loads(config_file_handle.read())
        except json.decoder.JSONDecodeError as e:
            logger.warning('%s could not be parsed, using default config values. Error: %s', config_file_path, str(e))
            raise(e)
        except FileNotFoundError as e:
            logger.warning('%s could not be opened, using default config values. Error: %s', config_file_path, str(e))
            raise(e)

    def _connect_to_database(self, include_spdx=False):
        user = self.read_config('Database', 'user')
        host = self.read_config('Database', 'host')
        port = self.read_config('Database', 'port')
        dbname = self.read_config('Database', 'name')

        database_connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(
            user, self.read_config('Database', 'password'), host, port, dbname
        )

        csearch_path_options = 'augur_data'
        if include_spdx == True:
            csearch_path_options += ',spdx'

        engine = s.create_engine(database_connection_string, poolclass=s.pool.NullPool,
            connect_args={'options': f'-csearch_path={csearch_path_options}'}, pool_pre_ping=True)

        try:
            test_connection = engine.connect()
            test_connection.close()
            return engine
        except s.exc.OperationalError as e:
            logger.fatal(f"Unable to connect to the database. Terminating...")
            raise(e)

    def read_config(self, section, name=None):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """
        if name is not None:
            try:
                value = self.config[section][name]
            except KeyError as e:
                value = default_config[section][name]
        else:
            try:
                value = self.config[section]
            except KeyError as e:
                value = default_config[section]

        return value

    def load_env_configuration(self):
        self.set_env_value(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY')
        self.set_env_value(section='Database', name='host', environment_variable='AUGUR_DB_HOST')
        self.set_env_value(section='Database', name='name', environment_variable='AUGUR_DB_NAME')
        self.set_env_value(section='Database', name='port', environment_variable='AUGUR_DB_PORT')
        self.set_env_value(section='Database', name='user', environment_variable='AUGUR_DB_USER')
        self.set_env_value(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD')
        self.set_env_value(section='Development', name='log_level', environment_variable='AUGUR_LOG_LEVEL')

    def set_env_value(self, section, name, environment_variable, sub_config=None):
        """
        Sets names and values of specified config section according to their environment variables.
        """
        # using sub_config lets us grab values from nested config blocks
        if sub_config is None:
            sub_config = self.config

        env_value = os.getenv(environment_variable)

        if env_value is not None:
            self.env_config[environment_variable] = env_value
            sub_config[section][name] = env_value
