from platformdirs import PlatformDirs
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
    """Enable consistent storage and retrieval of filesystem paths needed by the system
    
    The paths that are used follow the following hierarchy:
    - Absolute path specified by an environment variable
    - Relative path specified by an environment variable, resolved against the home directory
    - Default path for the operating system based on accepted standards
    
    """
    app_name = "CollectOSS"
    app_org = "CHAOSS"
    # Automatically targets the proper OS directory and handles creation
    dirs = PlatformDirs(app_name, app_org, ensure_exists=True)

    def _build_path(self, env_path:str, default_path:Path) -> Path:
        """Build a path from the environment variable or the default path.
        
        If the environment variable is an absolute path, return it.
        If the environment variable is a relative path, resolve it against the home directory.
        If the environment variable is not set, return the default path.
        """
        if env_path is not None:
            if env_path.is_absolute():
                return env_path
            else:
                return _path_from_env(SystemEnv.get("HOME")) / env_path
        else:
            return default_path

    def get_facade_directory(self, create = True) -> Path:
        """Get the facade directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY"))

        return _verify_path(
            self._build_path(env_path, self.dirs.user_downloads_path / "collectoss_facade"),
            create = create
        )

    def get_config_directory(self, create = True) -> Path:
        """Get the config directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_CONFIG_DIRECTORY") or SystemEnv.get("CONFIG_DATADIR"))

        return _verify_path(
            self._build_path(env_path, self.dirs.user_config_path),
            create = create
        )

    def get_logs_directory(self, create = True) -> Path:
        """Get the logs directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_LOGS_DIRECTORY"))

        return _verify_path(
            self._build_path(env_path, self.dirs.user_log_path),
            create = create
        )

    def get_cache_directory(self, create = True) -> Path:
        """Get the cache directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_CACHE_DIRECTORY") or SystemEnv.get("CACHE_DATADIR"))

        return _verify_path(
            self._build_path(env_path, self.dirs.user_cache_path),
            create = create
        )
