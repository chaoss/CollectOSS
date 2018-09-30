#SPDX-License-Identifier: MIT
"""
Provides a class that can be used to extend Augur
"""
class AugurPlugin(object):
    """
    Defines a base class for Augur plugins to implement
    """
    def __init__(self, augur_app):
        self._augur = augur_app

    @classmethod
    def register(cls, metadata, datasource=False):
        from augur.application import Application
        cls.augur_plugin_meta = metadata

        if datasource:
            Application.register_datasource(cls)
        else:
            Application.register_plugin(cls)

    def create_routes(self, server):
        pass

    @staticmethod
    def update(shared):
        """
        Should implement a function that gathers data
        """
        pass