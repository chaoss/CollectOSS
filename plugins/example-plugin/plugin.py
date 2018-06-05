#SPDX-License-Identifier: MIT
from augur import register_plugin, logger
from augur.server import addMetric
# (don't remove the above line, it's for a script)

class ExamplePlugin(object):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self):
        logger.info('example-plugin loaded')
        return

    def example_metric(self, owner, repo):
        return []


def add_routes(app, instance):
    """
    Responsible for adding this plugin's data sources to the API
    """
    addMetric(app, instance.example_metric, 'example-metric')



register_plugin(ExamplePlugin, 'example-plugin', routes='routes.py')