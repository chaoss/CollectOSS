#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class LibrariesIOPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__librariesio = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .librariesio import LibrariesIO
        if self.__librariesio is None:
            logger.debug('Initializing LibrariesIO')
            self.__librariesio = LibrariesIO(
                user=self._augur.read_config('Database', 'user', 'AUGUR_LIBRARIESIO_DB_USER', 'root'),
                password=self._augur.read_config('Database', 'pass', 'AUGUR_LIBRARIESIO_DB_PASS', 'password'),
                host=self._augur.read_config('Database', 'host', 'AUGUR_LIBRARIESIO_DB_HOST', '127.0.0.1'),
                port=self._augur.read_config('Database', 'port', 'AUGUR_LIBRARIESIO_DB_PORT', '3306'),
                dbname=self._augur.read_config('Database', 'name', 'AUGUR_LIBRARIESIO_DB_NAME', 'librariesio')
            )
        return self.__librariesio

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)

LibrariesIOPlugin.register({
    'name': 'librariesio'
})

__all__ = ['LibrariesIOPlugin']