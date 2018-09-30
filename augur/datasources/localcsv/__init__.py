#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class LocalCSVPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__localCSV= None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from augur.localcsv import LocalCSV
        if self.__localCSV is None:
            logger.debug('Initializing LocalCSV')
            self.__localCSV = LocalCSV()
        return self.__localCSV

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


LocalCSVPlugin.register({
    'name': 'localcsv'
})

__all__ = ['LocalCSVPlugin']