#SPDX-License-Identifier: MIT
"""
Creates routes for user login functionality
"""

import logging
import requests
import json
import hashlib
from flask import request, Response, jsonify
from sqlalchemy.sql import text

from augur.application.db.models import User

logger = logging.getLogger(__name__)
from augur.application.db.engine import engine

AUGUR_API_VERSION = 'api/unstable'

def hash_algorithm():
    return hashlib.sha256()

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

    server.app.route(f"/{AUGUR_API_VERSION}/user/validate", methods=['POST', 'GET'])
    def validate_user():
        if not request.is_secure:
            return generate_upgrade_request()

        login_name = request.args.get("username")
        password = request.args.get("password")

        if login_name is None or password is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400
        with engine.connect() as connection:
            hashing = hash_algorithm()
            hashing.update(password.encode('utf8'))
            pass_hash = hashing.hexdigest()
            result = connection.execute("SELECT * FROM users WHERE login_name = %(login_name)s",{ 'login_name' : login_name }).fetchall()
            checkPassword = connection.execute("SELECT login_hashword FROM users WHERE login_name = %(login_name)s",{ 'login_name' : login_name }).fetchall()
            if not len(result) > 0:
                return jsonify({"status": "Invalid username"})
            if not pass_hash == checkPassword[0]['login_hashword']:
                return jsonify({"status": "Invalid password"})
            return jsonify({"status": "Validated"})

    server.app.route(f"/{AUGUR_API_VERSION}/user/create", methods=['POST', 'GET'])
    def create_user():
        if not request.is_secure:
            return generate_upgrade_request()

        with engine.connect() as connection:
            login_name = request.args.get("username")
            password = request.args.get("password")
            email = request.args.get("email")
            first_name = request.args.get("first_name")
            last_name = request.args.get("last_name")

            if login_name is None or password is None or email is None:
                # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
                return jsonify({"status": "Missing argument"}), 400

            checkUsername = connection.execute("SELECT * FROM users WHERE login_name = %(login_name)s",{ 'login_name' : login_name }).fetchall()
            checkEmail = connection.execute("SELECT * FROM users WHERE email = %(email)s",{ 'email' : email }).fetchall()
            if len(checkUsername) > 0:
                return jsonify({"status": "User already exists"})
            elif len(checkEmail) > 0:
                return jsonify({"status": "Email already exists"})
            else:
                try:
                    hashing = hash_algorithm()
                    hashing.update(password.encode('utf8'))
                    login_hashword = hashing.hexdigest()
                    statement = text("INSERT INTO users (login_name, login_hashword, email, first_name, last_name) VALUES (:login_name, :login_hashword, :email, :first_name, :last_name)")
                    connection.execute(statement, {'login_name': login_name, 'login_hashword': login_hashword, 'email': email, "first_name": first_name, "last_name": last_name})
                    return jsonify({"status": "User created"})
                except AssertionError as exception_message: 
                        return jsonify(msg='Error: {}. '.format(exception_message)), 400
