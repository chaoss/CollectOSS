from collectoss.application.environment import SystemEnv
from pathlib import Path

def _verify_path(path: Path, create = True) -> Path:
    """Verify the path is a valid directory"""
    if create:
        if not path.exists():
            path.mkdir(parents=True)
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a valid directory")
    return path.resolve()


def _path_from_env(env_value: str) -> Path:
    """Get the path from the environment variable"""
    if env_value is None:
        return None
    if env_value == "":
        return None
    return Path(env_value)

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
