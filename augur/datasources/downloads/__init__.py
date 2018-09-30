#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class DownloadsPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__downloads = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .downloads import Downloads
        if self.__downloads is None:
            logger.debug('Initializing Downloads')
            self.__downloads = Downloads(self._augur['githubapi']())
        return self.__downloads

    def create_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


DownloadsPlugin.register({
    'name': 'downloads'
}, datasource=True)

__all__ = ['DownloadsPlugin']