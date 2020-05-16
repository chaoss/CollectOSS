#SPDX-License-Identifier: MIT
"""
Augur library script for generating a config file
"""

import os
import click
import json

from augur import logger

ENVVAR_PREFIX = "AUGUR_"

default_config = {
        "Database": {
            "name": "augur",
            "host": "localhost",
            "key": "key",
            "password": "augur",
            "port": 5432,
            "user": "augur"
        },
        "Housekeeper": {
            "jobs": [
                {
                    "all_focused": 1,
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "issues",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_request_commits",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "github_url"
                    ],
                    "model": "repo_info",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": [
                        "repo_group"
                    ],
                    "model": "commits",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "github_url"
                    ],
                    "model": "pull_requests",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "contributors",
                    "repo_group_id": 0
                },                
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "insights",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "badges",
                    "repo_group_id": 0
                },
                {
                    "delay": 1000000,
                    "given": [
                        "git_url"
                    ],
                    "model": "value",
                    "repo_group_id": 0
                },
                {
                "delay": 100000,
                "given": [
                    "github_url"
                ],
                "model": "pull_request_files",
                "repo_group_id": 0
                }
            ]
        },
        "Workers": {
            "facade_worker": {
                "port": 50100,
                "repo_directory": "repos/",
                "switch": 1,
                "workers": 1
            },
            "github_worker": {
                "port": 50200,
                "switch": 1,
                "workers": 1
            },
            "insight_worker": {
                "port": 50300,
                "metrics": {"issues-new": "issues", "code-changes": "commit_count", "code-changes-lines": "added", 
                           "reviews": "pull_requests", "contributors-new": "new_contributors"},
                "contamination": 0.041,
                "switch": 0,
                "workers": 1,
                "training_days": 365,
                "anomaly_days": 2
            },
            "linux_badge_worker": {
                "port": 50400,
                "switch": 1,
                "workers": 1
            },
            "metric_status_worker": {
                "port": 50500,
                "switch": 0,
                "workers": 1
            },
            "pull_request_worker": {
                "port": 50600,
                "switch": 1,
                "workers": 1
            },
            "repo_info_worker": {
                "port": 50700,
                "switch": 1,
                "workers": 1
            },
            "value_worker": {
                "port": 50800,
                "scc_bin": "scc",
                "switch": 0,
                "workers": 1
            },
            "contributor_worker": {
                "port": 50900,
                "switch": 1,
                "workers": 1
            }
        },
        "Facade": {
            "check_updates": 1,
            "clone_repos": 1,
            "create_xlsx_summary_files": 1,
            "delete_marked_repos": 0,
            "fix_affiliations": 1,
            "force_analysis": 1,
            "force_invalidate_caches": 1,
            "force_updates": 1,
            "limited_run": 0,
            "multithreaded": 0,
            "nuke_stored_affiliations": 0,
            "pull_repos": 1,
            "rebuild_caches": 1,
            "run_analysis": 1
        },
        "Server": {
            "cache_expire": "3600",
            "host": "0.0.0.0",
            "port": "5000",
            "workers": 4,
            "timeout": 60
        },
        "Frontend": {
            "host": "0.0.0.0",
            "port": "5000"
        },
        "Development": {
            "log_level": "INFO"
        }
    }

@click.group('configure', short_help='Generate an augur.config.json')
def cli():
    pass

@cli.command('generate')
@click.option('--db_name', help="Database name for your data collection database", envvar=ENVVAR_PREFIX + 'DB_NAME')
@click.option('--db_host', help="Host for your data collection database", envvar=ENVVAR_PREFIX + 'DB_HOST')
@click.option('--db_user', help="User for your data collection database", envvar=ENVVAR_PREFIX + 'DB_USER')
@click.option('--db_port', help="Port for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PORT')
@click.option('--db_password', help="Password for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PASSWORD')
@click.option('--github_api_key', help="GitHub API key for data collection from the GitHub API", envvar=ENVVAR_PREFIX + 'GITHUB_API_KEY')
@click.option('--facade_repo_directory', help="Directory on the database server where Facade should clone repos", envvar=ENVVAR_PREFIX + 'FACADE_REPO_DIRECTORY')
@click.option('--rc-config-file', help="File containing existing config whose values will be used as the defaults", type=click.Path(exists=True))
def generate(db_name, db_host, db_user, db_port, db_password, github_api_key, facade_repo_directory, rc_config_file):
    """
    Generate an augur.config.json
    """

    config = default_config
    rc_config = None

    if rc_config_file != None:
        try:
            with open(os.path.abspath(rc_config_file), 'r') as f:
                rc_config = json.load(f)
                for item in rc_config.items():
                    if item[0] == 'Workers':
                        for index in range(0, len(item[1])):
                            key = list(item[1].keys())[index]
                            secondary_dict = list(item[1].values())[index]

                            for secondary_dict_index in range(0, len(secondary_dict)):
                                secondary_key = list(secondary_dict.keys())[secondary_dict_index]
                                value = list(secondary_dict.values())[secondary_dict_index]

                                config[item[0]][key][secondary_key] = value
                    else:
                        for index, key in enumerate(list(item[1].keys())):
                            config[item[0]][key] = list(item[1].values())[index]

                logger.info('Predefined config successfully loaded')

        except Exception as e:
            logger.error(f"Error opening {rc_config_file}: {str(e)}")

    if db_name is not None:
        config['Database']['database'] = db_name # this is for backwards compatibility
    if db_name is not None:
        config['Database']['name'] = db_name
    if db_host is not None:
        config['Database']['host'] = db_host
    if db_port is not None:
        config['Database']['port'] = int(db_port)
    if db_user is not None:
        config['Database']['user'] = db_user
    if db_password is not None:
        config['Database']['password'] = db_password
    if github_api_key is not None:
        config['Database']['key'] = github_api_key
    if facade_repo_directory is not None:
        config['Workers']['facade_worker']['repo_directory'] = facade_repo_directory

    try:
        with open(os.path.abspath('augur.config.json'), 'w') as f:
            json.dump(config, f, indent=4)
            logger.info('augur.config.json successfully created')
    except Exception as e:
        logger.error("Error writing augur.config.json " + str(e))
