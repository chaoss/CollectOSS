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

    def create_routes(self, server):
        pass

    @staticmethod
    def update(shared):
        """
        Should implement a function that gathers data
        """
        pass