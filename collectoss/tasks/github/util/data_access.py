from keyman.KeyClient import KeyClient
import logging
class DataAccess:
    """Base class for shared HTTP data access functionality"""
    
    def __init__(self, platform_name: str,logger: logging.Logger, key_client:KeyClient = None):
        """Initializes the DataAccess object

        Args:
            platform_name (str): the name primarily used to identify this platform's API limits to keyman. Example: "github_rest" or "github_graphql"
            logger (logging.Logger): the logger to use for this class
            key_client (KeyClient, optional): An instance of keyclient to use instead of creating one. Intended for testing purposes. Defaults to None (create a new one).
        """
    
        self.logger = logger
        self.platform_name = platform_name
        self.key_client = KeyClient(platform_name, logger) if key_client is None else key_client
        self.key = None
        self.expired_keys_for_request = []

    def __handle_not_authorized_response(self):

        self.key = self.key_client.invalidate(self.key)