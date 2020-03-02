#SPDX-License-Identifier: MIT
"""
Handles global context, I/O, and configuration
"""

import os
import time
import logging
import multiprocessing as mp
import json
import pkgutil
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from augur.models.common import Base
from augur import logger
from augur.metrics import MetricDefinitions
import augur.plugins

from augur.cli.configure import default_config

logging.basicConfig(level=logging.INFO)

class Application(object):
    """Initalizes all classes from Augur using a config file or environment variables"""

    def __init__(self):
        """
        Reads config, creates DB session, and initializes cache
        """
        self.config_file_name = 'augur.config.json'
        self.__shell_config = None
        self.__export_file = None
        self.__env_file = None
        self.config = default_config
        self.env_config = {}
        default_config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/' + self.config_file_name
        using_config_file = False


        config_locations = [self.config_file_name, default_config_path, f"/opt/augur/{self.config_file_name}"]
        if os.getenv('AUGUR_CONFIG_FILE') is not None:
            config_file_path = os.getenv('AUGUR_CONFIG_FILE')
            using_config_file = True
        else:
            for index, location in enumerate(config_locations):
                try:
                    f = open(location, "r+")
                    config_file_path = os.path.abspath(location)
                    using_config_file = True
                    f.close()
                    break
                except FileNotFoundError:
                    pass

        if using_config_file:
            try:
                with open(config_file_path, 'r+') as config_file_handle:
                    self.config = json.loads(config_file_handle.read())
            except json.decoder.JSONDecodeError as e:
                logger.warn('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', config_file_path, str(e))
        else:
            logger.warn('%s could not be parsed, using defaults. Error: %s', str(e))

        self.load_env_configuration()

        # List of data sources that can do periodic updates

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

        self.metrics = MetricDefinitions(self)

    def read_config(self, section, name=None):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """
        if section is not None:
            value = self.config[section]
            if name is not None:
                value = self.config[section][name]
        else:
            value = None

        if os.getenv('AUGUR_DEBUG_LOG_ENV', '0') == '1':
            logger.debug('{}:{} = {}'.format(section, name, value))

        return value

    def load_env_configuration(self):
        self.set_env_value(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY')
        self.set_env_value(section='Server', name='port', environment_variable='AUGUR_PORT')
        self.set_env_value(section='Database', name='host', environment_variable='AUGUR_DB_HOST')
        self.set_env_value(section='Database', name='database', environment_variable='AUGUR_DB_NAME')
        self.set_env_value(section='Database', name='port', environment_variable='AUGUR_DB_PORT')
        self.set_env_value(section='Database', name='user', environment_variable='AUGUR_DB_USER')
        self.set_env_value(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD')
        self.set_env_value(section='facade_worker', name='repo_directory', environment_variable='AUGUR_FACADE_REPO_DIRECTORY', sub_config=self.config['Workers'])

    def set_env_value(self, section, name, environment_variable, sub_config=None):
        """
        Sets names and values of specified config section according to their environment variables.
        """
        # using sub_config lets us grab values from nested config blocks
        if sub_config is None:
            sub_config = self.config

        if os.getenv(environment_variable) is not None:
            if section is not None and name is not None:
                sub_config[section][name] = os.getenv(environment_variable)
        try:
            self.env_config[environment_variable] = os.getenv(environment_variable, sub_config[section][name])
        except KeyError as e:
            print(environment_variable + " has no default value. Skipping...")

    @property
    def shell(self, banner1='-- Augur Shell --', **kwargs):
        from IPython.terminal.embed import InteractiveShellEmbed
        if not self.__shell_config:
            from augur.util import init_shell_config
            self.__shell_config = init_shell_config()
        return InteractiveShellEmbed(config=self.__shell_config, banner1=banner1, **kwargs)

