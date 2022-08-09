from augur.application.config import AugurConfig
import logging
import os
import json
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

def test_config_get_value(config, engine):

    try:

        data = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}


        with engine.connect() as connection:

            query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

            connection.execute(query, **data)


        result = config.get_value(data["section_name"], data["setting_name"],)

        assert result == "ipv4"

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_get_section(config, engine):

    try:
        section_name = "Network"
        ip_standard = {"section_name": section_name, "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": section_name, "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": section_name, "setting_name": "subnet_mask", "value": "/24"}

        network_data = [ip_standard, ip, subnet_mask]


        with engine.connect() as connection:

            for data in network_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)


        result = config.get_section(section_name)

        assert result is not None

        for data in network_data:

            setting_name = data["setting_name"]
            setting_value = data["value"]

            assert setting_value == result[setting_name]


    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")


def test_config_load_config(config, engine):

    try:
        
        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        cpu_speed = {"section_name": "Computer", "setting_name": "cpu_speed", "value": "3GHZ"}
        cores = {"section_name": "Computer", "setting_name": "cores", "value": "8"}
        screen_size = {"section_name": "Computer", "setting_name": "screen_size", "value": "16in"}

        all_data = [ip_standard, ip, subnet_mask, cpu_speed, cores, screen_size]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)


        result = config.load_config()

        assert result is not None

        for data in all_data:

            section_name = data["section_name"]
            setting_name = data["setting_name"]
            setting_value = data["value"]

            assert setting_value == result[section_name][setting_name]


    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_empty(config, engine):

    try:

        assert config.empty() == True
        
        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        cpu_speed = {"section_name": "Computer", "setting_name": "cpu_speed", "value": "3GHZ"}
        cores = {"section_name": "Computer", "setting_name": "cores", "value": "8"}
        screen_size = {"section_name": "Computer", "setting_name": "screen_size", "value": "16in"}

        all_data = [ip_standard, ip, subnet_mask, cpu_speed, cores, screen_size]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)


        assert config.empty() == False

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_is_section_in_config(config, engine):

    try:

        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        cpu_speed = {"section_name": "Computer", "setting_name": "cpu_speed", "value": "3GHZ"}
        cores = {"section_name": "Computer", "setting_name": "cores", "value": "8"}
        screen_size = {"section_name": "Computer", "setting_name": "screen_size", "value": "16in"}

        all_data = [ip_standard, ip, subnet_mask, cpu_speed, cores, screen_size]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)

        for data in all_data:
            assert config.is_section_in_config(data["section_name"]) == True

        assert config.is_section_in_config("Server") == False
        assert config.is_section_in_config("Logging") == False

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_add_settings(config, engine):

    try:
        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        settings = [ip_standard, subnet_mask]

        config.add_or_update_settings(settings)

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            assert result is not None
            assert len(result) == 2

            for row in result:

                dict_data = dict(row)

                del dict_data["id"]

                assert dict_data in settings

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_update_settings(config, engine):

    try:
        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}

        ip_standard_updated = ip_standard.copy()
        ip_updated = ip.copy()
        subnet_mask_updated = subnet_mask.copy()

        new_ip_standard = "ipv6"
        new_ip = "1.1.1.1"
        new_subnet_mask = "/16"

        ip_standard_updated["value"] = new_ip_standard
        ip_updated["value"] = new_ip
        subnet_mask_updated["value"] = new_subnet_mask

        all_data = [ip_standard, ip, subnet_mask]
        updated_settings = [ip_standard_updated, ip_updated, subnet_mask_updated]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)

        config.add_or_update_settings(updated_settings)

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            assert len(result) == 3

            for row in result:
                dict_data = dict(row)

                del dict_data['id']

                assert dict_data in updated_settings

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")


def test_config_add_section_from_json(config, engine):

    try:
        section_name = "Network"
        network_section = {
                "ip_standard": "ipv4",
                "ip": "8.8.8.8",
                "subnet_mask": "/24"
        }

        config.add_section_from_json(section_name, network_section)

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""")

            for row in result:
                dict_data = dict(row)
                
                assert section_name == dict_data["section_name"]

                setting_name = dict_data["setting_name"]
                value = dict_data["value"]

                assert network_section[setting_name] == value

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")


def test_load_config_file(config):

    try:

        file_path = "temp.json"
        config_dict = {
            "Network": {
                "ip_standard": "ipv4",
                "ip": "8.8.8.8",
                "subnet_mask": "/24"
            }     
        }

        with open(file_path, 'w') as outfile:
            json.dump(config_dict, outfile)

        result = config.load_config_file(file_path)

        assert result == config_dict

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def test_config_load_config_from_dict(config, engine):

    try:
        config_dict = {
            "Network": {
                "ip_standard": "ipv4",
                "ip": "8.8.8.8",
                "subnet_mask": "/24"
            },
            "Computer": {
                "cores": "8",
                "cpu_speed": "3Ghz"
            }     
        }

        config.load_config_from_dict(config_dict)

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            for row in result:
                dict_data = dict(row)

                section_name = dict_data["section_name"]
                
                assert section_name in config_dict.keys() 

                setting_name = dict_data["setting_name"]
                value = dict_data["value"]

                assert config_dict[section_name][setting_name] == value

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_config_clear(config, engine):

    try:
        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        all_data = [ip_standard, ip, subnet_mask]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)

        config.clear()

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            assert len(result) == 0


    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_remove_section(config, engine):

    try:
        section_removed = "Network"

        ip_standard = {"section_name": "Network", "setting_name": "ip_standard", "value": "ipv4"}
        ip = {"section_name": "Network", "setting_name": "ip", "value": "8.8.8.8"}
        subnet_mask = {"section_name": "Network", "setting_name": "subnet_mask", "value": "/24"}
        cpu_speed = {"section_name": "Computer", "setting_name": "cpu_speed", "value": "3GHZ"}
        cores = {"section_name": "Computer", "setting_name": "cores", "value": "8"}
        screen_size = {"section_name": "Computer", "setting_name": "screen_size", "value": "16in"}

        all_data = [ip_standard, ip, subnet_mask, cpu_speed, cores, screen_size]

        with engine.connect() as connection:

            for data in all_data:

                query = text("""INSERT INTO "augur_operations"."config" ("section_name", "setting_name", "value", "type") VALUES (:section_name, :setting_name, :value, 'str');""")

                connection.execute(query, **data)

        config.remove_section(section_removed)

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            for row in result:
                dict_data = dict(row)

                assert dict_data["section_name"] != section_removed


    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")



def test_create_default_config(config, engine):

    from augur.application.config import default_config

    config.create_default_config()

    try:

        with engine.connect() as connection:

            result = connection.execute("""SELECT * FROM augur_operations.config""").fetchall()

            for row in result:
                dict_data = dict(row)

                assert dict_data["section_name"] != section_removed


    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")





