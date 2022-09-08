#SPDX-License-Identifier: MIT
"""
Creates routes for user login functionality
"""

import logging
import requests
import json
from flask import request, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker

from augur.application.db.models import User

logger = logging.getLogger(__name__)
from augur.application.db.engine import create_database_engine
Session = sessionmaker(bind=create_database_engine())

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

    @server.app.route(f"/{AUGUR_API_VERSION}/user/validate", methods=['POST'])
    def validate_user():
        if not request.is_secure:
            return generate_upgrade_request()
        session = Session()
        username = request.args.get("username")
        password = request.args.get("password")
        if username is None or password is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400

        user = session.query(User).filter(User.login_name == username).first()
        checkPassword = check_password_hash(user.login_hashword, password)
        if user is None:
            return jsonify({"status": "Invalid username"})
        if checkPassword == False:
            return jsonify({"status": "Invalid password"})
        return jsonify({"status": "Validated"})

    @server.app.route(f"/{AUGUR_API_VERSION}/user/create", methods=['POST', 'GET'])
    def create_user():
        if not request.is_secure:
            return generate_upgrade_request()

        session = Session()
        username = request.args.get("username")
        password = request.args.get("password")
        email = request.args.get("email")
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")

        if username is None or password is None or email is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400
        user = session.query(User).filter(User.login_name == username).first()
        if user is not None:
            return jsonify({"status": "User already exists"})
        emailCheck = session.query(User).filter(User.email == email).first()
        if emailCheck is not None:
            return jsonify({"status": "Email already exists"})
        try:
            user = User(login_name = username, login_hashword = generate_password_hash(password), email = email, first_name = first_name, last_name = last_name, tool_source="User API", tool_version=None, data_source="API")
            session.add(user)
            session.commit()
            return jsonify({"status": "User created"})
        except AssertionError as exception_message: 
            return jsonify(msg='Error: {}. '.format(exception_message)), 400
    
    @server.app.route(f"/{AUGUR_API_VERSION}/user/remove", methods=['GET', 'PUT','DELETE'])
    def delete_user():
        if not request.is_secure:
            return generate_upgrade_request()
        session = Session()
        username = request.args.get("username")
        if username is None:
            return jsonify({"status": "Missing argument"}), 400
        user = session.query(User).filter(User.login_name == username).first()
        if user is None:
            return jsonify({"status": "User does not exist"})
        else:
            session.delete(user)
            session.commit()
            return jsonify({"status": "User deleted"}), 200
    
    @server.app.route(f"/{AUGUR_API_VERSION}/user/update", methods=['GET', 'POST'])
    def update_user():
        session = Session()
        username = request.args.get("username")
        password = request.args.get("password")
        email = request.args.get("email")
        new_login_name = request.args.get("new_username")
        new_password = request.args.get("new_password")
        if username is None:
            return jsonify({"status": "Missing argument"}), 400
        user = session.query(User).filter(User.login_name == username).first()
        checkPassword = check_password_hash(user.login_hashword, password)
        if user is None:
            return jsonify({"status": "User does not exist"})
        if checkPassword == False:
            return jsonify({"status": "Invalid password"}) 
        if user:
            if(email is not None and checkPassword is True):
                user.email = email
                session.commit()
                return jsonify({"status": "Email Updated"})
            if(new_password is not None and checkPassword is True):
                user.login_hashword = generate_password_hash(new_password)
                session.commit()
                return jsonify({"status": "Password Updated"})
            if(new_login_name is not None and checkPassword is True):
                user.login_name = new_login_name
                session.commit()
                return jsonify({"status": "Username Updated"})
