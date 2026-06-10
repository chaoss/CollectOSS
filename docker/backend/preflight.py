from collectoss.util.startup import collect_env_variables, check_init_schema, check_update_schema, setup_facade_directory, merge_config, warn_import_repos, print_platform_information
from collectoss.application.logs import getFormatter
from collectoss.application.cli import DatabaseContext
import sys
import logging

if __name__ == "__main__":
    # We cannot use systemLogger here because it depends on the database
    # At this point in execution, the database may not yet be initialized or
    # usable for configuration. So for now we DIY it as a temporary measure
    # until we can more comprehensively improve the high level configuration system
    logger = logging.getLogger("collectoss.preflight")
    log_level = logging.INFO
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        handler.setFormatter(getFormatter(log_level))
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.propagate = False

    collect_env_variables(logger)

    check_init_schema()
    check_update_schema()

    setup_facade_directory(logger)

    merge_config(DatabaseContext().engine, logger)

    warn_import_repos(logger)

    print_platform_information(logger)

    sys.exit(0)
