import json
import os
import sys

def configure_cache(config):
    print("==Setting up Cache configuration==")
    config['Cache'] = {'config': {}}
    config['Cache']['config']['cache.data_dir'] = "runtime/cache/"
    config['Cache']['config']['cache.lock_dir'] = "runtime/cache/"
    config['Cache']['config']['cache.type'] = "file"

def configure_database(config, credentials):
    print("==Setting up Augur Database==")
    config['Database'] = {}
    config['Database']['database'] = credentials['database'] or "augur"
    config['Database']['name'] = credentials['name']
    config['Database']['host'] = credentials['host'] or "localhost"
    config['Database']['port'] = credentials['port'] or "5432"
    config['Database']['user'] = credentials['user'] or "augur"
    config['Database']['password'] = credentials['password'] or "YOUR PASSWORD"
    config['Database']['schema'] = credentials['schema'] or "augur_data"
    config['Database']['key'] = credentials['key'] or "YOUR KEY"
    config['Database']['zombie_id'] = credentials['zombie_id'] or "22"

    github_api_key = input("Please enter your GitHub API key: ")
    config['GitHub'] = {'apikey': github_api_key}
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
            "host": "localhost",
            "name": "facade",
            "pass": "password",
            "port": "3306",
            "projects": [],
            "user": "augur"
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

    if not 'GHTorrentPlus' in config:
        config['GHTorrentPlus'] = {
            "host": "localhost",
            "name": "ghtorrentplus",
            "pass": "password",
            "port": "3306",
            "user": "ghdata"
        }
        print("Set default values for GHTorrentPlus...")

    if not 'Controller' in config:
        config["Controller"] = {
            "broker": 1,
            "housekeeper": 1,
            "github_worker": 0
        }
        print("Set default values for Controller...")

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
            "jobs": []
        }
        print("Set default values for Housekeeper...")

    if not 'Workers' in config:
        config['Workers'] = {}
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
    with open('temp.config.json', 'r') as db_credentials_file:
        configure_database(config, json.load(db_credentials_file))
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