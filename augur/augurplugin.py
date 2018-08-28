#SPDX-License-Identifier: MIT
"""
Provides a class that can be used to extend Augur
"""

class AugurPlugin(object):
    """Defines a base class for Augur plugins to implement"""
    def __init__(self, config):
        self.config = config

    @classmethod
    def register(cls, application):
        application.register_plugin(cls)

    def create_routes(self, flask_app):
        routes = __import__('routes')
        routes.create(flask_app)