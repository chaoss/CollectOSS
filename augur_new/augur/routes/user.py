#SPDX-License-Identifier: MIT
"""
Creates routes for user login functionality
"""

import logging
import requests
import json
from flask import request, Response, jsonify

from db.models import Users

logger = logging.getLogger(__name__)

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

    @server.app.route(f"/{server.api_version}/user/validate", methods=['POST'])
    def validate_user():
        if not request.is_secure:
            return generate_upgrade_request()

        user = response.args.get("user_id")
        password = response.args.get("password")

        if user is None or password is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400

        # TODO database stuff. See pseudocode below

        """
        - SELECT * FROM users WHERE id = user

        - if not result:
            return jsonify({"status": "Invalid user ID"})

        - Hash user's password

        - if not pass_hash == password:
            return jsonify({"status": "invalid password"})

        - return jsonify({"status": "Validated"})
        """

    @server.app.route(f"/{server.api_version}/user/create", methods=['POST'])
    def create_user():
        if not request.is_secure:
            return generate_upgrade_request()

        user = response.args.get("user_id")
        password = response.args.get("password")

        if user is None or password is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400

        # TODO database stuff. See pseudocode below

        user = User(username = name, password = password, email = email)

        db.session.add(user)
        db.commit()

        """
        - SELECT * FROM users WHERE id = user

        - if result:
            return jsonify({"status": "User already exists"})

        - Hash user's password

        - INSERT INTO users VALUES (user, pass_hash)

        - return jsonify({"status": "User created"})
        """
