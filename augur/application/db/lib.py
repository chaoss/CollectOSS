import sqlalchemy as s
import logging
from typing import List, Any, Optional
from augur.application.db.models import Config, CollectionStatus, PullRequest
from augur.application.db import get_session
from augur.application.db.util import execute_session_query

logger = logging.getLogger("db_lib")

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


def get_section(section_name) -> dict:
    """Get a section of data from the config.

    Args:
        section_name: The name of the section being retrieved

    Returns:
        The section data as a dict
    """
    with get_session() as session:

        query = session.query(Config).filter_by(section_name=section_name)
        section_data = execute_session_query(query, 'all')
        
        section_dict = {}
        for setting in section_data:
            setting_dict = setting.__dict__

            setting_dict = convert_type_of_value(setting_dict, logger)

            setting_name = setting_dict["setting_name"]
            setting_value = setting_dict["value"]

            section_dict[setting_name] = setting_value

        return section_dict


def get_value(section_name: str, setting_name: str) -> Optional[Any]:
    """Get the value of a setting from the config.

    Args:
        section_name: The name of the section that the setting belongs to 
        setting_name: The name of the setting

    Returns:
        The value from config if found, and None otherwise
    """

    with get_session() as session:


        # TODO temporary until added to the DB schema
        if section_name == "frontend" and setting_name == "pagination_offset":
            return 25

        try:
            query = session.query(Config).filter(Config.section_name == section_name, Config.setting_name == setting_name)
            config_setting = execute_session_query(query, 'one')
        except s.orm.exc.NoResultFound:
            return None

        setting_dict = config_setting.__dict__

        setting_dict = convert_type_of_value(setting_dict, logger)

        return setting_dict["value"]
    

def get_secondary_data_last_collected(repo_id):
    
    with get_session() as session:
        try:
           return session.query(CollectionStatus).filter(CollectionStatus.repo_id == repo_id).one().secondary_data_last_collected 
        except s.orm.exc.NoResultFound:
            return None
        
def get_updated_prs(since):
    
    with get_session() as session:
        return session.query(PullRequest).filter(PullRequest.pr_updated_at >= since).order_by(PullRequest.pr_src_number).all()
            
