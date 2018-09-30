#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class FacadePlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__facade = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .facade import Facade
        if self.__facade is None:
            logger.debug('Initializing Facade')
            self.__facade = Facade(
                user=self._augur.read_config('Facade', 'user', 'AUGUR_FACADE_DB_USER', 'root'),
                password=self._augur.read_config('Facade', 'pass', 'AUGUR_FACADE_DB_PASS', ''),
                host=self._augur.read_config('Facade', 'host', 'AUGUR_FACADE_DB_HOST', '127.0.0.1'),
                port=self._augur.read_config('Facade', 'port', 'AUGUR_FACADE_DB_PORT', '3306'),
                dbname=self._augur.read_config('Facade', 'name', 'AUGUR_FACADE_DB_NAME', 'facade'),
                projects=self._augur.read_config('Facade', 'projects', None, [])
            )
        return self.__facade

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


FacadePlugin.register({
    'name': 'facade'
})

__all__ = ['FacadePlugin']