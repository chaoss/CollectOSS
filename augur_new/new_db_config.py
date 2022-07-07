
from db.models import Config

class AugurConfig():

    def __init__(self, session, logger):

        self.session = session
        self.logger = logger

    
    def add_or_update_setting(section, setting_name, value):

        setting_type = value.__class__.__name__

        if setting_type == "NoneType":
            setting_type = None

        config_row = {
            "section": section,
            "name": setting_name,
            "value": value,
            "type": setting_type
        }

        session.insert_data(config_row, Config, ["section", "name"])

    def insert_json_to_config(section_name, data):

        config_rows = []
        for key in list(data.keys()):

            value = data[key]
            name = key

            add_or_update_setting(section_name, name, value)


    def get_section(section):

        section = Config.query.filter_by(section=section).all()

        section_dict = {}

        for setting in section:
            setting_dict = setting.__dict__

            setting_dict = convert_type_of_value(setting_dict)

            setting_name = setting_dict["name"]
            setting_value = setting_dict["value"]

            section_dict[setting_name] = setting_value

        return section_dict


    def get_value(section, name):

        config_setting = Config.query.filter_by(section=section, name=name).one()

        if config_setting is None:
            logger.info("Could not find this value in the config")
            return None

        setting_dict = config_setting.__dict__

        setting_dict = convert_type_of_value(setting_dict)

        return setting_dict["value"]


    def convert_type_of_value(config_dict):
        
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

        else:
            logger.info(f"Need to add support for {data_type} types to config")

        return config_dict

    def load_config() -> dict:

        # get all the sections in the config table
        sections = Config.query.with_entities(Config.section).distinct().all()

        config = {}
        # loop through and get the data for each section
        for section in sections:

            section_data = get_section(section[0])

            # rows with a section of None are on the top level, 
            # so we are adding these values to the top level rather 
            # than creating a section for them
            if section[0] is None:
                for key in list(section_data.keys()):
                    config[key] = section_data[key]
                continue

            # add section data to config object
            config[section[0]] = section_data

        return config
        
