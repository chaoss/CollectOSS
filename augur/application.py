#SPDX-License-Identifier: MIT
"""
Handles global context, I/O, and configuration
"""

import os
import time
import multiprocessing as mp
import logging
import configparser as configparser
import json
import importlib
import pkgutil
import coloredlogs
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options
from lockfile import LockFile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from augur import logger
import augur.plugins
import augur.datasources
import argparse


class Application(object):
    """Initalizes all classes from Augur using a config file or environment variables"""

    def __init__(self, config_file='augur.config.json', no_config_file=0, description='Augur application', db_str='sqlite:///:memory:'):
        """
        Reads config, creates DB session, and initializes cache
        """
        # Command line arguments
        # TODO: make this useful
        self.arg_parser = argparse.ArgumentParser(description=description)
        self.arg_parser.parse_known_args()

        # Open the config file
        self.__already_exported = {}
        self.__default_config = { 'Plugins': [] }
        self.__using_config_file = True
        self.__config_bad = False
        self.__config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
        self.__config_location = os.path.dirname(self.__config_file_path)
        self.__runtime_location = 'runtime/'
        self.__export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
        if os.getenv('AUGUR_ENV_ONLY', '0') != '1' and no_config_file == 0:
            try:
                self.__config_file = open(self.__config_file_path, 'r+')
            except:
                logger.info('Couldn\'t open {}, attempting to create. If you have a augur.cfg, you can convert it to a json file using "make to-json"'.format(config_file))
                if not os.path.exists(self.__config_location):
                    os.makedirs(self.__config_location)
                self.__config_file = open(self.__config_file_path, 'w+')
                self.__config_bad = True
            # Options to export the loaded configuration as environment variables for Docker
           
            if self.__export_env:
                export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'augur.cfg.sh')
                self.__export_file = open(export_filename, 'w+')
                logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
                self.__export_file.write('#!/bin/bash\n')

            # Load the config file
            try:
                config_text = self.__config_file.read()
                self.__config = json.loads(config_text)
            except json.decoder.JSONDecodeError as e:
                if not self.__config_bad:
                    self.__using_config_file = False
                    logger.error('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', self.__config_file_path, str(e))

                self.__config = self.__default_config
        else:
            self.__using_config_file = False
            self.__config = self.__default_config

        # List of data sources that can do periodic updates
        self.__updatable = []
        self.__processes = []

        # Create cache
        cache_config = {
            'cache.type': 'file',
            'cache.data_dir': self.path('$(RUNTIME)/cache/'),
            'cache.lock_dir': self.path('$(RUNTIME)/cache/')
        }
        cache_config.update(self.read_config('Cache', 'config', None, cache_config))
        cache_config['cache.data_dir'] = self.path(cache_config['cache.data_dir'])
        cache_config['cache.lock_dir'] = self.path(cache_config['cache.lock_dir'])
        if not os.path.exists(cache_config['cache.data_dir']):
            os.makedirs(cache_config['cache.data_dir'])
        if not os.path.exists(cache_config['cache.lock_dir']):
            os.makedirs(cache_config['cache.lock_dir'])
        cache_parsed = parse_cache_config_options(cache_config)
        self.cache = CacheManager(**cache_parsed)

        # Create DB Session
        self.db = None
        self.session = None
        if db_str:
            self.db = create_engine(db_str)
            self.__Session = sessionmaker(bind=self.db)
            self.session = self.__Session()

        # Initalize all objects to None
        self.__metrics_status = None
        self._loaded_plugins = {}

        for plugin_name in Application.default_plugins:
            self[plugin_name]

    def __getitem__(self, plugin_name):
        """
        Returns plugin matching the name of the parameter 'plugin_name'

        :param plugin_name: name of specified plugin
        """
        if plugin_name not in self._loaded_plugins:
            if plugin_name not in Application.plugins:
                raise ValueError('Plugin %s not found.' % plugin_name)
            self._loaded_plugins[plugin_name] = Application.plugins[plugin_name](self)
            logger.debug('{plugin_name} plugin loaded')
        return self._loaded_plugins[plugin_name]

    @classmethod
    def import_plugins(cls):
        """
        Imports all plugins and datasources 
        """
        if not hasattr(cls, 'plugins'):
            setattr(cls, 'plugins', {})
        for module in [augur.plugins, augur.datasources]:
            for importer, modname, ispkg in pkgutil.iter_modules(module.__path__):
                if ispkg:
                    try:
                        importer.find_module(modname).load_module(modname)
                    except Exception as e:
                        logger.warn('Error when loading plugin {module.__name__}.{modname}:')
                        logger.exception(e)

    @classmethod
    def register_plugin(cls, plugin):
        """
        Registers specified plugin

        :param plugin: specified plugin to register
        """
        if 'name' not in plugin.augur_plugin_meta:
            raise NameError("{} didn't have a name")
        cls.plugins[plugin.augur_plugin_meta['name']] = plugin
        if plugin.augur_plugin_meta.get('datasource'):
            Application.default_plugins.append(plugin.augur_plugin_meta['name'])

    def replace_config_variables(self, string, reverse=False):
        """
        Replaces the configuration of a variable sent
        """
        variable_map = {
            'AUGUR': self.__config_location,
            'RUNTIME': self.__runtime_location
        }
        for variable, source in variable_map.items():
            if not reverse:
                string = string.replace('$({})'.format(variable), source)
            else:
                string = string.replace(source, '$({})'.format(variable))
        return string

    def path(self, path):
        """
        Returns the absolute path for the given relative path
        """
        path = self.replace_config_variables(path)
        path = os.path.abspath(os.path.expanduser(path))
        return path

    @staticmethod
    def updater_process(name, delay, shared):
        """
        Controls a given plugin's update process

        :param name: name of object to be updated 
        :param delay: time needed to update
        :param shared: shared object that is to also be updated
        """
        logger.info('Spawned {} updater process with PID {}'.format(name, os.getpid()))
        app = Application()
        datasource = getattr(app, name)()
        try:
            while True:
                logger.info('Updating {}...'.format(name))
                datasource.update(shared)
                time.sleep(delay)
        except KeyboardInterrupt:
            os._exit(0)
        except:
            raise

    def __updater(self, updates=None):
        """
        Starts update processes
        """
        if updates is None:
            updates = self.__updatable
        for update in updates:
            if not 'started' in update:
                up = mp.Process(target=Application.updater_process, args=(update['name'], update['delay']), daemon=True)
                up.start()
                self.__processes.append(up)
                update['started'] = True

    def read_config(self, section, name, environment_variable=None, default=None):
        """
        Read a variable in specified section of the config file, unless provided an environment variable

        :param section: location of given variable
        :param name: name of variable
        """
        value = None
        if environment_variable is not None:
            value = os.getenv(environment_variable)
        if value is None:
            try:
                value =  self.__config[section][name]
            except Exception as e:
                value = default
                if not section in self.__config:
                    self.__config[section] = {}
                if self.__using_config_file:
                    self.__config_bad = True
                    self.__config[section][name] = default
        if (environment_variable is not None
                and value is not None
                and self.__export_env
                and not hasattr(self.__already_exported, environment_variable)):
            self.__export_file.write('export ' + environment_variable + '="' + str(value) + '"\n')
            self.__already_exported[environment_variable] = True
        if os.getenv('AUGUR_DEBUG_LOG_ENV', '0') == '1':
            logger.debug('{}:{} = {}'.format(section, name, value))
        return value

    def set_config(self, section, name, value):
        """
        Sets names and values of specified config section

        :param section: area of object
        :param name: name of specified object
        :param value: new value to be set to object
        """
        if not section in self.__config:
            self.__config[section] = {}
        self.__config[section][name] = value

    def finalize_config(self):
        """
        Parse args and generates a valid config if the given one is bad
        """
        # Parse args with help
        self.arg_parser.parse_known_args()
        # Close files and save config
        if self.__config_bad:
            logger.info('Regenerating config with missing values...')
            self.__config_file.close()
            self.__config_file = open(self.__config_file_path, 'w')
            config_text = json.dumps(self.__config, sort_keys=True, indent=4)
            config_text = config_text.replace(self.__config_location, '$(AUGUR)')
            self.__config_file.write(config_text)
        self.__config_file.close()

    def path_relative_to_config(self, path):
        """
        Returns path relative to the config file

        :param path: specified path of variable
        """
        if not os.path.isabs(path):
            return os.path.join(self.__config_location, path)
        else:
            return path

    def update_all(self):
        """
        Updates all plugins
        """
        print(self.__updatable)
        for updatable in self.__updatable:
            logger.info('Updating {}...'.format(updatable['name']))
            updatable['update']()

    def schedule_updates(self):
        """
        Schedules updates
        """
        # don't use this, 
        logger.debug('Scheduling updates...')
        self.__updater()

    def join_updates(self):
        """
        Join to the update processes
        """
        for process in self.__processes:
            process.join()

    def shutdown_updates(self):
        """
        Ends all running update processes
        """
        for process in self.__processes:
            process.terminate()

Application.plugins = {}
Application.default_plugins = []
Application.import_plugins()
