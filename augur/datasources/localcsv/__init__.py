#SPDX-License-Identifier: MIT
from augur.application import Application
from augur.augurplugin import AugurPlugin
from augur import logger

class LocalCSVPlugin(AugurPlugin):
    """
    Plugin that can read local CSV files
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

    def create_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


LocalCSVPlugin.augur_plugin_meta = {
    'name': 'localcsv',
    'datasource': True
}
Application.register_plugin(LocalCSVPlugin)

__all__ = ['LocalCSVPlugin']