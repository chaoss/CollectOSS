#SPDX-License-Identifier: MIT
from augur.application import Application
from augur.augurplugin import AugurPlugin
from augur import logger

class MetricsStatusPlugin(AugurPlugin):
    """
    This plugin determines the implementation status of CHAOSS metrics within Augur
    """
    def __init__(self, augur):
        self.__metrics_status = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .metrics_status import MetricsStatus
        if self.__metrics_status is None:
            logger.debug('Initializing MetricsStatus')
            self.__metrics_status = MetricsStatus(self._augur['githubapi']())
        return self.__metrics_status

    def create_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)

MetricsStatusPlugin.augur_plugin_meta = {
    'name': 'metrics_status',
    'datasource': True
}
Application.register_plugin(MetricsStatusPlugin)

__all__ = ['MetricsStatusPlugin']
