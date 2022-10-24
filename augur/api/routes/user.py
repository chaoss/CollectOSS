#SPDX-License-Identifier: MIT
"""
Creates routes for user login functionality
"""

import logging
import requests
import json
import os
from flask import request, Response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.util.repo_load_controller import RepoLoadController


from augur.application.db.models import User, UserRepo
from augur.application.config import get_development_flag
logger = logging.getLogger(__name__)
development = get_development_flag()
from augur.application.db.engine import create_database_engine
Session = sessionmaker(bind=create_database_engine())

AUGUR_API_VERSION = 'api/unstable'

# TODO This should probably be available to all endpoints
def generate_upgrade_request():
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426
    response = jsonify({"status": "SSL Required"})
    response.headers["Upgrade"] = "TLS"
    response.headers["Connection"] = "Upgrade"

    return response, 426

def create_routes(server):
    # TODO This functionality isn't specific to the User endpoints, and should be moved
    @server.app.errorhandler(405)
    def unsupported_method(error):
        return jsonify({"status": "Unsupported method"}), 405

    @server.app.route(f"/{AUGUR_API_VERSION}/user/validate", methods=['POST'])
    def validate_user():
        if not development and not request.is_secure:
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
    
    @server.app.route(f"/{AUGUR_API_VERSION}/user/query", methods=['POST'])
    def query_user():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        session = Session()
        username = request.args.get("username")
        if username is None:
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
            return jsonify({"status": "Missing argument"}), 400
        user = session.query(User).filter(User.login_name == username).first()
        
        if user is None:
            return jsonify({"status": "Invalid username"})

        return jsonify({"status": True})

    @server.app.route(f"/{AUGUR_API_VERSION}/user/create", methods=['POST'])
    def create_user():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        session = Session()
        username = request.args.get("username")
        password = request.args.get("password")
        email = request.args.get("email")
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")
        admin = request.args.get("create_admin") or False

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
            user = User(login_name = username, login_hashword = generate_password_hash(password), email = email, first_name = first_name, last_name = last_name, tool_source="User API", tool_version=None, data_source="API", admin=False)
            session.add(user)
            session.commit()
            return jsonify({"status": "User created"})
        except AssertionError as exception_message: 
            return jsonify(msg='Error: {}. '.format(exception_message)), 400
    
    @server.app.route(f"/{AUGUR_API_VERSION}/user/remove", methods=['POST', 'DELETE'])
    def delete_user():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        session = Session()
        username = request.args.get("username")
        if username is None:
            return jsonify({"status": "Missing argument"}), 400

        user = session.query(User).filter(User.login_name == username).first()
       
        if user is None:
            return jsonify({"status": "User does not exist"})

        user_repos = session.query(UserRepo).filter(UserRepo.user_id == user.user_id).all()
        for repo in user_repos:
            session.delete(repo)

        session.delete(user)
        session.commit()
        return jsonify({"status": "User deleted"}), 200

    @server.app.route(f"/{AUGUR_API_VERSION}/user/update", methods=['POST'])
    def update_user():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        session = Session()
        username = request.args.get("username")
        password = request.args.get("password")
        email = request.args.get("email")
        new_login_name = request.args.get("new_username")
        new_password = request.args.get("new_password")

        if username is None or password is None:
            return jsonify({"status": "Missing argument"}), 400

        user = session.query(User).filter(User.login_name == username).first()
        if user is None:
            return jsonify({"status": "User does not exist"})

        checkPassword = check_password_hash(user.login_hashword, password)
        if checkPassword == False:
            return jsonify({"status": "Invalid password"}) 

        if email is not None:
            existing_user = session.query(User).filter(User.email == email).one()
            if existing_user is not None:
                return jsonify({"status": "Already an account with this email"})

            user.email = email
            session.commit()
            return jsonify({"status": "Email Updated"})

        if new_password is not None:
            user.login_hashword = generate_password_hash(new_password)
            session.commit()
            return jsonify({"status": "Password Updated"})

        if new_login_name is not None:
            existing_user = session.query(User).filter(User.login_name == new_login_name).one()
            if existing_user is not None:
                return jsonify({"status": "Username already taken"})

            user.login_name = new_login_name
            session.commit()
            return jsonify({"status": "Username Updated"})

        return jsonify({"status": "Missing argument"}), 400

    @server.app.route(f"/{AUGUR_API_VERSION}/user/repos", methods=['GET', 'POST'])
    def user_repos():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        username = request.args.get("username")

        with DatabaseSession(logger) as session:
    
            if username is None:
                return jsonify({"status": "Missing argument"}), 400
            user = session.query(User).filter(User.login_name == username).first()
            if user is None:
                return jsonify({"status": "User does not exist"})
            
            repo_load_controller = RepoLoadController(gh_session=session)

            repo_ids = repo_load_controller.get_user_repo_ids(user.user_id)

            return jsonify({"status": "success", "repo_ids": repo_ids})

    @server.app.route(f"/{AUGUR_API_VERSION}/user/add_repo", methods=['GET', 'POST'])
    def add_user_repo():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        username = request.args.get("username")
        repo = request.args.get("repo_url")

        with GithubTaskSession(logger) as session:

            if username is None:
                return jsonify({"status": "Missing argument"}), 400
            user = session.query(User).filter(
                User.login_name == username).first()
            if user is None:
                return jsonify({"status": "User does not exist"})

            repo_load_controller = RepoLoadController(gh_session=session)

            result = repo_load_controller.add_frontend_repo(repo, user.user_id)

            return jsonify(result)


    @server.app.route(f"/{AUGUR_API_VERSION}/user/add_org", methods=['GET', 'POST'])
    def add_user_org():
        if not development and not request.is_secure:
            return generate_upgrade_request()

        username = request.args.get("username")
        org = request.args.get("org_url")

        with GithubTaskSession(logger) as session:

            if username is None:
                return jsonify({"status": "Missing argument"}), 400
            user = session.query(User).filter(
                User.login_name == username).first()
            if user is None:
                return jsonify({"status": "User does not exist"})

            repo_load_controller = RepoLoadController(gh_session=session)

            result = repo_load_controller.add_frontend_org(org, user.user_id)

            return jsonify(result)


        
