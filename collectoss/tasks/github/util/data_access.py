from keyman.KeyClient import KeyClient
import logging
class DataAccess:
    """Base class for shared HTTP data access functionality"""
    
    def __init__(self, platform_name: str,logger: logging.Logger, key_client = None):
    
        self.logger = logger
        self.key_client = KeyClient(platform_name, logger) if key_client is None else key_client
        self.key = None
        self.expired_keys_for_request = []

    def __handle_not_authorized_response(self):

        self.key = self.key_client.invalidate(self.key)