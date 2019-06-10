#SPDX-License-Identifier: MIT
from augur.application import Application
from augur.augurplugin import AugurPlugin
from augur import logger

class BrokerHandler(AugurPlugin):
    """
    
    """
    def __init__(self, augur):
        self.__broker = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .broker import Broker
        if self.__broker is None:
            logger.debug('Initializing Broker')
            self.__broker = Broker()
        return self.__broker

    def create_routes(self, flask_app):
        """
        
        """
        from .routes import create_routes
        create_routes(flask_app)

BrokerHandler.augur_plugin_meta = {
    'name': 'broker',
    'datasource': False
}
Application.register_plugin(BrokerHandler)

__all__ = ['BrokerHandler']
