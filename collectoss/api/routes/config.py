#SPDX-License-Identifier: MIT
"""
Creates routes for config functionality
"""
import logging
from flask import request, jsonify, current_app
import sqlalchemy as s

# Disable the requirement for SSL by setting env["AUGUR_DEV"] = True
from collectoss.application.config import get_development_flag
from collectoss.application.db.lib import get_session
from collectoss.api.util import ssl_required
from collectoss.application.db.models import Config
from collectoss.application.config import SystemConfig
from collectoss.application.db.session import DatabaseSession
from ..server import app

logger = logging.getLogger(__name__)

from collectoss.api.routes import API_VERSION

def generate_upgrade_request():
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426
    response = jsonify({"status": "SSL Required"})
    response.headers["Upgrade"] = "TLS"
    response.headers["Connection"] = "Upgrade"

    return response, 426

@app.route(f"/{API_VERSION}/config/get", methods=['GET', 'POST'])
@ssl_required
def get_config():
    with DatabaseSession(logger, engine=current_app.engine) as session:
        
        config_dict = SystemConfig(logger, session).config.load_config()

    return jsonify(config_dict), 200


@app.route(f"/{API_VERSION}/config/update", methods=['POST'])
@ssl_required
def update_config():
    update_dict = request.get_json()

    with get_session() as session:

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
