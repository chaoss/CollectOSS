import json
import os
import sys

def main():
    print("Beginning 'augur.config.json' creation process...\n")

    # with open('temp.config.json', 'r') as db_credentials_file:
    #     credentials = json.load(db_credentials_file)
    #     configure_database(config, credentials)

    config = {
            "Database": {},
            "Cache": {
                "config": {
                    "cache.data_dir": "runtime/cache/",
                    "cache.lock_dir": "runtime/cache/",
                    "cache.type": "file"
                }
            },
            "Development": {
                "developer": "0",
                "interactive": "0"
            },
            "Plugins": [],
            "Server": {
                "cache_expire": "3600",
                "host": "127.0.0.1",
                "port": "5000",
                "workers": "4"
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
            "Workers": {
                "facade_worker": {
                    "port": 56111,
                    "repo_directory": "/home/repos/",
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

    config['Database']['database'] = sys.argv[1]
    config['Database']['host'] = sys.argv[2]
    config['Database']['port'] = sys.argv[3]
    config['Database']['user'] = sys.argv[4]
    config['Database']['password'] = sys.argv[5]
    config['Database']['schema'] = "augur_data"

    config['Database']['key'] = sys.argv[6]

    config['Workers']['facade_worker']['repo_directory'] = sys.argv[7]

    print(config)

    # try:
    #     with open('../../../augur.config.json', 'w') as f:
    #         f.write(json.dumps(config, indent=4))
    #         print('augur.config.json successfully created')
    # except Exception as e:
    #     print("Error writing augur.config.json " + str(e))

if __name__ == "__main__":
    main()
