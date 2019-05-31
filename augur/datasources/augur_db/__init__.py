#SPDX-License-Identifier: MIT
from augur.application import Application
from augur.augurplugin import AugurPlugin
from augur import logger

class AugurPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__augur_db = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .augur_db import Augur
        if self.__augur_db is None:
            logger.debug('Initializing Augur New Schema')
            self.__augur_db = Augur(
                user=self._augur.read_config('Database', 'user', 'AUGUR_DB_USER', 'augur'),
                password=self._augur.read_config('Database', 'password', 'AUGUR_DB_PASS', 'password'),
                host=self._augur.read_config('Database', 'host', 'AUGUR_DB_HOST', '127.0.0.1'),
                port=self._augur.read_config('Database', 'port', 'AUGUR_DB_PORT', '5433'),
                dbname=self._augur.read_config('Database', 'name', 'AUGUR_DB_NAME', 'augur'),
                schema=self._augur.read_config('Database', 'schema', 'AUGUR_DB_SCHEMA', 'augur_data')
            )
        return self.__augur_db

    def create_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)

AugurPlugin.augur_plugin_meta = {
    'name': 'augur_db',
    'datasource': True
}
Application.register_plugin(AugurPlugin)

__all__ = ['AugurPlugin']
