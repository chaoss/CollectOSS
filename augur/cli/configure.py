#SPDX-License-Identifier: MIT
"""
Augur library script for generating a config file
"""

import os
import click
import json

ENVVAR_PREFIX = "AUGUR_"

@click.group('configure', short_help='Generate an augur.config.json')
def cli():
    pass

@cli.command('generate', short_help='Generate an augur.config.json')
@click.option('--db_name', help="Database name for your data collection database", envvar=ENVVAR_PREFIX + 'DB_NAME')
@click.option('--db_host', help="Host for your data collection database", envvar=ENVVAR_PREFIX + 'DB_HOST')
@click.option('--db_user', help="User for your data collection database", envvar=ENVVAR_PREFIX + 'DB_USER')
@click.option('--db_port', help="Port for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PORT')
@click.option('--db_password', help="Password for your data collection database", envvar=ENVVAR_PREFIX + 'DB_PASSWORD')
@click.option('--github_api_key', help="GitHub API key for data collection from the GitHub API", envvar=ENVVAR_PREFIX + 'GITHUB_API_KEY')
@click.option('--facade_repo_directory', help="Directory on the database server where Facade should clone repos", envvar=ENVVAR_PREFIX + 'FACADE_REPO_DIRECTORY')
def generate(db_name, db_host, db_user, db_port, db_password, github_api_key, facade_repo_directory):

    config = {
        "Cache": {
            "config": {
                "cache.data_dir": "runtime/cache/",
                "cache.lock_dir": "runtime/cache/",
                "cache.type": "file"
            }
        },
        "Database": {
            "connection_string": "sqlite:///:memory:",
            "database": "augur",
            "host": "localhost",
            "key": "key",
            "password": "augur",
            "port": 5432,
            "schema": "augur_data",
            "user": "augur"
        },
        "Development": {
            "developer": "0",
            "interactive": "0"
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
                        "github_url"
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
                }
            ]
        },
        "Plugins": [],
        "Server": {
            "cache_expire": "3600",
            "host": "0.0.0.0",
            "port": "5000",
            "workers": "4"
        },
        "Frontend": {
            "host": "0.0.0.0",
            "port": "5000"
        },
        "Workers": {
            "facade_worker": {
                "port": 56111,
                "repo_directory": "repos/",
                "switch": 0,
                "workers": 1
            },
            "github_worker": {
                "port": 56211,
                "switch": 0,
                "workers": 2
            },
            "insight_worker": {
                "port": 56311,
                "switch": 0,
                "workers": 2
            },
            "linux_badge_worker": {
                "port": 56811,
                "switch": 0,
                "workers": 1
            },
            "metric_status_worker": {
                "port": 56711,
                "switch": 0,
                "workers": 1
            },
            "pull_request_worker": {
                "port": 56411,
                "switch": 0,
                "workers": 2
            },
            "repo_info_worker": {
                "port": 56511,
                "switch": 0,
                "workers": 2
            },
            "value_worker": {
                "port": 56611,
                "scc_bin": "scc",
                "switch": 0,
                "workers": 1
            }
        }
    }

    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    try:
        with open('../default.config.json') as default_config:
            config = json.load(default_config)
    except Exception as e:
        print("Error reading default.config.json " + str(e))

    if db_name is not None:
        config['Database']['database'] = db_name
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

    config['Database']['schema'] = "augur_data"

    try:
        with open('../../augur.config.json', 'w') as f:
            json.dump(config, f, indent=4)
            print('augur.config.json successfully created')
    except Exception as e:
        print("Error writing augur.config.json " + str(e))

