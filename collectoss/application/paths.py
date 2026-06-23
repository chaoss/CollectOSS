from collectoss.application.environment import SystemEnv


class SystemPaths:
    """Enable consistent storage and retrieval of filesystem paths needed by the system"""

    def get_facade_directory(self) -> str:
        """Get the facade directory"""
        return SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY")

    def get_config_directory(self) -> str:
        """Get the config directory"""
        return SystemEnv.get("CONFIG_DATADIR")

    def get_logs_directory(self) -> str:
        """Get the logs directory"""
        return SystemEnv.get("COLLECTOSS_LOGS_DIRECTORY")

    def get_cache_directory(self) -> str:
        """Get the cache directory"""
        return SystemEnv.get("CACHE_DATADIR")
