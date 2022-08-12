import logging

from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig

logger = logging.getLogger(__name__)

with DatabaseSession(logger) as session:
        
    config = AugurConfig(logger, session)

redis_db_number = config.get_value("Redis", "database_number") * 3