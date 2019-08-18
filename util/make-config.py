import json
import os
import sys


def configure_cache(config):
    print("==Setting up Cache configuration==")
    config['Cache'] = {'config': {}}
    c_data_dir = input("Enter Cache Data Directory [Default: runtime/cache/]: ") or "runtime/cache/"
    config['Cache']['config']['cache.data_dir'] = c_data_dir
    c_lock_dir = input("Enter Cache Lock Directory [Default: runtime/cache/]: ") or "runtime/cache/"
    config['Cache']['config']['cache.lock_dir'] = c_lock_dir
    c_type = input("Enter Cache Type [Default: file]: ") or "file"
    config['Cache']['config']['cache.type'] = c_type
    print()

def configure_database(config):
    print("==Setting up Augur Database==")
    config['Database'] = {}
    config['Database']['connection_string'] = "sqlite:///:memory:"
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
    s_host = input("Enter Server Host [Default: 0.0.0.0]: ") or "0.0.0.0"
    config['Server']['host'] = s_host
    s_port = input("Enter Server Host [Default: 5000]: ") or "5000"
    config['Server']['port'] = s_port
    s_workers = input("Enter Number of Workers [Default: 4]: ") or "4"
    config['Server']['workers'] = s_workers
    s_cache = input("Enter Cache Expiry Duration [Default: 3600]: ") or "3600"
    config['Server']['cache_expire'] = s_cache
    print()

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

def configure_ghtorrent_plus(config):
    print("==Setting up GHTorrent Plus==")
    config['GHTorrentPlus'] = {}
    gh_host = input("Enter GHTorrentPlus Host [Default: localhost]: ") or "localhost"
    config['GHTorrentPlus']['host'] = gh_host
    gh_port = input("Enter GHTorrentPlus Port [Default: 3306]: ") or "3306"
    config['GHTorrentPlus']['port'] = gh_port
    gh_name = input("Enter GHTorrentPlus Name [Default: ghtorrentplus]: ") or "ghtorrentplus"
    config['GHTorrentPlus']['name'] = gh_name
    gh_user = input("Enter GHTorrentPlus Username [Default: augur]: ") or "augur"
    config['GHTorrentPlus']['user'] = gh_user
    gh_pass = input("Enter GHTorrentPlus Password: ") or "password"
    config['GHTorrentPlus']['pass'] = gh_pass
    print()

def configure_defaults(config):
    print("\n==Setting up defaults==")

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
    configure_database(config)
    configure_server(config)

    inp = input("Would you like to setup GHTorrent? (Y/N): ")
    if inp.lower() == 'y':
        configure_ghtorrent(config)
    else:
        print("Skipping GHTorrent configuration...")

    inp = input("Would you like to setup GHTorrentPlus? (Y/N): ")
    if inp.lower() == 'y':
        configure_ghtorrent_plus(config)
    else:
        print("Skipping GHTorrent Plus configuration...")

    inp = input("Would you like to setup Facade? (Y/N): ")
    if inp.lower() == 'y':
        configure_facade(config)
    else:
        print("Skipping Facade configuration...")

    configure_defaults(config)

    try:
        with open('augur.config.json', 'w') as f:
            f.write(json.dumps(config, indent=4))
            print('augur.config.json successfully created')
    except Exception as e:
        print("Error writing augur.config.json " + str(e))


if __name__ == "__main__":
    main()