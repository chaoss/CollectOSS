import sqlalchemy as s
import json
from typing import List, Any, Optional
import os
from augur.application.db.models import Config 
from augur.application.db.util import execute_session_query

def get_development_flag_from_config():
    
    from logging import getLogger
    from augur.application.db.session import DatabaseSession

    logger = getLogger(__name__)
    with DatabaseSession(logger) as session:

        config = AugurConfig(logger, session)

        section = "Augur"
        setting = "developer"

        return config.get_value(section, setting)

def get_development_flag():
    return os.getenv("AUGUR_DEV") or get_development_flag_from_config() or False



default_config = {
            "Augur": {
                "developer": 0,
                "version": 1
            },
            "Keys": {
                "github": "<gh_api_key>",
                "gitlab": "<gl_api_key>"
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
                "multithreaded": 1,
                "nuke_stored_affiliations": 0,
                "pull_repos": 1,
                "rebuild_caches": 1,
                "run_analysis": 1
            },
            "Server": {
                "cache_expire": "3600",
                "host": "0.0.0.0",
                "port": 5000,
                "workers": 6,
                "timeout": 6000,
                "ssl": False,
                "ssl_cert_file": None, 
                "ssl_key_file": None 
            },
            "Logging": {
                "logs_directory": "",
                "log_level": "INFO",
            },
            "Celery": {
                "concurrency": 12
            },
            "Redis": {
                "cache_group": 0, 
                "connection_string": "redis://127.0.0.1:6379/"
            },
            "Tasks": {
                "collection_interval": 2592000
            },
            "Message_Insights": {
                    "insight_days": 30,
                    "models_dir": "message_models"
            },
            "Clustering_Task": {
                "max_df": 0.9,
                "max_features": 1000,
                "min_df": 0.1,
                "num_clusters": 4
            },
            "Insight_Task": {
                # TODO: How to store metrics in database config?
                "confidence_interval": 95,
                "contamination": 0.1,
                "switch": 1,
                "workers": 1,
                "training_days": 1000,
                "anomaly_days": 14
            },
            "Task_Routine": {
                "prelim_phase": 1,
                "repo_collect_phase": 1,
                "machine_learning_phase": 0
            }
        }


def convert_type_of_value(config_dict, logger=None):
        
        data_type = config_dict["type"]

        if data_type == "str" or data_type is None:
            return config_dict

        elif data_type == "int":
            config_dict["value"] = int(config_dict["value"])

        elif data_type == "bool":
            value = config_dict["value"]
            
            if value.lower() == "false":
                config_dict["value"] = False
            else:
                config_dict["value"] = True

        elif data_type == "float":
            config_dict["value"] = float(config_dict["value"])

        else:
            if logger:
                logger.error(f"Need to add support for {data_type} types to config") 
            else:
                print(f"Need to add support for {data_type} types to config")

        return config_dict

class AugurConfig():

    def __init__(self, logger, session):

        self.session = session
        self.logger = logger

        self.accepted_types = ["str", "bool", "int", "float", "NoneType"]
        self.default_config = default_config

    def get_section(self, section_name) -> dict:
        """Get a section of data from the config.

        Args:
            section_name: The name of the section being retrieved

        Returns:
            The section data as a dict
        """
        query = self.session.query(Config).filter_by(section_name=section_name)
        section_data = execute_session_query(query, 'all')
        
        section_dict = {}
        for setting in section_data:
            setting_dict = setting.__dict__

            setting_dict = convert_type_of_value(setting_dict, self.logger)

            setting_name = setting_dict["setting_name"]
            setting_value = setting_dict["value"]

            section_dict[setting_name] = setting_value

        return section_dict


    def get_value(self, section_name: str, setting_name: str) -> Optional[Any]:
        """Get the value of a setting from the config.

        Args:
            section_name: The name of the section that the setting belongs to 
            setting_name: The name of the setting

        Returns:
            The value from config if found, and None otherwise
        """
        try:
            query = self.session.query(Config).filter(Config.section_name == section_name, Config.setting_name == setting_name)
            config_setting = execute_session_query(query, 'one')
        except s.orm.exc.NoResultFound:
            return None

        setting_dict = config_setting.__dict__

        setting_dict = convert_type_of_value(setting_dict, self.logger)

        return setting_dict["value"]


    def load_config(self) -> dict:
        """Get full config as a dictionary.
        
        Returns:
            The config from the database
        """
        # get all the sections in the config table
        query = self.session.query(Config.section_name)
        section_names = execute_session_query(query, 'all')

        config = {}
        # loop through and get the data for each section
        for section_name in section_names:

            section_data = self.get_section(section_name[0])

            # rows with a section of None are on the top level, 
            # so we are adding these values to the top level rather 
            # than creating a section for them
            if section_name[0] is None:
                for key in list(section_data.keys()):
                    config[key] = section_data[key]
                continue

            # add section data to config object
            config[section_name[0]] = section_data

        return config


    def empty(self) -> bool:
        """Determine if a config is empty.
        
        Returns:
            True if the config is empty, and False if it is not
        """
        query = self.session.query(Config)
        return execute_session_query(query, 'first') is None

    def is_section_in_config(self, section_name: str) -> bool:
        """Determine if a section is in the config.
        
        Args:
            section_name: section to search for in config

        Returns:
            True if section is in the config, and False if it is not
        """
        query = self.session.query(Config).filter(Config.section_name == section_name)
        return execute_session_query(query, 'first') is not None


    def add_or_update_settings(self, settings: List[dict]):
        """Add or update a list of settings.

        Args:
            list of settings with dicts containing section_name, setting_name, value, and optionally type

        Examples:
            type is optional
            setting = {
                    "section_name": section_name,
                    "setting_name": setting_name,
                    "value": value,
                    "type": data_type # optional
                }
        """
        for setting in settings:

            if "type" not in setting:
                setting["type"] = setting["value"].__class__.__name__

            if setting["type"] == "NoneType":
                setting["type"] = None

        #print(f"\nsetting: {settings}")
        self.session.insert_data(settings,Config, ["section_name", "setting_name"])
       

    def add_section_from_json(self, section_name: str, json_data: dict) -> None:
        """Add a section from a dict.
        
        Args:
            section_name: The name of the section being added
            json_data: The data being added
        """
        data_keys = list(json_data.keys())

        settings = []
        for key in data_keys:

            value = json_data[key]

            if isinstance(value, dict) is True:
                # TODO: Uncomment out when insights worker config stuff is resolved
                # self.logger.error(f"Values cannot be of type dict: {value}")
                return

            setting = {
                "section_name": section_name,
                "setting_name": key,
                "value": json_data[key],
            }
            settings.append(setting)

        self.add_or_update_settings(settings)


    def load_config_file(self, file_path: str) -> dict:
        """Add a section from a dict.
        
        Args:
            file_path: Path to json file being loaded

        Returns:
            data in the json file
        """
        with open(file_path, 'r') as f:
            file_data = json.load(f)

            return file_data

    def load_config_from_dict(self, dict_data: dict) -> None:
        """Create config from a dict.
        
        Args:
            dict_data: The data being loaded into the config
        """
        section_names = list(dict_data.keys())

        for section_name in section_names:
            
            value = dict_data[section_name]
            #print(f"\n{value}")
            # check for "sections" that are actually just a key value pair 
            # and not a key that has a value of type dict
            if isinstance(value, dict) is True:
                self.add_section_from_json(section_name=section_name, json_data=value)

            else:
                self.logger.error(f"Error! {section_name}: {value} will not be added because a section must have a dict as its values (all of the top level keys in the config must have a value of type dict")

    def clear(self) -> None:
        """Remove all values from the config."""
        self.session.query(Config).delete()
        self.session.commit()

    def remove_section(self, section_name: str) -> None:
        """Remove a section from the config.
        
        Args:
            section_name: The name of the section being deleted
        """
        self.session.query(Config).filter(Config.section_name == section_name).delete()
        self.session.commit()


    def create_default_config(self) -> None:
        """Create default config in the database."""
        self.load_config_from_dict(self.default_config)
