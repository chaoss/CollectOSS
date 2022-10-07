import uuid
import os

def get_development_flag_from_config():
    from augur.application.config import AugurConfig
    from augur.application.db.session import DatabaseSession
    from logging import getLogger

    logger = getLogger(__name__)
    with DatabaseSession(logger) as session:

        config = AugurConfig(logger, session)

        section = "Augur"
        setting = "developer"

        return config.get_value(section, setting)


instance_id = uuid.uuid4().hex
development = os.getenv("AUGUR_DEV") or get_development_flag_from_config() or False





