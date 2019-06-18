# #SPDX-License-Identifier: MIT
# from augur.application import Application
# from augur.augurplugin import AugurPlugin
# from augur import logger
# import logging
# logging.basicConfig(filename='worker.log', level=logging.INFO)

# class BrokerHandler(AugurPlugin):
#     """
    
#     """
#     def __init__(self, augur):
#         self.__broker = self.__call__()
        
#         # _augur will be set by the super init
#         super().__init__(augur)
        

#     def __call__(self):
#         from .broker import Broker
#         return Broker()

#     def create_routes(self, flask_app):
#         """
        
#         """
#         from .routes import create_routes
#         create_routes(flask_app, self.__broker)

# BrokerHandler.augur_plugin_meta = {
#     'name': 'broker',
#     'datasource': True
# }
# Application.register_plugin(BrokerHandler)

# __all__ = ['BrokerHandler']
