import json
import os
import sys

def configure_cache(config):
    print("==Setting up Cache configuration==")
    config['Cache'] = {'config': {}}
    config['Cache']['config']['cache.data_dir'] = "runtime/cache/"
    config['Cache']['config']['cache.lock_dir'] = "runtime/cache/"
    config['Cache']['config']['cache.type'] = "file"

def configure_database(config, credentials=None):
    print("==Setting up Augur Database==")
    config['Database'] = {}
    if credentials:
        print("Using values stored in temp.config.json to set database config")
        config['Database']['database'] = credentials['database'] or "augur"
        config['Database']['host'] = credentials['host'] or "localhost"
        config['Database']['port'] = credentials['port'] or "5432"
        config['Database']['user'] = credentials['user'] or "augur"
        config['Database']['password'] = credentials['password'] or "YOUR PASSWORD"
        config['Database']['schema'] = "augur_data"
        config['Database']['key'] = credentials['key'] or "YOUR KEY"
        config['Database']['zombie_id'] = credentials['zombie_id'] or "22"

        github_api_key = input("Please enter your GitHub API key: ")
        config['GitHub'] = {'apikey': github_api_key}
    else:
        db_name = input("Enter Database Name [Default: augur]: ") or "augur"
        config['Database']['database'] = db_name
        config['Database']['name'] = db_name
        db_host = input("Enter Database Host [Default: localhost]: ") or "localhost"
        config['Database']['host'] = db_host
        db_port = input("Enter Database Port [Default: 5432]: ") or "5432"
        config['Database']['port'] = db_port
        db_user = input("Enter Database User [Default: augur]: ") or "augur"
        config['Database']['user'] = db_user
        db_password = input("Enter Database Password: ") or "YOUR PASSWORD"
        config['Database']['password'] = db_password
        db_schema = input("Enter Database Schema [Default: augur_data]: ") or "augur_data"
        config['Database']['schema'] = db_schema
        db_key = input("Enter GitHub API key/token: ") or "YOUR KEY"
        config['Database']['key'] = db_key
        config['GitHub'] = {'apikey': db_key}
        db_zombie = input("Enter Zombie ID [Default: 22]:") or "22"
        config['Database']['zombie_id'] = db_zombie

    print()

def configure_server(config):
    print("==Setting up Augur Server==")
    config['Server'] = {}
    config['Server']['host'] = "0.0.0.0"
    config['Server']['port'] = "5000"
    config['Server']['workers'] = "4"
    config['Server']['cache_expire'] = "3600"

def configure_facade(config):
    print("==Setting up Facade==")
    config['Facade'] = {}
    f_host = input("Enter Facade DB Host [Default: localhost]: ") or "localhost"
    config['Facade']['host'] = f_host
    f_port = input("Enter Facade DB Port [Default: 3306]: ") or "3306"
    config['Facade']['port'] = f_port
    f_name = input("Enter Facade DB Name [Default: facade]: ") or "facade"
    config['Facade']['name'] = f_name
    f_user = input("Enter Facade DB Username [Default: augur]: ") or "augur"
    config['Facade']['user'] = f_user
    f_pass = input("Enter Facade DB Password: ") or "password"
    config['Facade']['pass'] = f_pass
    f_proj = input("Enter Facade Projects: ")
    config['Facade']['projects'] = f_proj.split()
    print()

def configure_ghtorrent(config):
    print("==Setting up GHTorrent==")
    config['GHTorrent'] = {}
    gh_host = input("Enter GHTorrent Host [Default: localhost]: ") or "localhost"
    config['GHTorrent']['host'] = gh_host
    gh_port = input("Enter GHTorrent Port [Default: 3306]: ") or "3306"
    config['GHTorrent']['port'] = gh_port
    gh_name = input("Enter GHTorrent Name [Default: ghtorrent]: ") or "ghtorrent"
    config['GHTorrent']['name'] = gh_name
    gh_user = input("Enter GHTorrent Username [Default: augur]: ") or "augur"
    config['GHTorrent']['user'] = gh_user
    gh_pass = input("Enter GHTorrent Password: ") or "password"
    config['GHTorrent']['pass'] = gh_pass
    print()

def configure_defaults(config):
    print("==Setting up defaults==")

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

    if not 'GHTorrent' in config:
        config['GHTorrent'] = {
            "host": "localhost",
            "name": "ghtorrent",
            "pass": "password",
            "port": "3306",
            "user": "augur"
        }
        print("Set default values for GHTorrent...")

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
                    "given": ["git_url"],
                    "model": "issues",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": ["git_url"],
                    "model": "repo_info",
                    "repo_group_id": 0
                },
                {
                    "delay": 150000,
                    "given": ["git_url"],
                    "model": "pull_requests",
                    "repo_group_id": 0
                }
            ]
        }
        print("Set default values for Housekeeper...")

    msg = "Enter directory where all repositories are stored [Default: $HOME/augur-repos]: "
    repo_dir = input(msg) or f"{os.environ['HOME']}/augur-repos"

    try:
        if not os.path.exists(repo_dir):
            print(f"{repo_dir} does not exist. Creating...")
            os.makedirs(repo_dir)
    except FileExistsError:
        pass
    except Exception as e:
        print("An unexpected error occured: ", e)
        print("Continuing...")

    if not "Workers" in config:
        config["Workers"] = {
            "facade_worker": {
                "port": 51246,
                "switch": 0,
                "workers": 1,
                "repo_directory": repo_dir
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
    if os.path.isfile("augur.config.json"):
        print("augur.config.json already exists!")
        inp = input("Do you want to rewrite it? (Y/N): ")
        if inp.lower() != 'y':
            print('Exiting...')
            return

    print("Beginning 'augur.config.json' creation process...\n")
    config = {}

    configure_cache(config)
    try:
        with open('temp.config.json', 'r') as db_credentials_file:
            configure_database(config, json.load(db_credentials_file))
    except FileNotFoundError:
        configure_database(config)
    configure_server(config)

    # inp = input("Would you like to setup GHTorrent? (Y/N): ")
    # if inp.lower() == 'y':
    #     configure_ghtorrent(config)
    # else:
    #     print("Skipping GHTorrent configuration...")

    # inp = input("Would you like to setup Facade? (Y/N): ")
    # if inp.lower() == 'y':
    #     configure_facade(config)
    # else:
    #     print("Skipping Facade configuration...")

    configure_defaults(config)

    try:
        with open('augur.config.json', 'w') as f:
            f.write(json.dumps(config, indent=4))
            print('augur.config.json successfully created')
    except Exception as e:
        print("Error writing augur.config.json " + str(e))


if __name__ == "__main__":
    main()