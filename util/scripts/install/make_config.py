import json
import os
import sys

def configure_database(config, credentials):
    print("==Setting up Augur Database==")
    config['Database'] = {}
    config['Database']['database'] = credentials['database']
    config['Database']['host'] = credentials['host']
    config['Database']['port'] = credentials['port']
    config['Database']['user'] = credentials['user']
    config['Database']['password'] = credentials['password']
    config['Database']['schema'] = "augur_data"
    config['Database']['key'] = credentials['github_api_key']

    config['GitHub'] = {'apikey': credentials['github_api_key']}

def configure_defaults(config):
    print("==Setting up defaults==")

    if not 'Cache' in config:
        config['Cache'] = {}
        config['Cache']['config'] = {
            "cache.data_dir": "runtime/cache/",
            "cache.lock_dir": "runtime/cache/",
            "cache.type": "file"
        }

    if not 'Server' in config:
        config['Server'] = {
            "host": "0.0.0.0",
            "port": "5000",
            "workers": "4",
            "cache_expire": "3600"
        }

    if not 'Facade' in config:
        config["Facade"] = {
            "check_updates": 1,
            "clone_repos": 1,
            "create_xlsx_summary_files": 1,
            "delete_marked_repos": 0,
            "fix_affiliations": 1,
            "force_analysis": 1,
            "force_invalidate_caches": 0,
            "force_updates": 1,
            "limited_run": 0,
            "multithreaded": 0,
            "nuke_stored_affiliations": 0,
            "pull_repos": 1,
            "rebuild_caches": 1,
            "run_analysis": 1
        }
        print("Set default values for Facade...")

    if not 'Development' in config:
        config["Development"] = {
            "developer": "0",
            "interactive": "0"
        }
        print("Set default values for Developement...")

    if not 'Plugins' in config:
        config['Plugins'] = []
        print("Set default values for Plugins...")

    if not 'Housekeeper' in config:
        config['Housekeeper'] = {
            "jobs": [
                {
                    "delay": 150000,
                    "given": ["github_url"],
                    "model": "issues",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": ["github_url"],
                    "model": "repo_info",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": ["github_url"],
                    "model": "pull_requests",
                    "repo_group_id": 0
                }
            ]
        }
        print("Set default values for Housekeeper...")

    if not 'Workers' in config:
        config['Workers'] = {
            "facade_worker": {
                "port": 51246,
                "switch": 0,
                "workers": 1,
                "repo_directory": "$HOME/augur_repos"
            },
            "pull_request_worker": {
                "port": 51252,
                "switch": 0,
                "workers": 1
            },
            "github_worker": {
                "port": 51238,
                "switch": 0,
                "workers": 1
            },
            "insight_worker": {
                "port": 51244,
                "switch": 0,
                "workers": 1
            },
            "repo_info_worker": {
                "port": 51242,
                "switch": 0,
                "workers": 1
            }
        }
        print("Set default values for Workers")

    print()

def main():
    print("Beginning 'augur.config.json' creation process...\n")
    config = {}

    with open('temp.config.json', 'r') as db_credentials_file:
        configure_database(config, json.load(db_credentials_file))

    configure_defaults(config)

    try:
        with open('../../../augur.config.json', 'w') as f:
            f.write(json.dumps(config, indent=4))
            print(config)
            print('augur.config.json successfully created')
    except Exception as e:
        print("Error writing augur.config.json " + str(e))


if __name__ == "__main__":
    main()