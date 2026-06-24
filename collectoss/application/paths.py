from platformdirs import PlatformDirs
from collectoss.application.environment import SystemEnv
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

def _clean_path(path: Path | str) -> Path | None:
    if path is None:
        return None
    if isinstance(path, str):
        path = Path(path)
    return path.expanduser().resolve()

def _verify_path(path: Path, create = True) -> Path | None:
    """Verify the path is a valid directory"""
    if create:
        if not path.exists():
            path.mkdir(parents=True)
        if not path.is_dir():
            raise ValueError(f"Path {path} is not a valid directory")
    return _clean_path(path)


def _path_from_env(env_value: str) -> Path | None:
    """Get the path from the environment variable"""
    if env_value is None:
        return None
    if env_value == "":
        return None
    return Path(env_value)

def _build_path(env_path:str, default_path:Path) -> Path:
    """Build a path from the environment variable or the default path.
    
    If the environment variable is an absolute path, return it.
    If the environment variable is a relative path, resolve it against the home directory.
    If the environment variable is not set, return the default path.
    """
    if env_path is not None:
        env_path = Path(env_path)
        if env_path.is_absolute():
            return _clean_path(env_path)
        else:
            return _clean_path(Path.home() / env_path)
    else:
        return default_path

class SystemPaths:
    """Enable consistent storage and retrieval of filesystem paths needed by the system
    
    The paths that are used follow the following hierarchy:
    - Absolute path specified by an environment variable
    - Relative path specified by an environment variable, resolved against the home directory
    - Default path for the operating system based on accepted standards
    
    """
    app_name = "CollectOSS"
    app_org = "CHAOSS"

    @staticmethod
    def os_defaults(create = True) -> PlatformDirs:
        """Get the set of conventional directories for the operating system"""
        return PlatformDirs(SystemPaths.app_name, SystemPaths.app_org, ensure_exists=create)

    @staticmethod
    def get_facade_directory(create = True) -> Path:
        """Get the facade directory. Requires database for historical compatibility"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY"))
        database_path = None

        from collectoss.application.config import SystemConfig
        from collectoss.application.db.session import DatabaseSession
        from collectoss.application.db import get_engine
        with DatabaseSession(logger, get_engine()) as session:
            config = SystemConfig(logger, session)
            database_path = config.get_value("Facade", "repo_directory")


        return _verify_path(
            _build_path(env_path or database_path, SystemPaths.os_defaults(create).user_downloads_path / "collectoss_facade"),
            create = create
        )

    @staticmethod
    def get_config_directory(create = True) -> Path:
        """Get the config directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_CONFIG_DIRECTORY") or SystemEnv.get("CONFIG_DATADIR"))

        return _verify_path(
            _build_path(env_path, SystemPaths.os_defaults(create).user_config_path),
            create = create
        )

    @staticmethod
    def get_logs_directory(create = True) -> Path:
        """Get the logs directory. Requires database for historical compatibility"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_LOGS_DIRECTORY"))
        database_path = None

        from collectoss.application.config import SystemConfig
        from collectoss.application.db.session import DatabaseSession
        from collectoss.application.db import get_engine
        with DatabaseSession(logger, get_engine()) as session:
            config = SystemConfig(logger, session)
            database_path = config.get_value("Logging", "logs_directory")

        return _verify_path(
            _build_path(env_path or database_path, SystemPaths.os_defaults(create).user_log_path),
            create = create
        )

    @staticmethod
    def get_cache_directory(create = True) -> Path:
        """Get the cache directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_CACHE_DIRECTORY") or SystemEnv.get("CACHE_DATADIR"))

        return _verify_path(
            _build_path(env_path, SystemPaths.os_defaults(create).user_cache_path),
            create = create
        )

    
    @staticmethod
    def get_models_directory(create = True) -> Path:
        """Get the models directory. Requires database for historical compatibility"""
        database_dirname = None

        from collectoss.application.config import SystemConfig
        from collectoss.application.db.session import DatabaseSession
        from collectoss.application.db import get_engine
        with DatabaseSession(logger, get_engine()) as session:
            config = SystemConfig(logger, session)
            database_dirname = config.get_value("Message_Insights", 'models_dir') or "message_models"
        
        return _verify_path(
            SystemPaths.os_defaults(create).user_data_path / "tasks" / "data_analysis" / "message_insights" / database_dirname,
            create = create
        )
    
    @staticmethod
    def get_model_training_data_directory(create = True) -> Path:
        """Get the model training data directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_ANALYSIS_DIRECTORY"))
        return _verify_path(
            _build_path(env_path / "message_insights" / "train_data", SystemPaths.os_defaults(create).user_data_path / "tasks" / "data_analysis" / "message_insights" / "train_data"),
            create = create
        )

    @staticmethod
    def get_discourse_analysis_directory(create = True) -> Path:
        """Get the discourse analysis directory"""
        env_path = _path_from_env(SystemEnv.get("COLLECTOSS_ANALYSIS_DIRECTORY"))
        return _verify_path(
            _build_path(env_path / "discourse_analysis", SystemPaths.os_defaults(create).user_data_path / "tasks" / "data_analysis" / "discourse_analysis"),
            create = create
        )

    @staticmethod
    def get_install_path() -> Path:
        """Get the path that CollectOSS is currently installed to. This should be treated as read- only."""
        # This paths file is only one level below the root of the module.
        # accessing above that is not possible as the module could be installed separately
        return _verify_path(Path(__file__).parent, create = False)
    
    @staticmethod
    def print_all_paths(logger):
        logger.info(f"Install path: {SystemPaths.get_install_path()}")
        logger.info(f"Facade directory: {SystemPaths.get_facade_directory(create = False)}")
        logger.info(f"Config directory: {SystemPaths.get_config_directory(create = False)}")
        logger.info(f"Logs directory: {SystemPaths.get_logs_directory(create = False)}")
        logger.info(f"Cache directory: {SystemPaths.get_cache_directory(create = False)}")
        logger.info(f"Models directory: {SystemPaths.get_models_directory(create = False)}")
        logger.info(f"Model training data directory: {SystemPaths.get_model_training_data_directory(create = False)}")
        logger.info(f"Discourse analysis directory: {SystemPaths.get_discourse_analysis_directory(create = False)}")