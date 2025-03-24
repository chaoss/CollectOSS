# SPDX-License-Identifier: MIT
"""
Creates routes for config functionality
"""
import logging
import httpx

import sqlalchemy as s
from flask import current_app, jsonify, request

# Disable the requirement for SSL by setting env["AUGUR_DEV"] = True
from augur.api.util import admin_required, ssl_required
from augur.application.config import AugurConfig
from augur.application.db.lib import (
    get_session,
    remove_setting,
    remove_worker_oauth_key,
)
from augur.application.db.models.augur_operations import WorkerOauth
from augur.application.db.models import Config
from augur.application.db.session import DatabaseSession
from keyman.KeyClient import KeyPublisher
from augur.tasks.github.util.github_api_key_handler import GithubApiKeyHandler
from augur.tasks.gitlab.gitlab_api_key_handler import GitlabApiKeyHandler
from ..server import app

logger = logging.getLogger(__name__)

from augur.api.routes import AUGUR_API_VERSION

@app.route(f"/{AUGUR_API_VERSION}/config/get", methods=["GET", "POST"])
@ssl_required
def get_config():
    with DatabaseSession(logger, engine=current_app.engine) as session:
        config_dict = AugurConfig(logger, session).config.load_config()

    return jsonify(config_dict), 200


@app.route(f"/{AUGUR_API_VERSION}/config/set", methods=["GET", "POST"])
@ssl_required
@admin_required
def set_config_item():
    setting = request.args.get("setting")
    section = request.args.get("section")
    value = request.values.get("value")
    
    result = {
        "section_name": section,
        "setting_name": setting,
        "value": value
    }
    
    if not setting or not section or not value:
        return jsonify({"status": "Missing argument"}), 400

    with get_session() as session:
        config = AugurConfig(logger, session)
        config.add_or_update_settings([result])

    return jsonify({"status": "success"})


@app.route(f"/{AUGUR_API_VERSION}/config/update", methods=["POST"])
@ssl_required
def update_config():
    update_dict = request.get_json()

    with get_session() as session:
        for section, data in update_dict.items():
            for key, value in data.items():
                try:
                    config_setting = (
                        session.query(Config)
                        .filter(
                            Config.section_name == section, Config.setting_name == key
                        )
                        .one()
                    )
                except s.orm.exc.NoResultFound:
                    return jsonify(
                        {"status": "Bad Request", "section": section, "setting": key}
                    ), 400

                config_setting.value = value

                session.add(config_setting)

        session.commit()

    return jsonify({"status": "success"}), 200


@app.route(f"/{AUGUR_API_VERSION}/workeroauth/get/keys", methods=['GET'])
@ssl_required
@admin_required
def get_oauth_keys():
    """
    Retrieve all worker oauth keys from the configuration table in the database.
    The keys from the "Keys" section are normalized and returned such that they follow the format:
      {
         "github_api_key": "ghp_XXXXXXXXXXXXXXX",
         "gitlab_api_key": "glpat_XXXXXXXXXXXXXXX"
      }
    """
    # Open a database session using the current application engine
    with DatabaseSession(logger, engine=current_app.engine) as session:
        config = AugurConfig(logger, session)
        # Get the Keys section if it exists; otherwise, key list remains empty.
        if config.is_section_in_config("Keys"):
            keys_section = config.get_section("Keys")
        else:
            keys_section = {}

    # Normalize the key names (append '_api_key' if needed)
    keys_dict = {}
    for platform, key_value in keys_section.items():
        platform_lower = platform.lower()
        if "github" in platform_lower:
            platform_lower = "github"
        elif "gitlab" in platform_lower:
            platform_lower = "gitlab"
        keys_dict[f"{platform_lower}_api_key"] = key_value

    return jsonify(keys_dict), 200


@app.route(f"/{AUGUR_API_VERSION}/workeroauth/get/invalidkeys", methods=["GET"])
@ssl_required
@admin_required
def get_invalid_keys():
    """
    Retrieve all invalid worker OAuth keys by comparing the keys loaded 
    in the KeyPublisher at startup with those stored in the database, 
    and by checking the live keys with the is_bad_api_key function.
    
    A key is considered valid if it appears in the set of live keys and passes 
    the is_bad_api_key test; any key that fails is considered invalid.
    """
    keypub = KeyPublisher()

    invalid_keys = {}
    live_keys = {}
    for platform in keypub.list_platforms():
        platform_lower = platform.lower()
        tokens = keypub.list_keys(platform)
        if tokens is not None:
            live_keys[platform_lower] = set(tokens)

    # Instantiate the API key handlers and HTTP client.
    ghkeyman = GithubApiKeyHandler(logger)
    glkeyman = GitlabApiKeyHandler(logger)
    client = httpx.Client()

    github_db_keys = ghkeyman.get_api_keys_from_database()
    # For GitHub, we check keys published under both channels.
    github_live = live_keys.get("github_rest", set()) | live_keys.get("github_graphql", set())
    for token in github_db_keys:
        if token not in github_live or ghkeyman.is_bad_api_key(client, token):
            invalid_keys.setdefault("github", []).append(token)

    gitlab_db_keys = glkeyman.get_api_keys_from_database()
    gitlab_live = live_keys.get("gitlab_rest", set())
    for token in gitlab_db_keys:
        if token not in gitlab_live or glkeyman.is_bad_api_key(client, token):
            invalid_keys.setdefault("gitlab", []).append(token)

    # This ensures that even if a key is live, we verify it using is_bad_api_key.
    for token in live_keys.get("github_rest", set()):
        if ghkeyman.is_bad_api_key(client, token) and token not in invalid_keys.get("github", []):
            invalid_keys.setdefault("github", []).append(token)
    for token in live_keys.get("github_graphql", set()):
        if ghkeyman.is_bad_api_key(client, token) and token not in invalid_keys.get("github", []):
            invalid_keys.setdefault("github", []).append(token)
    for token in live_keys.get("gitlab_rest", set()):
        if glkeyman.is_bad_api_key(client, token) and token not in invalid_keys.get("gitlab", []):
            invalid_keys.setdefault("gitlab", []).append(token)

    for platform, tokens in invalid_keys.items():
        invalid_keys[platform] = [{"id": token, "token": token} for token in tokens]

    return jsonify(invalid_keys), 200



@app.route(f"/{AUGUR_API_VERSION}/workeroauth/delete/key", methods=["POST"])
@ssl_required
@admin_required
def delete_oauth_key():
    """
    Delete a worker oauth key from the KeyPublisher, config table and worker oauth table
    Expects a JSON payload with the platform and token properties.
    """
    data = request.get_json()

    if not data or "platform" not in data or "token" not in data:
        return jsonify(
            {"status": "Bad Request", "message": "Missing platform or token"}
        ), 400

    keypub = KeyPublisher()

    platform = data.get("platform").lower()
    if platform == "github":
        keypub.unpublish(data["token"], "github_rest")
        keypub.unpublish(data["token"], "github_graphql")
    elif platform == "gitlab":
        keypub.unpublish(data["token"], "gitlab_rest")

    remove_worker_oauth_key(platform=data["platform"].lower())
    remove_setting(section_name="Keys", setting_name=data["platform"].lower() + "_api_key")

    return jsonify({"status": "success"}), 200



@app.route(f"/{AUGUR_API_VERSION}/workeroauth/new/keys", methods=["POST"])
@ssl_required
@admin_required
def new_oauth_keys():
    """
    Add new worker oauth keys to the KeyPublisher.
    Expects a JSON payload with the platform and token properties.
    """
    data = request.get_json()

    if not data or "platform" not in data or "token" not in data:
        return jsonify(
            {"status": "Bad Request", "message": "Missing platform or token"}
        ), 400
    
    ghkeyman = GithubApiKeyHandler(logger)
    glkeyman = GitlabApiKeyHandler(logger)

    keypub = KeyPublisher()
    client = httpx.Client()

    if data.get("platform") == "github":
        if ghkeyman.is_bad_api_key(client, data["token"]):
            return jsonify({"status": "Bad Request", "message": "Invalid GitHub API key"}), 400
        keypub.publish(data["token"], "github_rest")
        keypub.publish(data["token"], "github_graphql")

    elif data.get("platform") == "gitlab":
        if glkeyman.is_bad_api_key(client, data["token"]):
            return jsonify({"status": "Bad Request", "message": "Invalid GitLab API key"}), 400
        keypub.publish(data["token"], "gitlab_rest")

    return jsonify({"status": "success"}), 200