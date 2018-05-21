import os
import logging
import configparser as configparser
import json
import augur
from augur import logger

class Application(object):
    """Initalizes all classes form Augur using a config file or environment variables"""

    def __init__(self, config_file='augur.config.json', no_config_file=0):

        # Open the config file
        self.__already_exported = {}
        self.__default_config = { 'Plugins': [] }
        self.__using_config_file = True
        self.__config_bad = False
        self.__config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', config_file))
        self.__config_location = os.path.dirname(self.__config_file_path)
        if os.getenv('AUGUR_ENV_ONLY', '0') != '1' and no_config_file == 0:
            try:
                self.__config_file = open(self.__config_file_path, 'r+')
            except:
                logger.info('Couldn\'t open {}, attempting to create. If you have a augur.cfg, you can convert it to a json file using "make to-json"'.format(config_file))
                self.__config_file = open(self.__config_file_path, 'w+')
                self.__config_bad = True
            # Options to export the loaded configuration as environment variables for Docker
            self.__export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
            if self.__export_env:
                export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'augur.cfg.sh')
                self.__export_file = open(export_filename, 'w+')
                logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
                self.__export_file.write('#!/bin/bash\n')

            # Load the config file
            try:
                self.__config = json.loads(self.__config_file.read())
            except json.decoder.JSONDecodeError as e:
                if not self.__config_bad:
                    self.__using_config_file = False
                    logger.error('%s could not be parsed, using defaults. Fix that file, or delete it and run this again to regenerate it. Error: %s', self.__config_file_path, str(e))

                self.__config = self.__default_config
        else:
            self.__using_config_file = False
            self.__config = self.__default_config

        self.__ghtorrent = None
        self.__ghtorrentplus = None
        self.__github = None
        self.__librariesio = None
        self.__downloads = None
        self.__publicwww = None
        self.__localCSV = None
        

    def read_config(self, section, name, environment_variable, default):
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

    def finalize_config(self):
        # Close files and save config
        if self.__config_bad:
            logger.info('Regenerating config with missing values...')
            self.__config_file.close()
            self.__config_file = open(self.__config_file_path, 'w')
            self.__config_file.write(json.dumps(self.__config, sort_keys=True, indent=4))
        self.__config_file.close()
        if (self.__export_env):
            self.__export_file.close()

    def path_relative_to_config(self, path):
        if not os.path.isabs(path):
            return os.path.join(self.__config_location, path)
        else:
            return path

    def ghtorrent(self):
        if self.__ghtorrent is None:
            logger.debug('Initializing GHTorrent')
            self.__ghtorrent = augur.GHTorrent(
                user=self.read_config('Database', 'user', 'AUGUR_DB_USER', 'root'),
                password=self.read_config('Database', 'pass', 'AUGUR_DB_PASS', 'password'),
                host=self.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1'),
                port=self.read_config('Database', 'port', 'AUGUR_DB_PORT', '3306'),
                dbname=self.read_config('Database', 'name', 'AUGUR_DB_NAME', 'msr14')
            )
        return self.__ghtorrent

    def ghtorrentplus(self):
        if self.__ghtorrentplus is None:
            logger.debug('Initializing GHTorrentPlus')
            self.__ghtorrentplus = augur.GHTorrentPlus(
                user=self.read_config('GHTorrentPlus', 'user', 'AUGUR_GHTORRENT_PLUS_USER', 'root'),
                password=self.read_config('GHTorrentPlus', 'pass', 'AUGUR_GHTORRENT_PLUS_PASS', 'password'),
                host=self.read_config('GHTorrentPlus', 'host', 'AUGUR_GHTORRENT_PLUS_HOST', '127.0.0.1'),
                port=self.read_config('GHTorrentPlus', 'port', 'AUGUR_GHTORRENT_PLUS_PORT', '3306'),
                dbname=self.read_config('GHTorrentPlus', 'name', 'AUGUR_GHTORRENT_PLUS_NAME', 'ghtorrentplus')
            , ghtorrent=self.ghtorrent())
        return self.__ghtorrentplus

    def git(self):
        storage = self.path_relative_to_config(
            self.read_config('Git', 'storage', 'AUGUR_GIT_STORAGE', 'runtime/git_repos/')
        )
        repolist = self.read_config('Git', 'repositories', None, [])

        if self.__github is None:
            logger.debug('Initializing Git')
            self.__git = augur.Git(list_of_repositories=repolist, storage_folder=storage)
        return self.__git


    def github(self):
        if self.__github is None:
            logger.debug('Initializing GitHub API')
            self.__github = augur.GitHubAPI(api_key=self.read_config('GitHub', 'apikey', 'AUGUR_GITHUB_API_KEY', 'None'))
        return self.__github

    def librariesio(self):
        if self.__librariesio is None:
            logger.debug('Initializing LibrariesIO')
            self.__librariesio = augur.LibrariesIO(api_key=self.read_config('LibrariesIO', 'apikey', 'AUGUR_LIBRARIESIO_API_KEY', 'None'), githubapi=self.github())
        return self.__librariesio

    def downloads(self):
        if self.__downloads is None:
            logger.debug('Initializing Downloads')
            self.__downloads = augur.Downloads(self.github())
        return self.__downloads

    def publicwww(self):
        if self.__publicwww is None:
            logger.debug('Initializing PublicWWW')
            self.__publicwww = augur.PublicWWW(api_key=self.read_config('PublicWWW', 'apikey', 'AUGUR_PUBLIC_WWW_API_KEY', 'None'))
        return self.__publicwww

    def localcsv(self):
        if self.__localCSV is None:
            logger.debug('Initializing LocalCSV')
            self.__localCSV = augur.LocalCSV()
        return self.__localCSV


