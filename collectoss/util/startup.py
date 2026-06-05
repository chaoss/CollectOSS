## Startup helpers


from pathlib import Path
import os
import getpass
import subprocess
from subprocess import check_call

from sqlalchemy.orm.attributes import get_history
from collectoss.application.config import SystemConfig
from collectoss.application.db.session import DatabaseSession
from collectoss.application.environment import SystemEnv
from typing_extensions import deprecated

from collectoss.util.inspect_without_import import get_phase_names_without_import

ROOT_PROJECT_REPO_DIRECTORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

def check_init_schema():
    """Initialize the CollectOSS database schema as appropriate
    """

    pass
    # does public.alembic_version exist?
        # if yes, do nothing
        # if no, do a sanity check to make sure the other schemas dont exist,
        #   then init the current db with sqlalchemy and stamp the current version with alembic

def check_update_schema():
    """ensure the CollectOSS schema is on the latest version
    """
    pass
    # alembic upgrade head, unless theres an env var preventing automatic migration
    check_call(["alembic", "upgrade", "head"])

def collect_env_variables(logger):
    """convenience helper for assembling more complex environment variables out of smaller ones
    and other environment variable convenience operations
    """

    if SystemEnv.get("COLLECTOSS_DB") is None:
        names = ["COLLECTOSS_DB_HOST", "COLLECTOSS_DB_USER", "COLLECTOSS_DB_PASSWORD", "COLLECTOSS_DB_NAME"]
        values = [SystemEnv.get(n) for n in names]

        if all(map(lambda p: p is not None, values)):
            host, user, passwd, name = values
            logger.verbose(f"Assembling COLLECTOSS_DB string from provided variables")
            SystemEnv.set("COLLECTOSS_DB", f"postgresql+psycopg2://{user}:{passwd}@{host}/{name}")
        else:
            logger.warning("CollectOSS was unable to create your database connection string automatically")
            logger.warning("The following environment variables are missing:")
            for n, v in zip(names, values):
                if v is None:
                    logger.warning(n)


    
    db_string = SystemEnv.get("COLLECTOSS_DB")
    if db_string and "localhost" in db_string:
        logger.verbose(f"Swapping localhost in COLLECTOSS_DB string with docker host gateway name")
        SystemEnv.set("COLLECTOSS_DB", db_string.replace("localhost", "host.docker.internal"))
    elif db_string and "127.0.0.1" in db_string:
        logger.verbose(f"Swapping 127.0.0.1 in COLLECTOSS_DB string with docker host gateway name")
        SystemEnv.set("COLLECTOSS_DB", db_string.replace("127.0.0.1", "host.docker.internal"))

    redis_string = SystemEnv.get("REDIS_CONN_STRING")
    if redis_string and "localhost" in redis_string:
        logger.verbose(f"Swapping localhost in REDIS_CONN_STRING with docker host gateway name")
        SystemEnv.set("REDIS_CONN_STRING", redis_string.replace("localhost", "host.docker.internal"))
    elif redis_string and "127.0.0.1" in redis_string:
        logger.verbose(f"Swapping 127.0.0.1 in REDIS_CONN_STRING with docker host gateway name")
        SystemEnv.set("REDIS_CONN_STRING", redis_string.replace("127.0.0.1", "host.docker.internal"))


    # if user didnt specify gitlab credentials, just inject fake ones so we can start up.
    if SystemEnv.get("COLLECTOSS_GITLAB_API_KEY") is None:
        logger.verbose(f"Detected no specified gitlab key, using made up values as a workaround")
        SystemEnv.set("COLLECTOSS_GITLAB_API_KEY", "fake")
    if SystemEnv.get("COLLECTOSS_GITLAB_USERNAME") is None:
        logger.verbose(f"Detected no specified gitlab username, using made up value as a workaround")
        SystemEnv.set("COLLECTOSS_GITLAB_USERNAME", "fake")

    # provide a default value for the facade repo directory (assumes docker paths)
    facade_repo_directory = SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY")
    if facade_repo_directory is None:
        logger.verbose(f"Setting default value for COLLECTOSS_FACADE_REPO_DIRECTORY")
        SystemEnv.set("COLLECTOSS_FACADE_REPO_DIRECTORY", "/collectoss/facade/")
    else:
        # Check if the path is resolveable/make it absolute
        logger.verbose(f"Resolving full path to COLLECTOSS_FACADE_REPO_DIRECTORY")
        SystemEnv.set("COLLECTOSS_FACADE_REPO_DIRECTORY", str(Path(facade_repo_directory).resolve(strict=True)))

    # ensure trailing slash is present
    facade_repo_directory = SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY")
    if facade_repo_directory and not facade_repo_directory.endswith("/"):
        facade_repo_directory += "/"
        SystemEnv.set("COLLECTOSS_FACADE_REPO_DIRECTORY", facade_repo_directory)

@deprecated("The bulk of this function is handling .git-credentials, which will be replaced with pygit2 (see issue #258)", category=None)
def setup_facade_directory(logger):
    """Perform permission checks and create the facade directory if it doesnt exist
    """

    facade_directory_path = SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY") or "/collectoss/facade/"

    facade_directory = Path(facade_directory_path)

    if not facade_directory.exists():
        logger.verbose(f"Specified facade directory {facade_directory_path} does not exist. Creating...")
        facade_directory.mkdir()

    git_credentials = facade_directory.joinpath(".git-credentials")
    git_credentials.touch(exist_ok=True)

    if not os.access(git_credentials, os.R_OK):
        logger.error(f"User {getpass.getuser()} does not have permission to write to {git_credentials}. Please select another location")
    else:
        logger.verbose(f"Permission check passed for {git_credentials}")
     

    credentials = []

    gh_names = ["COLLECTOSS_GITHUB_USERNAME","COLLECTOSS_GITHUB_API_KEY"]
    gh_values = [SystemEnv.get(n) for n in gh_names]

    if all(map(lambda p: p is not None, gh_values)):
        user, key = gh_values
        credentials.append(f"https://{user}:{key}@github.com")


    gl_names = ["COLLECTOSS_GITLAB_USERNAME","COLLECTOSS_GITLAB_API_KEY"]
    gl_values = [SystemEnv.get(n) for n in gl_names]

    if all(map(lambda p: p is not None, gl_values)):
        user, key = gl_values
        credentials.append(f"https://{user}:{key}@gitlab.com")

    with git_credentials.open(encoding="utf-8") as c:
        c.writelines(credentials)
    
    subprocess.call(["git", "config", "--global", "credential.helper", "store", "--file", str(git_credentials)])


def merge_config(
    engine,
    logger,
    github_api_key:str | None = None,
    facade_repo_directory:str | None = None,
    gitlab_api_key:str | None = None,
    redis_conn_string:str | None = None,
    rabbitmq_conn_string:str | None = None,
    logs_directory:str | None = None
    ):
    """Merge config items provided via environment variables into a place where SystemConfig can pick them up.

    Args:
        engine: the database engine to connect to
        logger: object to use for outputting logging messages
        github_api_key (str): config value
        facade_repo_directory (str): config value
        gitlab_api_key (str): config value
        redis_conn_string (str): config value
        rabbitmq_conn_string (str): config value
        logs_directory (str): config value
    """

    github_api_key = github_api_key or SystemEnv.get("COLLECTOSS_GITHUB_API_KEY")
    facade_repo_directory = github_api_key or SystemEnv.get("COLLECTOSS_FACADE_REPO_DIRECTORY")
    gitlab_api_key = github_api_key or SystemEnv.get("COLLECTOSS_GITLAB_API_KEY")
    redis_conn_string = github_api_key or SystemEnv.get("REDIS_CONN_STRING")
    rabbitmq_conn_string = github_api_key or SystemEnv.get("RABBITMQ_CONN_STRING")
    logs_directory = github_api_key or SystemEnv.get("COLLECTOSS_LOGS_DIRECTORY")

    keys = {}

    keys["github_api_key"] = github_api_key
    keys["gitlab_api_key"] = gitlab_api_key

    with DatabaseSession(logger, engine=engine) as session:

        config = SystemConfig(logger, session)

        augmented_config = config.base_config

        phase_names = get_phase_names_without_import()

        #Add all phases as enabled by default
        for name in phase_names:

            if name not in augmented_config['Task_Routine']:
                augmented_config['Task_Routine'].update({name : 1})

        #print(default_config)
        if redis_conn_string:

            try:
                redis_string_array = redis_conn_string.split("/")
                cache_number = int(redis_string_array[-1])
                digits = len(str(cache_number))

                redis_conn_string = redis_conn_string[:-digits]
            
            except ValueError:
                pass

            augmented_config["Redis"]["connection_string"] = redis_conn_string

        if rabbitmq_conn_string:
            augmented_config["RabbitMQ"]["connection_string"] = rabbitmq_conn_string

        augmented_config["Keys"] = keys

        augmented_config["Facade"]["repo_directory"] = facade_repo_directory

        augmented_config["Logging"]["logs_directory"] = logs_directory or (ROOT_PROJECT_REPO_DIRECTORY + "/logs/")

        config.load_config_from_dict(augmented_config)
