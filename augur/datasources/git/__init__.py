#SPDX-License-Identifier: MIT
from augur.augurplugin import AugurPlugin
from augur import logger

class GitPlugin(AugurPlugin):
    """
    This plugin serves as an example as to how to load plugins into Augur
    """
    def __init__(self, augur):
        self.__git = None
        # _augur will be set by the super init
        super().__init__(augur)

    def __call__(self):
        from .git import Git
        storage = self._augur.path_relative_to_config(
            self._augur.read_config_path('Git', 'storage', 'AUGUR_GIT_STORAGE', '$(RUNTIME)/git_repos/')
        )
        repolist = self._augur.read_config('Git', 'repositories', None, [])
        if self.__git is None:
            logger.debug('Initializing Git')
            self._augur.__git = Git(
                list_of_repositories=repolist,
                storage_folder=storage,
                csv=None,
                cache=self._augur.cache
            )
        return self._augur.__git

    def add_routes(self, flask_app):
        """
        Responsible for adding this plugin's data sources to the API
        """
        from .routes import create_routes
        create_routes(flask_app)


GitPlugin.register({
    'name': 'git'
})

__all__ = ['GitPlugin']