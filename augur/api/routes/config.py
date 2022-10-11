#SPDX-License-Identifier: MIT
"""
Creates routes for config functionality
"""
import logging
import requests
import json
import os
from flask import request, jsonify, Response
import sqlalchemy as s

# Disable the requirement for SSL by setting env["AUGUR_DEV"] = True
from augur.application.config import get_development_flag
from augur.application.db.models import Config
from augur.application.db.session import DatabaseSession

logger = logging.getLogger(__name__)
development = get_development_flag()

AUGUR_API_VERSION = 'api/unstable'

def generate_upgrade_request():
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426
    response = jsonify({"status": "SSL Required"})
    response.headers["Upgrade"] = "TLS"
    response.headers["Connection"] = "Upgrade"

    return response, 426

def create_routes(server):

    @server.app.errorhandler(405)
    def unsupported_method(error):
        return jsonify({"status": "Unsupported method"}), 405


    @server.app.route(f"/{AUGUR_API_VERSION}/config/get", methods=['GET', 'POST'])
    def get_config():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        with DatabaseSession(logger) as session:
            
            config_dict = session.config.load_config()

        return jsonify(config_dict), 200


    @server.app.route(f"/{AUGUR_API_VERSION}/config/update", methods=['POST'])
    def update_config():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        update_dict = request.get_json()

        with DatabaseSession(logger) as session:

            for section, data in update_dict.items():

                for key, value in data.items():

                    try:
                        config_setting = session.query(Config).filter(Config.section_name == section, Config.setting_name == key).one()
                    except s.orm.exc.NoResultFound:
                        return jsonify({"status": "Bad Request", "section": section, "setting": key}), 400

                    config_setting.value = value

                    session.add(config_setting)

            session.commit()

        return jsonify({"status": "success"}), 200


