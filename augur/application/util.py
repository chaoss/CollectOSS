import logging

from augur.application.db.session import DatabaseSession
from augur.application.db.engine import DatabaseEngine
from augur.util.repo_load_controller import RepoLoadController

logger = logging.getLogger(__name__)

def get_all_repos(page=0, page_size=25, sort="repo_id", direction="ASC", **kwargs):

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        controller = RepoLoadController(session)

        result = controller.paginate_repos("all", page, page_size, sort, direction, **kwargs)

        return result

def get_all_repos_count(**kwargs):

    with DatabaseEngine() as engine, DatabaseSession(logger, engine) as session:

        controller = RepoLoadController(session)

        result = controller.get_repo_count(source="all", **kwargs)

        return result


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