#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class GitHubAPIPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__githubapi = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .githubapi import GitHubAPI
        if self.__githubapi is None:
            logger.debug('Initializing GitHub API')
            api_key=self._augur.read_config('GitHub', 'apikey', 'AUGUR_GITHUB_API_KEY', 'None')
            self.__githubapi = GitHubAPI(api_key=api_key)
        return self.__githubapi

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


GitHubAPIPlugin.register({
    'name': 'githubapi'
})

__all__ = ['GitHubAPIPlugin']