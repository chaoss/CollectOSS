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
from augur import logger
import argparse

def updater_process(name, delay):
    logger.info('Spawned {} updater process with PID {}'.format(name, os.getpid()))
    app = Application()
    datasource = getattr(app, name)()
    try:
        while True:
            logger.info('Updating {}...'.format(name))
            datasource.update()
            time.sleep(delay)
    except KeyboardInterrupt:
        os._exit(0)
    except:
        raise

def load_plugins():
    if not hasattr(load_plugins, 'already_loaded'):
        import augur.plugins
    load_plugins.already_loaded = True

class Application(object):
    """Initalizes all classes form Augur using a config file or environment variables"""

    def __init__(self, config_file='augur.config.json', no_config_file=0, description='Augur application'):

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

        # Initalize all objects to None
        self.__ghtorrent = None
        self.__ghtorrentplus = None
        self.__githubapi = None
        self.__git = None
        self.__facade = None
        self.__librariesio = None
        self.__downloads = None
        self.__localCSV = None
        self.__metrics_status = None

        # Load plugins
        import augur.plugins

    @classmethod
    def register_plugin(cls, plugin):
        if not hasattr(plugin, 'name'):
            raise NameError("{} didn't have a name")
        cls.plugins[plugin.name] = plugin

    def replace_config_variables(self, string, reverse=False):
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
        path = self.replace_config_variables(path)
        path = os.path.abspath(os.path.expanduser(path))
        return path

    def __updater(self, updates=None):
        if updates is None:
            updates = self.__updatable
        for update in updates:
            if not 'started' in update:
                up = mp.Process(target=updater_process, args=(update['name'], update['delay']), daemon=True)
                up.start()
                self.__processes.append(up)
                update['started'] = True

    def init_all(self):
        self.ghtorrent()
        self.ghtorrentplus()
        self.githubapi()
        self.git()
        self.facade()
        self.librariesio()
        self.downloads()
        self.localcsv()        
        self.metrics_status()

    def read_config(self, section, name, environment_variable=None, default=None):
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
            self.__export_file.write('export ' + environment_variable + '="' + value + '"\n')
            self.__already_exported[environment_variable] = True
        if os.getenv('AUGUR_DEBUG_LOG_ENV', '0') == '1': 
            logger.debug('{}:{} = {}'.format(section, name, value))
        return value

    def read_config_path(self, section, name, environment_variable=None, default=None):
        path = self.read_config(section, name, environment_variable, default)
        path = self.path(path)
        return path

    def set_config(self, section, name, value):
        if not section in self.__config:
            self.__config[section] = {}
        self.__config[section][name] = value

    def finalize_config(self):
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
        if (self.__export_env):
            self.__export_file.close()

    def path_relative_to_config(self, path):
        if not os.path.isabs(path):
            return os.path.join(self.__config_location, path)
        else:
            return path

    def update_all(self):
        print(self.__updatable)
        for updatable in self.__updatable:
            logger.info('Updating {}...'.format(updatable['name']))
            updatable['update']()

    def schedule_updates(self):
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
        for process in self.__processes:
            process.terminate()

    def ghtorrent(self):
        from augur.ghtorrent import GHTorrent
        if self.__ghtorrent is None:
            logger.debug('Initializing GHTorrent')
            self.__ghtorrent = GHTorrent(
                user=self.read_config('Database', 'user', 'AUGUR_DB_USER', 'root'),
                password=self.read_config('Database', 'pass', 'AUGUR_DB_PASS', 'password'),
                host=self.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1'),
                port=self.read_config('Database', 'port', 'AUGUR_DB_PORT', '3306'),
                dbname=self.read_config('Database', 'name', 'AUGUR_DB_NAME', 'msr14')
            )
        return self.__ghtorrent

    def facade(self):
        from augur.facade import Facade
        if self.__facade is None:
            logger.debug('Initializing Facade')
            self.__facade = Facade(
                user=self.read_config('Facade', 'user', 'AUGUR_FACADE_DB_USER', 'root'),
                password=self.read_config('Facade', 'pass', 'AUGUR_FACADE_DB_PASS', ''),
                host=self.read_config('Facade', 'host', 'AUGUR_FACADE_DB_HOST', '127.0.0.1'),
                port=self.read_config('Facade', 'port', 'AUGUR_FACADE_DB_PORT', '3306'),
                dbname=self.read_config('Facade', 'name', 'AUGUR_FACADE_DB_NAME', 'facade'),
                projects=self.read_config('Facade', 'projects', None, [])
            )
        return self.__facade

    def ghtorrentplus(self):
        from augur.ghtorrentplus import GHTorrentPlus
        if self.__ghtorrentplus is None:
            logger.debug('Initializing GHTorrentPlus')
            self.__ghtorrentplus = GHTorrentPlus(
                user=self.read_config('GHTorrentPlus', 'user', 'AUGUR_GHTORRENT_PLUS_USER', 'root'),
                password=self.read_config('GHTorrentPlus', 'pass', 'AUGUR_GHTORRENT_PLUS_PASS', 'password'),
                host=self.read_config('GHTorrentPlus', 'host', 'AUGUR_GHTORRENT_PLUS_HOST', '127.0.0.1'),
                port=self.read_config('GHTorrentPlus', 'port', 'AUGUR_GHTORRENT_PLUS_PORT', '3306'),
                dbname=self.read_config('GHTorrentPlus', 'name', 'AUGUR_GHTORRENT_PLUS_NAME', 'ghtorrentplus')
            , ghtorrent=self.ghtorrent())
        return self.__ghtorrentplus

    def git(self, update=False):
        from augur.git import Git
        storage = self.path_relative_to_config(
            self.read_config_path('Git', 'storage', 'AUGUR_GIT_STORAGE', '$(RUNTIME)/git_repos/')
        )
        repolist = self.read_config('Git', 'repositories', None, [])
        if self.__git is None:
            logger.debug('Initializing Git')
            self.__git = Git(
                list_of_repositories=repolist,
                storage_folder=storage,
                csv=self.localcsv(),
                cache=self.cache
            )
            self.__updatable.append({
                'name': 'git',
                'delay': int(self.read_config('Git', 'refresh', 'AUGUR_GIT_REFRESH', '3600')),
                'update': self.__git.update
            })
        if update:
            self.__git.update()
        return self.__git


    def githubapi(self):
        from augur.githubapi import GitHubAPI
        if self.__githubapi is None:
            logger.debug('Initializing GitHub API')
            api_key=self.read_config('GitHub', 'apikey', 'AUGUR_GITHUB_API_KEY', 'None')
            self.__githubapi = GitHubAPI(api_key=api_key)
        return self.__githubapi

    def librariesio(self):
        from augur.librariesio import LibrariesIO
        if self.__librariesio is None:
            logger.debug('Initializing LibrariesIO')
            self.__librariesio = LibrariesIO(
                api_key=self.read_config('LibrariesIO', 'apikey', 'AUGUR_LIBRARIESIO_API_KEY', 'None'), 
                githubapi=self.githubapi()
            )
        return self.__librariesio

    def downloads(self):
        from augur.downloads import Downloads
        if self.__downloads is None:
            logger.debug('Initializing Downloads')
            self.__downloads = Downloads(self.githubapi())
        return self.__downloads

    def localcsv(self):
        from augur.localcsv import LocalCSV
        if self.__localCSV is None:
            logger.debug('Initializing LocalCSV')
            self.__localCSV = LocalCSV()
        return self.__localCSV

    def metrics_status(self):
        from augur.metrics_status import MetricsStatus
        if self.__metrics_status is None:
            logger.debug('Initializing MetricsStatus')
            self.__metrics_status = MetricsStatus(self.githubapi())
        return self.__metrics_status


Application.plugins = {}
