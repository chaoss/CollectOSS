import sqlalchemy as s
import json

from augur.application.db.models import Config 

default_config = {
            "Augur": {
                "developer": 0,
                "version": 2
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
                "verbose": 0,
                "quiet": 0,
                "debug": 0
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

    def get_section(self, section_name):

        section_data = self.session.query(Config).filter_by(section_name=section_name).all()
        
        section_dict = {}
        for setting in section_data:
            setting_dict = setting.__dict__

            setting_dict = convert_type_of_value(setting_dict, self.logger)

            setting_name = setting_dict["setting_name"]
            setting_value = setting_dict["value"]

            section_dict[setting_name] = setting_value

        return section_dict


    def get_value(self, section_name, setting_name):

        try:
            config_setting = self.session.query(Config).filter(Config.section_name == section_name, Config.setting_name == setting_name).one()
            # config_setting = Config.query.filter_by(section_name=section_name, setting_name=setting_name).one()
        except s.orm.exc.NoResultFound:
            return None

        setting_dict = config_setting.__dict__

        setting_dict = convert_type_of_value(setting_dict, self.logger)

        return setting_dict["value"]


    def load_config(self) -> dict:

        # get all the sections in the config table
        section_names = self.session.query(Config.section_name).all()

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


    def empty(self):

        return self.session.query(Config).first() is None

    def is_section_in_config(self, section_name):

        return self.session.query(Config).filter(Config.section_name == section_name).first() is not None

    """
    type is optional
    config_row = {
            "section_name": section_name,
            "setting_name": setting_name,
            "value": value,
            "type": data_type # optional
        }
    """
    def add_or_update_settings(self, settings):

        for setting in settings:

            if "type" not in setting:
                setting["type"] = setting["value"].__class__.__name__

            if setting["type"] == "NoneType":
                setting["type"] = None

        self.session.insert_data(settings,Config, ["section_name", "setting_name"])
       

    def add_section_from_json(self, section_name, json_data):

        data_keys = list(json_data.keys())

        settings = []
        for key in data_keys:

            value = json_data[key]

            if type(value) == dict:
                self.logger.error("Values cannot be of type dict")
                return

            setting = {
                "section_name": section_name,
                "setting_name": key,
                "value": json_data[key],
            }
            settings.append(setting)

        self.add_or_update_settings(settings)


    def load_config_file(self, file_path):
        with open(file_path, 'r') as f:
            file_data = json.load(f)

            return file_data

    def load_config_from_dict(self, dict_data):

        section_names = list(dict_data.keys())

        for section_name in section_names:
            
            value = dict_data[section_name]

            # check for "sections" that are actually just a key value pair 
            # and not a key that has a value of type dict
            if type(value) == dict:
                self.add_section_from_json(section_name=section_name, json_data=value)

            else:
                self.logger.error(f"Error! {section_name}: {value} will not be added because a section must have a dict as its values (all of the top level keys in the config must have a value of type dict")

    def clear(self):
        pass
        # db.session.query(Config).delete()
        # db.session.commit()

    def remove_section(self, section_name):

        Config.query.filter_by(section_name=section_name).delete()

        # db.session.commit()


    def create_default_config(self):

        self.load_config_from_dict(self.default_config)
