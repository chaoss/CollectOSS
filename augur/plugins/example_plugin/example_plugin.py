#SPDX-License-Identifier: MIT
from augur import AugurPlugin, Application, logger
# (don't remove the above line, it's for a script)

class ExamplePlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, app):
        self.augur_app = app
        logger.info('example-plugin loaded')
        return

    def example_metric(self, owner, repo):
        return 'Hello, {}/{}'.format(owner, repo)

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        flask_app.addMetric(self.example_metric, 'example_metric')

ExamplePlugin.name = 'example-plugin'
Application.register_plugin(ExamplePlugin)