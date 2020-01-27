# # SPDX-License-Identifier: MIT
# from augur.augurplugin import AugurPlugin
# from augur.application import Application

# class HousekeeperPlugin(AugurPlugin):
#     """
#     This plugin serves as an example as to how to load plugins into Augur
#     """
#     def __init__(self, augur_app):
#         super().__init__(augur_app)
#         self.__housekeeper = self.__call__()

#     def __call__(self):
#         from .housekeeper import Housekeeper
#         return Housekeeper(
#                 user=self._augur.read_config('Database', 'user', 'AUGUR_DB_USER', 'root'),
#                 password=self._augur.read_config('Database', 'password', 'AUGUR_DB_PASSWORD', 'password'),
#                 host=self._augur.read_config('Database', 'host', 'AUGUR_DB_HOST', '0.0.0.0'),
#                 port=self._augur.read_config('Database', 'port', 'AUGUR_DB_PORT', '3306'),
#                 dbname=self._augur.read_config('Database', 'database', 'AUGUR_DB_NAME', 'msr14')
#             )


# HousekeeperPlugin.augur_plugin_meta = {
#     'name': 'housekeeper',
#     'datasource': True
# }
# Application.register_plugin(HousekeeperPlugin)

# __all__ = ['HousekeeperPlugin']