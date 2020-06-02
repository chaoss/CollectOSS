import os
import json
import logging

from augur.cli.configure import default_config

logger = logging.getLogger(__name__)

class AugurConfig():
    """docstring for AugurConfig"""
    def __init__(self, root_augur_dir):
        self._default_config_file_name = 'augur.config.json'
        self._root_augur_dir = root_augur_dir
        self._default_config = default_config
        self._env_config = {}
        self.load_config()

    def get_section(self, section_name):
        try:
            return self._config[section_name]
        except KeyError as e:
            if not self.using_default_config:
                logger.warn(f"{section_name} not found in loaded config. Checking default config")
                try:
                    return self._default_config[section_name]
                except KeyError as e:
                    logger.error(f"No defaults found for {section_name}")
                    raise(e)
            else:
                logger.debug(f"Already using default config, skipping check for {section_name}")

    def get_value(self, section_name, value):
        try:
            return self._config[section_name][value]
        except KeyError as e:
            if not self.using_default_config:
                logger.warn(f"{section_name}:{value} not found in loaded config. Checking default config")
                try:
                    return self._default_config[section_name][value]
                except KeyError as e:
                    logger.error(f"No defaults found for {section_name}:{value}")
                    raise(e)
            else:
                logger.debug(f"Already using default config, skipping check for {section_name}:{value}")

    def load_config(self):
        self._config = None
        self.using_default_config = False

        try:
            config_file_path = self.discover_config_file()
            try:
                with open(config_file_path, 'r+') as config_file_handle:
                    self._config = json.loads(config_file_handle.read())
            except json.decoder.JSONDecodeError as e:
                logger.warning("Unable to parse config. Using default configuration")
                self.using_default_config = True
                self._config = default_config
        except AugurConfigFileNotFoundException as e:
            logger.warning("Config file not found. Using default configuration")
            self.using_default_config = True
            self._config = default_config

        self.load_env_configuration()

    def discover_config_file(self):
        default_config_path = self._root_augur_dir + '/' + self._default_config_file_name
        config_file_path = None

        config_locations = [self._default_config_file_name, default_config_path
         , f"/opt/augur/{self._default_config_file_name}"]
        if os.getenv('AUGUR_CONFIG_FILE', None) is not None:
            config_file_path = os.getenv('AUGUR_CONFIG_FILE')
        else:
            for location in config_locations:
                try:
                    f = open(location, "r+")
                    config_file_path = os.path.abspath(location)
                    f.close()
                    break
                except FileNotFoundError:
                    logger.debug(f"No config file found at {config_file_path}")
                    pass
        if config_file_path:
            return config_file_path
        else:
            raise(AugurConfigFileNotFoundException(message=f"{self._default_config_file_name} not found", errors=None))

    def load_env_configuration(self):
        self.set_env_value(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY')
        self.set_env_value(section='Database', name='host', environment_variable='AUGUR_DB_HOST')
        self.set_env_value(section='Database', name='name', environment_variable='AUGUR_DB_NAME')
        self.set_env_value(section='Database', name='port', environment_variable='AUGUR_DB_PORT')
        self.set_env_value(section='Database', name='user', environment_variable='AUGUR_DB_USER')
        self.set_env_value(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD')
        self.set_env_value(section='Development', name='log_level', environment_variable='AUGUR_LOG_LEVEL')
        self.set_env_value(section='Development', name='verbose', environment_variable='AUGUR_LOG_VERBOSE')
        self.set_env_value(section='Development', name='quiet', environment_variable='AUGUR_LOG_QUIET')

    def set_env_value(self, section, name, environment_variable, sub_config=None):
        """
        Sets names and values of specified config section according to their environment variables.
        """
        # using sub_config lets us grab values from nested config blocks
        if sub_config is None:
            sub_config = self._config

        env_value = os.getenv(environment_variable)

        if env_value is not None:
            self._env_config[environment_variable] = env_value
            sub_config[section][name] = env_value
            logger.debug(f"{section}:{name} set to {env_value} from envvar: {environment_variable}")

    def get_raw_config(self):
        return self._config


class AugurConfigFileNotFoundException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
