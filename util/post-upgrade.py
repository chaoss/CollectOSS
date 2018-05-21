import configparser as configparser
import os
import sys
import json
from distutils.version import LooseVersion, StrictVersion

import augur

oldVersion = sys.argv[1]

upgrades = []

print('Post-install (context: {}, target: {})'.format(oldVersion, augur.__version__))


# Switch from old config to new
def migrate_config_to_json():
    config_file_path = os.path.abspath(os.getenv('AUGUR_CONFIG_FILE', 'augur.cfg'))
    output_file_path = os.path.join(os.path.dirname(config_file_path), 'augur.config.json')
    with open(config_file_path, 'r') as config_file:

        print('  - convert {} to {}'.format(config_file_path, output_file_path))

        conf = configparser.RawConfigParser()
        conf.read_file(config_file)

        json_object = {
            "Plugins": [

            ],
            "Git": {
                "repositories": [],
                "storage": "runtime/git_repos/"
            }
        }

        for section in conf.sections():
            json_object[section] = {}
            for key, val in conf.items(section):
                if val != 'None':
                    json_object[section][key] = val
                else:
                    json_object[section][key] = ''

        with open(output_file_path, 'w+') as output_file:
            output_file.write(json.dumps(json_object, sort_keys=True, indent=4))
migrate_config_to_json.ver = '0.5.0'
upgrades.append(migrate_config_to_json)



for upgrade in upgrades:
    try:
        if (upgrade.__name__ in sys.argv
                or LooseVersion(oldVersion) < LooseVersion(upgrade.ver)):
            print('{} (introduced {})'.format(upgrade.__name__, upgrade.ver))
            upgrade()
    except Exception as error:
        print(error)
