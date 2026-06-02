## Startup helpers


from pathlib import Path
from collectoss.application.environment import SystemEnv


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
    # check_call(["alembic", "upgrade", "head"])

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
