#SPDX-License-Identifier: MIT
import os
import json
import logging

from augur.logging import ROOT_AUGUR_DIRECTORY

ENVVAR_PREFIX = "AUGUR_"
CONFIG_HOME = f"{os.getenv('HOME', '~')}/.augur"

default_config = {
        "version": 1,
        "Augur": {
            "developer": 0
        },
        "Database": {
            "name": "augur",
            "host": "localhost",
            "key": "key",
            "password": "augur",
            "port": 5432,
            "user": "augur",
            "gitlab_api_key":"gitlab_api_key"
        },
        "Housekeeper": {
            "jobs": [
                {
                    "all_focused": 1,
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "issues",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_request_commits",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "repo_info",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "repo_group"
                    ],
                    "model": "commits",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_requests",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "contributors",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "insights",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "badges",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "value",
                    "repo_group_id": 0
                },
                {
                    "delay": 100000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_request_files",
                    "repo_group_id": 0
                },
                {
                    "delay": 100000,
                    "given": [
                        "github_url"
                    ],
                    "model": "releases",
                    "repo_group_id": 0
                },
                {
                    "delay": 100000,
                    "given": [
                        "github_url"
                    ],
                    "model": "message_analysis",
                    "repo_group_id": 0
                },
                {
                    "delay": 100000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_request_analysis",
                    "repo_group_id": 0
                },

	        {
	    	"delay": 10000,
		"given":[
		    "git_url"
		],
		"model" : "discourse_analysis",
		"repo_group_id" : 0

	        },
	        {
                "delay": 10000,
                "given": [
                    "git_url"
                ],
                "model": "clustering",
                "repo_group_id": 0
                }
            ]
        },
        "Workers": {
            "facade_worker": {
                "port": 50100,
                "repo_directory": "repos/",
                "switch": 1,
                "workers": 1
            },
            "github_worker": {
                "port": 50200,
                "switch": 1,
                "workers": 1
            },
            "insight_worker": {
                "port": 50300,
                "metrics": {"issues-new": "issues", "code-changes": "commit_count", "code-changes-lines": "added",
                           "reviews": "pull_requests", "contributors-new": "new_contributors"},
                "confidence_interval": 95,
                "contamination": 0.1,
                "switch": 1,
                "workers": 1,
                "training_days": 1000,
                "anomaly_days": 14
            },
            "linux_badge_worker": {
                "port": 50400,
                "switch": 1,
                "workers": 1
            },
            "metric_status_worker": {
                "port": 50500,
                "switch": 0,
                "workers": 1
            },
            "pull_request_worker": {
                "port": 50600,
                "switch": 1,
                "workers": 1
            },
            "repo_info_worker": {
                "port": 50700,
                "switch": 1,
                "workers": 1
            },
            "value_worker": {
                "port": 50800,
                "scc_bin": "scc",
                "switch": 0,
                "workers": 1
            },
            "contributor_worker": {
                "port": 50900,
                "switch": 0,
                "workers": 1
            },
            "gitlab_issues_worker": {
                "port": 51000,
                "switch": 1,
                "workers": 1
            },
            "release_worker": {
                "port": 51100,
                "switch": 1,
                "workers": 1
            },
            "gitlab_merge_request_worker": {
                "port": 51200,
                "switch": 0,
                "workers": 1
            },
            "message_insights_worker": {
                "port": 51300,
                "switch": 0,
                "workers": 1,
                "insight_days": 30,
                "models_dir": "message_models"
            },
            "pull_request_analysis_worker": {
                "port": 51400,
                "switch": 0,
                "workers": 1,
                "insight_days": 30
            },
            "discourse_analysis_worker":{
	    "port" : 51500,
	    "switch": 0,
	    "workers": 1

	    },
	    "clustering_worker": {
            "port": 51600,
            "switch": 0,
            "workers": 1,
	    "max_df" : 0.9,
	    "max_features" : 1000,
	    "min_df": 0.1,
	    "num_clusters" : 4

        }
        },
        "Facade": {
            "check_updates": 1,
            "clone_repos": 1,
            "create_xlsx_summary_files": 1,
            "delete_marked_repos": 0,
            "fix_affiliations": 1,
            "force_analysis": 1,
            "force_invalidate_caches": 1,
            "force_updates": 1,
            "limited_run": 0,
            "multithreaded": 0,
            "nuke_stored_affiliations": 0,
            "pull_repos": 1,
            "rebuild_caches": 1,
            "run_analysis": 1
        },
        "Server": {
            "cache_expire": "3600",
            "host": "0.0.0.0",
            "port": "5000",
            "workers": 4,
            "timeout": 60
        },
        "Frontend": {
            "host": "0.0.0.0",
            "port": "5000"
        },
        "Logging": {
            "logs_directory": "logs/",
            "log_level": "INFO",
            "verbose": 0,
            "quiet": 0,
            "debug": 0
        }
    }

logger = logging.getLogger(__name__)

class AugurConfig():
    """docstring for AugurConfig"""
    def __init__(self, root_augur_dir, given_config={}):
        self._default_config_file_name = 'augur.config.json'
        self._root_augur_dir = root_augur_dir
        self._default_config = default_config
        self._env_config = {}
        self.config_file_location = None
        self.load_config()
        self.version = self.get_version()
        self._config.update(given_config)

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

    def get_version(self):
        try:
            return self._config["version"]
        except KeyError as e:
            logger.warning("No config version found. Setting version to 0.")
            return 0

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

        logger.debug("Attempting to load config file")
        try:
            self.discover_config_file()
            try:
                with open(self.config_file_location, 'r+') as config_file_handle:
                    self._config = json.loads(config_file_handle.read())
                    logger.debug("Config file loaded successfully")
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
        developer_config_location = ROOT_AUGUR_DIRECTORY + "/" + self._default_config_file_name
        config_file_path = None

        config_locations = [developer_config_location, CONFIG_HOME + "/" + self._default_config_file_name
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
                    pass
        if config_file_path:
            self.config_file_location = config_file_path
        else:
            raise(AugurConfigFileNotFoundException(message="Config file was not found", errors=None))

    def load_env_configuration(self):
        self.set_env_value(section='Database', name='key', environment_variable='AUGUR_GITHUB_API_KEY')
        self.set_env_value(section='Database', name='host', environment_variable='AUGUR_DB_HOST')
        self.set_env_value(section='Database', name='name', environment_variable='AUGUR_DB_NAME')
        self.set_env_value(section='Database', name='port', environment_variable='AUGUR_DB_PORT')
        self.set_env_value(section='Database', name='user', environment_variable='AUGUR_DB_USER')
        self.set_env_value(section='Database', name='password', environment_variable='AUGUR_DB_PASSWORD')
        self.set_env_value(section='Logging', name='log_level', environment_variable='AUGUR_LOG_LEVEL')
        self.set_env_value(section='Logging', name='quiet', environment_variable='AUGUR_LOG_QUIET')
        self.set_env_value(section='Logging', name='debug', environment_variable='AUGUR_LOG_DEBUG')
        self.set_env_value(section='Logging', name='verbose', environment_variable='AUGUR_LOG_VERBOSE')

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
            # logger.info(f"{section}:[\"{name}\"] set to {env_value} by: {environment_variable}")
        else:
            self._env_config[environment_variable] = self.get_value(section, name)

    def get_raw_config(self):
        return self._config

    def get_default_config(self):
        return self._default_config

    def get_env_config(self):
        return self._env_config

class AugurConfigFileNotFoundException(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
