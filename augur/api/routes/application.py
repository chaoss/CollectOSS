#SPDX-License-Identifier: MIT
"""
Creates routes for user functionality
"""

import logging
import requests
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
from augur.api.util import api_key_required, ssl_required

from augur.application.db.models import User, UserRepo, UserGroup, UserSessionToken, ClientApplication, RefreshToken
from augur.application.config import get_development_flag
from augur.tasks.init.redis_connection import redis_connection as redis
from ..server import app, engine

logger = logging.getLogger(__name__)
development = get_development_flag()
Session = sessionmaker(bind=engine)

from augur.api.routes import AUGUR_API_VERSION

@app.route(f"/{AUGUR_API_VERSION}/application", methods=['POST'])
@ssl_required
@api_key_required
def get_application_info(application: ClientApplication):
    user: User = application.user
    sessions = application.sessions

    info = {
        "name": application.name,
        "user": user.login_name,
        "active_sessions": len(sessions)
    }

    return info

@app.route(f"/{AUGUR_API_VERSION}/application/group/repos", methods=['POST'])
@ssl_required
@api_key_required
def get_application_group_repos(application: ClientApplication):
    """Select repos from an application's user group by name

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
    group_name = request.args.get("group_name")
    page = request.args.get("page") or 0
    page_size = request.args.get("page_size") or 25
    sort = request.args.get("sort") or "repo_id"
    direction = request.args.get("direction") or "ASC"

    result = application.user.get_group_repos(group_name, page, page_size, sort, direction)

    result_dict = result[1]
    if result[0] is not None:
        
        for repo in result[0]:
            repo["base64_url"] = str(repo["base64_url"].decode())

        result_dict.update({"repos": result[0]})        

    return jsonify(result_dict)

@app.route(f"/{AUGUR_API_VERSION}/application/group/repos/count", methods=['GET', 'POST'])
@ssl_required
@api_key_required
def get_application_group_repo_count(application: ClientApplication):
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
    group_name = request.args.get("group_name")

    result = application.user.get_group_repo_count(group_name)

    result_dict = result[1]
    if result[0] is not None:
        result_dict.update({"repo_count": result[0]})

    return jsonify(result_dict)

@app.route(f"/{AUGUR_API_VERSION}/application/groups/names", methods=['POST'])
@ssl_required
@api_key_required
def get_application_groups(application: ClientApplication):
    user: User = application.user
    result = user.get_group_names()

    return jsonify({"status": "success", "group_names": result[0]})

@app.route(f"/{AUGUR_API_VERSION}/application/groups/repos/", methods=['GET', 'POST'])
@ssl_required
@api_key_required
def get_application_groups_and_repos(application: ClientApplication):
    """Get a list of user groups and their repos"""
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

    data = []
    groups = application.user.groups
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
