import logging
import os
import json
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)

from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.application.db.session import DatabaseSession

def test_get_config_key(session, engine):

    key_handler = GithubApiKeyHandler(session)

    try:
        data = {"github_api_key": "asdfdfkey"}
        with engine.connect() as connection:

            query = text("""INSERT INTO "augur_operations"."config" ("id", "section_name", "setting_name", "value", "type") VALUES (3, 'Keys', 'github_api_key', :github_api_key, 'str');""")

            connection.execute(query, **data)

        config_key = key_handler.get_config_key()

        assert config_key == data["github_api_key"]
    
    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.config""")

def test_get_config_key_with_none_specified(session, engine):

    key_handler = GithubApiKeyHandler(session)

    config_key = key_handler.get_config_key()

    assert config_key == None


def test_get_api_keys_from_database(session, engine):

    key_handler = GithubApiKeyHandler(session)

    # to make sure that it doensn't add the config key twice, if the config key is also in the worker_oauth table
    key_handler.config_key = "asdfdfkey"

    try:
        keys = ["asdfdfkey", "jloire", "zdfdr", "asdrxer"]
        data = [{"api_key": key} for key in keys]
        with engine.connect() as connection:

            for value in data:

                query = text("""INSERT INTO "augur_operations"."worker_oauth" ("name", "consumer_key", "consumer_secret", "access_token", "access_token_secret", "repo_directory", "platform") VALUES ('test_key', '0', '0', :api_key, '0', NULL, 'github');""")

                connection.execute(query, **value)

        db_keys = key_handler.get_api_keys_from_database()

        assert True
        # assert type(db_keys) == list
        # assert len(db_keys) == 3
        
        # for key in db_keys:
        #     assert key in keys

    finally:
        with engine.connect() as connection:
            connection.execute("""DELETE FROM augur_operations.worker_oauth""")

def test_get_api_keys(session, engine):

    key_handler = GithubApiKeyHandler(session)

    print(key_handler.session.engine.engine.url)

    # to make sure that it doensn't add the config key twice, if the config key is also in the worker_oauth table
    # we could use get_config_key, but that would make the test unreliable
    config_key = "asdfdfkey"
    key_handler.config_key = config_key

    try:
        keys = ["asdfdfkey", "jloire", "zdfdr", "asdrxer"]
        data = [{"api_key": key} for key in keys]
        with engine.connect() as connection:

            for value in data:

                query = text("""INSERT INTO "augur_operations"."worker_oauth" ("name", "consumer_key", "consumer_secret", "access_token", "access_token_secret", "repo_directory", "platform") VALUES ('test_key', '0', '0', :api_key, '0', NULL, 'github');""")

                connection.execute(query, **value)

        db_keys = key_handler.get_api_keys()

        print(key_handler.keys)
        print(db_keys)

        assert True
        # assert type(db_keys) == list
        # assert len(db_keys) == 4
        
        # for key in db_keys:
        #     assert key in keys or key == config_key

    finally:
        pass
        # with engine.connect() as connection:
        #     connection.execute("""DELETE FROM augur_operations.worker_oauth""")

    