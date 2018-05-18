import os
import logging
import configparser as configparser
import augur
from augur import logger

class Application(object):
    """Initalizes all classes form Augur using a config file or environment variables"""

    def __init__(self, config_file='augur.cfg'):

        # Open the config file
        self.__already_exported = {}
        self.__config_bad = False
        if os.getenv('AUGUR_ENV_ONLY', '0') != '1':
            try:
                self.__config_file = open(os.getenv('AUGUR_CONFIG_FILE', config_file), 'r+')
            except:
                logger.info('Couldn\'t open config file, attempting to create.')
                self.__config_file = open(os.getenv('AUGUR_CONFIG_FILE', config_file), 'w+')
                self.__config_bad = True
            # Options to export the loaded configuration as environment variables for Docker
            self.__export_env = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
            if self.__export_env:
                export_filename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'lastrun.cfg.sh')
                self.__export_file = open(export_filename, 'w+')
                logger.info('Exporting {} to environment variable export statements in {}'.format(config_file, export_filename))
                self.__export_file.write('#!/bin/bash\n')

        self.__ghtorrent = None
        self.__ghtorrentplus = None
        self.__github = None
        self.__librariesio = None
        self.__downloads = None
        self.__publicwww = None
        self.__localCSV = None

        # Initialize the parser
        self.parser = configparser.RawConfigParser()
        self.parser.readfp(self.__config_file)

    def read_config(self, section, name, environment_variable, default):
        value = os.getenv(environment_variable)
        if value is None:
            if os.getenv('AUGUR_ENV_ONLY', '0') == '1':
                return default
            try:
                value =  self.parser.get(section, name)
            except Exception as e:
                if not self.parser.has_section(section):
                    self.parser.add_section(section)
                self.__config_bad = True
                logger.info('[' + section + ']->' + name + ' is missing. Your config will be regenerated with it included after execution.')
                self.parser.set(section, name, default)
                value = default
        if self.__export_env and not hasattr(self.__already_exported, environment_variable):
            self.__export_file.write('export ' + environment_variable + '="' + value + '"\n')
            self.__already_exported[environment_variable] = True
        if os.getenv('AUGUR_DEBUG_LOG_ENV', '0') == '1': 
            logger.debug('{} = {}'.format(environment_variable, value))
        return value

    def finalize_config(self):
        # Close files and save config
        if (self.__config_bad):
            logger.info('Regenerating config...')
            self.__config_file.seek(0)
            self.parser.write(self.__config_file)
        self.__config_file.close()
        if (self.__export_env):
            self.__export_file.close()

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

    def github(self):
        if self.__github is None:
            logger.debug('Initializing GitHub API')
            self.__github = augur.GitHubAPI(api_key=self.read_config('GitHub', 'APIKey', 'AUGUR_GITHUB_API_KEY', 'None'))
        return self.__github

    def librariesio(self):
        if self.__librariesio is None:
            logger.debug('Initializing LibrariesIO')
            self.__librariesio = augur.LibrariesIO(api_key=self.read_config('LibrariesIO', 'APIKey', 'AUGUR_LIBRARIESIO_API_KEY', 'None'), githubapi=self.github())
        return self.__librariesio

    def downloads(self):
        if self.__downloads is None:
            logger.debug('Initializing Downloads')
            self.__downloads = augur.Downloads(self.github())
        return self.__downloads

    def publicwww(self):
        if self.__publicwww is None:
            logger.debug('Initializing PublicWWW')
            self.__publicwww = augur.PublicWWW(api_key=self.read_config('PublicWWW', 'APIKey', 'AUGUR_PUBLIC_WWW_API_KEY', 'None'))
        return self.__publicwww

    def localcsv(self):
        if self.__localCSV is None:
            logger.debug('Initializing LocalCSV')
            self.__localCSV = augur.LocalCSV()
        return self.__localCSV


