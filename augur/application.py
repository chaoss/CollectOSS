import augur
import os
import configparser as configparser

class Application(object):
    """Initalizes all classes form Augur using a config file or environment variables"""

    def __init__(self, configFile='augur.cfg'):

        # Open the config file
        self.__configBad = False
        try:
            self.__configFile = open(os.getenv('AUGUR_CONFIG_FILE', configFile), 'r+')
        except:
            print('Couldn\'t open config file, attempting to create.')
            self.__configFile = open(os.getenv('AUGUR_CONFIG_FILE', configFile), 'w+')
            self.__configBad = True
        # Options to export the loaded configuration as environment variables for Docker
        self.__exportAsEnv = os.getenv('AUGUR_ENV_EXPORT', '0') == '1'
        if self.__exportAsEnv:
            exportFilename = os.getenv('AUGUR_ENV_EXPORT_FILE', 'lastrun.cfg.sh')
            self.__exportFile = open(exportFilename, 'w+')
            print('Exporting {} to environment variable export statements in {}'.format(configFile, exportFilename))
            self.__exportFile.write('#!/bin/bash\n')

        # Initialize the parser
        self.parser = configparser.RawConfigParser()
        self.parser.readfp(self.__configFile)

    def read_config(self, section, name, environment_variable, default):
        value = os.getenv(environment_variable)
        if value is None:
            try:
                value =  self.parser.get(section, name)
            except Exception as e:
                if not self.parser.has_section(section):
                    self.parser.add_section(section)
                self.__configBad = True
                print('[' + section + ']->' + name + ' is missing. Your config will be regenerated with it included after execution.')
                self.parser.set(section, name, default)
                value = default
        if self.__exportAsEnv:
            self.__exportFile.write('export ' + environment_variable + '="' + value + '"\n')
        return value

    def finalize_config(self):
        # Close files and save config
        if (self.__configBad):
            print('Regenerating config...')
            self.__configFile.seek(0)
            self.parser.write(self.__configFile)
        self.__configFile.close()
        if (self.__exportAsEnv):
            self.__exportFile.close()

    def ghtorrent(self):
        if not hasattr(self, '__ghtorrent'):
            self.__ghtorrent = augur.GHTorrent(dbstr='mysql+pymysql://{}:{}@{}:{}/{}'.format(
                self.read_config('Database', 'user', 'AUGUR_DB_USER', 'root'),
                self.read_config('Database', 'pass', 'AUGUR_DB_PASS', 'password'),
                self.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1'),
                self.read_config('Database', 'port', 'AUGUR_DB_PORT', '3306'),
                self.read_config('Database', 'name', 'AUGUR_DB_NAME', 'msr14')
            ))
        return self.__ghtorrent

    def ghtorrentplus(self):
        if not hasattr(self, '__ghtorrentplus'):
            self.__ghtorrentplus = augur.GHTorrentPlus(dbstr='mysql+pymysql://{}:{}@{}:{}/{}'.format(
                self.read_config('GHTorrentPlus', 'user', 'AUGUR_GHTORRENT_PLUS_USER', 'root'),
                self.read_config('GHTorrentPlus', 'pass', 'AUGUR_GHTORRENT_PLUS_PASS', 'password'),
                self.read_config('GHTorrentPlus', 'host', 'AUGUR_GHTORRENT_PLUS_HOST', '127.0.0.1'),
                self.read_config('GHTorrentPlus', 'port', 'AUGUR_GHTORRENT_PLUS_PORT', '3306'),
                self.read_config('GHTorrentPlus', 'name', 'AUGUR_GHTORRENT_PLUS_NAME', 'ghtorrentplus')
            ), ghtorrent=self.ghtorrent())
        return self.__ghtorrentplus

    def github(self):
        if not hasattr(self, '__github'):
            self.__github = augur.GitHubAPI(api_key=self.read_config('GitHub', 'APIKey', 'AUGUR_GITHUB_API_KEY', 'None'))
        return self.__github

    def librariesio(self):
        if not hasattr(self, '__librariesio'):
            self.__librariesio = augur.LibrariesIO(api_key=self.read_config('LibrariesIO', 'APIKey', 'AUGUR_LIBRARIESIO_API_KEY', 'None'), githubapi=self.github())
        return self.__librariesio

    def downloads(self):
        if not hasattr(self, '__downloads'):
            self.__downloads = augur.Downloads(self.github())
        return self.__downloads

    def publicwww(self):
        if not hasattr(self, '__publicwww'):
            self.__publicwww = augur.PublicWWW(api_key=self.read_config('PublicWWW', 'APIKey', 'AUGUR_PUBLIC_WWW_API_KEY', 'None'))
        return self.__publicwww

    def localcsv(self):
        if not hasattr(self, '__localCSV'):
            self.__localCSV = augur.LocalCSV()
        return self.__localCSV


