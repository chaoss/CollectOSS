# <up>SPDX-License-Identifier: MIT
# from augur.augurplugin import AugurPlugin
# from augur import logger
# from .example_datasource import ExampleDatasource

# class ExamplePlugin(AugurPlugin):
#     """
#     This plugin serves as an example as to how to load plugins into Augur
#     """
#     def __init__(self, augur_app):
#         super().__init__(augur_app)
#         logger.info('example-plugin enabled')

#     def __call__(self):
#         return ExampleDatasource()

#     def add_routes(self, flask_app):
#         """
#         Responsible for adding this plugin's data sources to the API
#         """
#         pass

# ExamplePlugin.register({
#     'name': 'example-plugin'
# })

# __all__ = ['ExamplePlugin']