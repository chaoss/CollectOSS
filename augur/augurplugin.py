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
        """
        Creates a route for the given plugin and assigns it to the server

        :param server: desired server to create plugin route
        """
        pass

    @staticmethod
    def update(shared):
        """
        Should implement a function that gathers data
        """
        pass