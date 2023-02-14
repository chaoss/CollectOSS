#SPDX-License-Identifier: MIT
"""
Creates routes for user functionality
"""

import logging
import requests
import json
import os
import base64
import time
import secrets
import pandas as pd
from flask import request, Response, jsonify, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.util.repo_load_controller import RepoLoadController
from augur.api.util import get_bearer_token
from augur.api.util import get_client_token

from augur.application.db.models import User, UserRepo, UserGroup, UserSessionToken, ClientApplication, RefreshToken
from augur.application.config import get_development_flag
from augur.tasks.init.redis_connection import redis_connection as redis
from ..server import app, engine

logger = logging.getLogger(__name__)
development = get_development_flag()
Session = sessionmaker(bind=engine)

from augur.api.routes import AUGUR_API_VERSION

def api_key_required(fun):
    # TODO Optionally rate-limit non authenticated users instead of rejecting requests
    def wrapper(*args, **kwargs):

        client_token = get_client_token()
                    
        # If valid:
        if client_token:

            session = Session()
            try:
                kwargs["application"] = session.query(ClientApplication).filter(ClientApplication.api_key == client_token).one()
                return fun(*args, **kwargs)
            except NoResultFound:
                pass

        return {"status": "Unauthorized client"}
    
    wrapper.__name__ = fun.__name__
    return wrapper

# usage:
"""
@app.route("/path")
@api_key_required
def priviledged_function():
    stuff
"""

# TODO This should probably be available to all endpoints
def generate_upgrade_request():
    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/426
    response = jsonify({"status": "SSL Required"})
    response.headers["Upgrade"] = "TLS"
    response.headers["Connection"] = "Upgrade"

    return response, 426

@app.route(f"/{AUGUR_API_VERSION}/user/validate", methods=['POST'])
def validate_user():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    
    username = request.args.get("username")
    password = request.args.get("password")
    if username is None or password is None:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
        return jsonify({"status": "Missing argument"}), 400

    session = Session()
    user = session.query(User).filter(User.login_name == username).first()
    session.close()

    if user is None:
        return jsonify({"status": "Invalid username"})

    checkPassword = check_password_hash(user.login_hashword, password)
    if checkPassword == False:
        return jsonify({"status": "Invalid password"})


    login_user(user)

    return jsonify({"status": "Validated"})


@app.route(f"/{AUGUR_API_VERSION}/user/logout", methods=['POST'])
@login_required
def logout_user_func():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    if logout_user():
        return jsonify({"status": "Logged out"})

    return jsonify({"status": "Error when logging out"})


@app.route(f"/{AUGUR_API_VERSION}/user/authorize", methods=['POST', 'GET'])
@login_required
def user_authorize():
    code = secrets.token_hex()
    username = current_user.login_name

    redis.set(code, username, ex=300)

    return jsonify({"status": "Validated", "code": code})

@app.route(f"/{AUGUR_API_VERSION}/user/session/generate", methods=['POST'])
@api_key_required
def generate_session(application):
    code = request.args.get("code")
    if not code:
        return jsonify({"status": "Missing argument: code"})
    
    if request.args.get("grant_type") != "code":
        return jsonify({"status": "Invalid grant type"})

    username = redis.get(code)
    redis.delete(code)
    if not username:
        return jsonify({"status": "Invalid authorization code"})

    with DatabaseSession(logger) as session:

        user = User.get_user(session, username)
        if not user:
            return jsonify({"status": "Invalid user"})

        seconds_to_expire = 86400

        existing_session = session.query(UserSessionToken).filter(UserSessionToken.user_id == user.user_id, UserSessionToken.application_id == application.id).first()
        if existing_session:
            existing_session.delete_refresh_tokens(session)

            session.delete(existing_session)
            session.commit()

        user_session_token = UserSessionToken.create(session, user.user_id, application.id, seconds_to_expire).token
        refresh_token = RefreshToken.create(session, user_session_token)

        response = jsonify({"status": "Validated", "username": username, "access_token": user_session_token, "refresh_token" : refresh_token.id, "token_type": "Bearer", "expires": seconds_to_expire})
        response.headers["Cache-Control"] = "no-store"

    return response

@app.route(f"/{AUGUR_API_VERSION}/user/session/refresh", methods=["GET", "POST"])
@api_key_required
def refresh_session(application):
    refresh_token_str = request.args.get("refresh_token")

    if not refresh_token_str:
        return jsonify({"status": "Invalid refresh token"})
    
    if request.args.get("grant_type") != "refresh_token":
        return jsonify({"status": "Invalid grant type"})

    with DatabaseSession(logger) as session:

        refresh_token = session.query(RefreshToken).filter(RefreshToken.id == refresh_token_str).first()
        if not refresh_token:
            return jsonify({"status": "Invalid refresh token"})

        if refresh_token.user_session.application == application:
            return jsonify({"status": "Applications do not match"})

        user_session = refresh_token.user_session
        user = user_session.user

        new_user_session_token = UserSessionToken.create(session, user.user_id, user_session.application.id).token
        new_refresh_token_id = RefreshToken.create(session, new_user_session_token).id
        
        session.delete(refresh_token)
        session.delete(user_session)
        session.commit()

    return jsonify({"status": "Validated", "refresh_token": new_refresh_token_id, "access_token": new_user_session_token, "expires": 86400})


@app.route(f"/{AUGUR_API_VERSION}/user/query", methods=['POST'])
def query_user():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    username = request.args.get("username")
    if username is None:
        return jsonify({"status": "Missing argument"}), 400

    if not User.exists(username):
        return jsonify({"status": "Invalid username"})

    return jsonify({"status": True})

@app.route(f"/{AUGUR_API_VERSION}/user/create", methods=['GET', 'POST'])
def create_user():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    username = request.args.get("username")
    password = request.args.get("password")
    email = request.args.get("email")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    admin = request.args.get("create_admin") or False

    result = User.create_user(username, password, email, first_name, last_name, admin)

    return jsonify(result[1])


@app.route(f"/{AUGUR_API_VERSION}/user/remove", methods=['POST', 'DELETE'])
@login_required
def delete_user():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    status = current_user.delete()
    return jsonify(status)


@app.route(f"/{AUGUR_API_VERSION}/user/update", methods=['POST'])
@login_required
def update_user():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    email = request.args.get("email")
    new_login_name = request.args.get("new_username")
    new_password = request.args.get("new_password")

    if email is not None:
        existing_user = session.query(User).filter(User.email == email).one()
        if existing_user is not None:
            session = Session()
            return jsonify({"status": "Already an account with this email"})

        current_user.email = email
        session.commit()
        session = Session()
        return jsonify({"status": "Email Updated"})

    if new_password is not None:
        current_user.login_hashword = generate_password_hash(new_password)
        session.commit()
        session = Session()
        return jsonify({"status": "Password Updated"})

    if new_login_name is not None:
        existing_user = session.query(User).filter(User.login_name == new_login_name).one()
        if existing_user is not None:
            return jsonify({"status": "Username already taken"})

        current_user.login_name = new_login_name
        session.commit()
        session = Session()
        return jsonify({"status": "Username Updated"})

    return jsonify({"status": "Missing argument"}), 400


@app.route(f"/{AUGUR_API_VERSION}/user/repo/add", methods=['GET', 'POST'])
@login_required
def add_user_repo():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    repo = request.args.get("repo_url")
    group_name = request.args.get("group_name")

    result = current_user.add_repo(group_name, repo)

    return jsonify(result[1])


@app.route(f"/{AUGUR_API_VERSION}/user/group/add", methods=['GET', 'POST'])
@login_required
def add_user_group():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    group_name = request.args.get("group_name")

    result = current_user.add_group(group_name)

    return jsonify(result[1])

@app.route(f"/{AUGUR_API_VERSION}/user/group/remove", methods=['GET', 'POST'])
@login_required
def remove_user_group():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    group_name = request.args.get("group_name")

    result = current_user.remove_group(group_name)

    return jsonify(result[1])


@app.route(f"/{AUGUR_API_VERSION}/user/org/add", methods=['GET', 'POST'])
@login_required
def add_user_org():
    if not development and not request.is_secure:
        return generate_upgrade_request()

    org = request.args.get("org_url")
    group_name = request.args.get("group_name")

    result = current_user.add_org(group_name, org)

    return jsonify(result[1])


@app.route(f"/{AUGUR_API_VERSION}/user/repo/remove", methods=['GET', 'POST'])
@login_required
def remove_user_repo():
    if not development and not request.is_secure:
        return generate_upgrade_request()


    group_name = request.args.get("group_name")

    try:
        repo_id = int(request.args.get("repo_id"))
    except TypeError:
        return {"status": "Repo id must be and integer"}

    result = current_user.remove_repo(group_name, repo_id)

    return jsonify(result[1])

@app.route(f"/{AUGUR_API_VERSION}/user/group/repos/", methods=['GET', 'POST'])
@login_required
def group_repos():
    """Select repos from a user group by name

    Arguments
    ----------
    group_name : str
        The name of the group to select
    page : int = 0 -> [>= 0]
        The page offset to use for pagination (optional)
    page_size : int = 25 -> [> 0]
        The number of result per page (optional)
    sort : str
        The name of the column to sort the data by (optional)
    direction : str = "ASC" -> ["ASC" | "DESC"]
        The direction to be used for sorting (optional)

    Returns
    -------
    list
        A list of dictionaries containing repos which match the given arguments
    """

    if not development and not request.is_secure:
        return generate_upgrade_request()

    group_name = request.args.get("group_name")
    page = request.args.get("page") or 0
    page_size = request.args.get("page_size") or 25
    sort = request.args.get("sort") or "repo_id"
    direction = request.args.get("direction") or "ASC"

    result = current_user.get_group_repos(group_name, page, page_size, sort, direction)


    result_dict = result[1]
    if result[0] is not None:
        
        for repo in result[0]:
            repo["base64_url"] = str(repo["base64_url"].decode())

        result_dict.update({"repos": result[0]})        

    return jsonify(result_dict)

@app.route(f"/{AUGUR_API_VERSION}/user/group/repos/count", methods=['GET', 'POST'])
@login_required
def group_repo_count():
    """Count repos from a user group by name

    Arguments
    ----------
    username : str
        The username of the user making the request
    group_name : str
        The name of the group to select

    Returns
    -------
    int
        A count of the repos in the given user group
    """

    if not development and not request.is_secure:
        return generate_upgrade_request()

    group_name = request.args.get("group_name")

    result = current_user.get_group_repo_count(group_name)

    result_dict = result[1]
    if result[0] is not None:
        result_dict.update({"repo_count": result[0]})

    return jsonify(result_dict)

@app.route(f"/{AUGUR_API_VERSION}/user/groups/names", methods=['GET', 'POST'])
@login_required
def get_user_groups():
    """Get a list of user groups by username

    Arguments
    ----------
    username : str
        The username of the user making the request

    Returns
    -------
    list
        A list of group names associated with the given username
    """

    if not development and not request.is_secure:
        return generate_upgrade_request()

    result = current_user.get_group_names()

    return jsonify({"status": "success", "group_names": result[0]})

@app.route(f"/{AUGUR_API_VERSION}/user/groups/repos/", methods=['GET', 'POST'])
@login_required
def get_user_groups_and_repos():
    """Get a list of user groups and their repos"""

    if not development and not request.is_secure:
        return generate_upgrade_request()

    columns = request.args.get("columns")
    if not columns:
        return {"status": "Missing argument columns"}

    # split list by , and remove whitespaces from edges

    valid_columns = []
    columns =  columns.split(",")
    for column in columns:

        if column.isspace() or column == "":
            continue

        valid_columns.append(column.strip())

    print(valid_columns)


    data = []
    groups = current_user.groups
    for group in groups:

        repos = [repo.repo for repo in group.repos]

        group_repo_dicts = []
        for repo in repos:

            repo_dict = {}
            for column in valid_columns:
                try:
                    repo_dict[column] = getattr(repo, column)
                except AttributeError:
                    return {"status": f"'{column}' is not a valid repo column"}

            group_repo_dicts.append(repo_dict)

        group_data = {"repos": group_repo_dicts, "favorited": group.favorited}
        data.append({group.name: group_data})

    return jsonify({"status": "success", "data": data})


@app.route(f"/{AUGUR_API_VERSION}/user/group/favorite/toggle", methods=['GET', 'POST'])
@login_required
def toggle_user_group_favorite():
    """Toggle the favorite status on a group

    Returns
    -------
    dict
        A dictionairy with key of 'status' that indicates the success or failure of the operation
    """

    if not development and not request.is_secure:
        return generate_upgrade_request()

    group_name = request.args.get("group_name")

    result = current_user.toggle_group_favorite(group_name)

    return jsonify(result[1])

@app.route(f"/{AUGUR_API_VERSION}/user/groups/favorites", methods=['GET', 'POST'])
@login_required
def get_favorite_groups():
    """Get a list of a users favorite groups

    Returns
    -------
    list
        A list of group names
    """

    if not development and not request.is_secure:
        return generate_upgrade_request()

    result = current_user.get_favorite_groups()
    groups = result[0]
    if groups is None:
        return jsonify(result[1])

    group_names = [group.name for group in groups]

    return jsonify({"status": "success", "group_names": group_names})
    