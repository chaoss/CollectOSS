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


# @app.route(f"/{AUGUR_API_VERSION}/workeroauth/get/keys", methods=['GET'])
# @ssl_required
# @admin_required
# def get_oauth_keys():
#     """
#     Retrieve all worker oauth keys in a JSON structure where the keys are named
#     following the pattern: <platform>_api_key. For example:
#     {
#        "github_api_key": "ghp_XXXXXXXXXXXXXXX",
#        "gitlab_api_key": "glpat_XXXXXXXXXXXXXXX"
#     }
#     """
#     keypub = KeyPublisher()
#     keys_dict = {}
#     for plat in keypub.list_platforms():
#         keys = keypub.list_keys(plat)
#         logger.info(f"Platform: {plat}")
#         logger.info(f"Keys: {keys}")

#         if not keys:
#             continue

#         # Normalize platform names for the frontend
#         if "github" in plat.lower():
#             if "github_api_key" not in keys_dict:  # use the first encountered GitHub key
#                 keys_dict["github_api_key"] = keys[0]
#         elif "gitlab" in plat.lower():
#             if "gitlab_api_key" not in keys_dict:  # use the first encountered GitLab key
#                 keys_dict["gitlab_api_key"] = keys[0]
#         else:
#             key_name = f"{plat.lower()}_api_key"
#             if key_name not in keys_dict:
#                 keys_dict[key_name] = keys[0]

#     return jsonify(keys_dict), 200

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
    keypub = KeyPublisher()

    print("add block")
    for plat in keypub.list_platforms():
        keys = keypub.list_keys(plat)
        if not keys:
            continue
        
        print(f"Platform: {plat}")
        print(f"Keys: {keys}")
    
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
        # Normalize platform names to lowercase.
        platform_lower = platform.lower()
        if platform_lower.endswith("_api_key"):
            keys_dict[platform_lower] = key_value
        else:
            keys_dict[f"{platform_lower}_api_key"] = key_value

    return jsonify(keys_dict), 200


@app.route(f"/{AUGUR_API_VERSION}/workeroauth/get/invalidkeys", methods=["GET"])
@ssl_required
@admin_required
def get_invalid_keys():
    """
    Retrieve all invalid worker oauth keys from the configuration table in the database.
    The keys from the "Keys" section are normalized and returned such that they follow the format:
      {
         "github_api_key": "ghp_XXXXXXXXXXXXXXX",
         "gitlab_api_key": "glpat_XXXXXXXXXXXXXXX"
      }
    """

    keypub = KeyPublisher()
    keys_dict = {}
    for plat in keypub.list_platforms():
        keys = keypub.list_keys(plat)
        if not keys:
            continue

        platform = plat.lower()
        if "github" in platform:
            platform = "Github"
        elif "gitlab" in platform:
            platform = "Gitlab"
        
        keys_dict[platform] = keys
    
    
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
        # Normalize platform names to lowercase.
        platform_lower = platform.lower()
        if platform_lower.endswith("_api_key"):
            keys_dict[platform_lower] = key_value
        else:
            keys_dict[f"{platform_lower}_api_key"] = key_value

    return jsonify(keys_dict), 200


@app.route(f"/{AUGUR_API_VERSION}/workeroauth/delete/key", methods=["POST"])
@ssl_required
@admin_required
def delete_oauth_key():
    """
    Delete a worker oauth key from the KeyPublisher.
    Expects a JSON payload with the platform and token properties.
    """
    data = request.get_json()

    if not data or "platform" not in data or "token" not in data:
        return jsonify(
            {"status": "Bad Request", "message": "Missing platform or token"}
        ), 400

    keypub = KeyPublisher()

    platform = data.get("platform").lower()
    print(f"Platform asish kumar: {platform}")
    if platform == "github":
        keypub.unpublish(data["token"], "github_rest")
        keypub.unpublish(data["token"], "github_graphql")
    elif platform == "gitlab":
        keypub.unpublish(data["token"], "gitlab_rest")

    remove_worker_oauth_key(platform=data["platform"].lower())
    remove_setting(section_name="Keys", setting_name=data["platform"].lower() + "_api_keys")


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