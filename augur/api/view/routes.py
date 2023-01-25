import logging
from flask import Flask, render_template, render_template_string, request, abort, jsonify, redirect, url_for, session, flash
from sqlalchemy.orm.exc import NoResultFound
from .utils import *
from flask_login import login_user, logout_user, current_user, login_required

from augur.application.db.models import User, Repo, ClientApplication
from .server import LoginException
from augur.application.db.session import DatabaseSession
from augur.tasks.init.redis_connection import redis_connection as redis
from augur.application.util import *
from augur.application.config import AugurConfig

logger = logging.getLogger(__name__)


# ROUTES -----------------------------------------------------------------------

def create_routes(server):
    """ ----------------------------------------------------------------
    root:
        This route returns a redirect to the application root, appended
        by the provided path, if any.
    """
    @server.app.route('/root/')
    @server.app.route('/root/<path:path>')
    def root(path=""):
        return redirect(getSetting("approot") + path)

    """ ----------------------------------------------------------------
    logo:
        this route returns a redirect to the application logo associated
        with the provided brand, otherwise the inverted Augur logo if no
        brand is provided.
    """
    @server.app.route('/logo/')
    @server.app.route('/logo/<string:brand>')
    def logo(brand=None):
        if brand is None:
            return redirect(url_for('static', filename='img/augur_logo.png'))
        elif "augur" in brand:
            return logo(None)
        elif "chaoss" in brand:
            return redirect(url_for('static', filename='img/Chaoss_Logo_white.png'))
        return ""

    """ ----------------------------------------------------------------
    default:
    table:
        This route returns the default view of the application, which
        is currently defined as the repository table view
    """
    @server.app.route('/')
    @server.app.route('/repos/views/table')
    def repo_table_view():
        query = request.args.get('q')
        try:
            page = int(request.args.get('p') or 0)
        except:
            page = 1

        sorting = request.args.get('s')
        rev = request.args.get('r')

        if rev is not None:
            if rev == "False":
                rev = False
            elif rev == "True":
                rev = True
        
        direction = "DESC" if rev else "ASC"

        with DatabaseSession(logger) as db_session:
            config = AugurConfig(logger, db_session)
    
            pagination_offset = config.get_value("frontend", "pagination_offset")

        
        if current_user.is_authenticated:
            data = current_user.get_repos(page = page, sort = sorting, direction = direction)[0]
            page_count = (current_user.get_repo_count()[0] or 0) // pagination_offset
        else:
            data = get_all_repos(page = page, sort = sorting, direction = direction)[0]
            page_count = (get_all_repos_count()[0] or 0) // pagination_offset
        
        #if not cacheFileExists("repos.json"):
        #    return renderLoading("repos/views/table", query, "repos.json")

        # return renderRepos("table", query, data, sorting, rev, page, True)
        return render_module("repos-table", title="Repos", repos=data, query_key=query, activePage=page, pages=page_count, offset=pagination_offset, PS="repo_table_view", reverse = rev, sorting = sorting)

    """ ----------------------------------------------------------------
    card:
        This route returns the repository card view
    """
    @server.app.route('/repos/views/card')
    def repo_card_view():
        query = request.args.get('q')
        if current_user.is_authenticated:
            count = current_user.get_repo_count()[0]
            data = current_user.get_repos(page_size = count)[0]
        else:
            count = get_all_repos_count()[0]
            data = get_all_repos(page_size=count)[0]

        return renderRepos("card", query, data, filter = True)

    """ ----------------------------------------------------------------
    groups:
        This route returns the groups table view, listing all the current
        groups in the backend
    """
    # @server.app.route('/groups')
    # @server.app.route('/groups/<group>')
    # def repo_groups_view(group=None):
    #     query = request.args.get('q')
    #     page = request.args.get('p')

    #     if(group is not None):
    #         query = group

    #     if(query is not None):
    #         buffer = []
    #         data = requestJson("repos")
    #         for repo in data:
    #             if query == str(repo["repo_group_id"]) or query in repo["rg_name"]:
    #                 buffer.append(repo)
    #         return renderRepos("table", query, buffer, page = page, pageSource = "repo_groups_view")
    #     else:
    #         groups = requestJson("repo-groups")
    #         return render_template('index.html', body="groups-table", title="Groups", groups=groups, query_key=query, api_url=getSetting('serving'))

    """ ----------------------------------------------------------------
    status:
        This route returns the status view, which displays information
        about the current status of collection in the backend
    """
    @server.app.route('/status')
    def status_view():
        return render_module("status", title="Status")

    """ ----------------------------------------------------------------
    login:
        Under development
    """
    @server.app.route('/account/login', methods=['GET', 'POST'])
    def user_login():
        if request.method == 'POST':
            try:
                username = request.form.get('username')
                remember = request.form.get('remember') is not None
                password = request.form.get('password')
                register = request.form.get('register')

                if username is None:
                    raise LoginException("A login issue occurred")

                with DatabaseSession(logger) as db_session:
                    user = User.get_user(db_session, username)

                    if not user and register is None:
                        raise LoginException("Invalid login credentials")
                    
                    # register a user
                    if register is not None:
                        if user:
                            raise LoginException("User already exists")
                        
                        email = request.form.get('email')
                        first_name = request.form.get('first_name')
                        last_name = request.form.get('last_name')
                        admin = request.form.get('admin') or False

                        result = User.create_user(db_session, username, password, email, first_name, last_name, admin)
                        if not result[0]:
                            raise LoginException("An error occurred registering your account")
                        else:
                            user = User.get_user(username)
                            flash(result[1]["status"])

                # Log the user in if the password is valid
                if user.validate(password) and login_user(user, remember = remember):
                    flash(f"Welcome, {username}!")
                    if "login_next" in session:
                        return redirect(session.pop("login_next"))
                    return redirect(url_for('root'))
                else:
                    print("Invalid login")
                    raise LoginException("Invalid login credentials")
            except LoginException as e:
                flash(str(e))
        return render_module('login', title="Login")

    """ ----------------------------------------------------------------
    logout:
        Under development
    """
    @server.app.route('/account/logout')
    @login_required
    def user_logout():
        logout_user()
        flash("You have been logged out")
        return redirect(url_for('root'))

    """ ----------------------------------------------------------------
    default:
    table:
        This route performs external authorization for a user
    """
    @server.app.route('/user/authorize')
    @login_required
    def authorize_user():
        client_id = request.args.get("client_id")
        state = request.args.get("state")
        response_type = request.args.get("response_type")

        if not client_id or response_type != "code":
            return render_message("Invalid Request", "Something went wrong. You may need to return to the previous application and make the request again.")
        
        # TODO get application from client id
        client = ClientApplication.get_by_id(client_id)            
        
        return render_module("authorization", app = client, state = state)

    @server.app.route('/account/delete')
    @login_required
    def user_delete():
        if current_user.delete()[0]:
            flash(f"Account {current_user.login_name} successfully removed")
            logout_user()
        else:
            flash("An error occurred removing the account")

        return redirect(url_for("root"))

    """ ----------------------------------------------------------------
    settings:
        Under development
    """
    @server.app.route('/account/settings')
    @login_required
    def user_settings():
        return render_template("settings.j2")

    """ ----------------------------------------------------------------
    report page:
        This route returns a report view of the requested repo (by ID).
    """
    @server.app.route('/repos/views/repo/<id>')
    def repo_repo_view(id):
        # For some reason, there is no reports definition (shouldn't be possible)
        if reports is None:
            return render_message("Report Definitions Missing", "You requested a report for a repo on this instance, but a definition for the report layout was not found.")

        repo = Repo.get_by_id(id)

        return render_module("repo-info", reports=reports.keys(), images=reports, title="Repo", repo=repo, repo_id=id)

    """ ----------------------------------------------------------------
    default:
    table:
        This route returns the default view of the application, which
        is currently defined as the repository table view
    """
    @server.app.route('/user/group/')
    @login_required
    def user_group_view():
        group = request.args.get("group")

        if not group:
            return render_message("No Group Specified", "You must specify a group to view this page.")

        params = {}

        try:
            params["page"] = int(request.args.get('p') or 0)
        except:
            params["page"] = 1

        if sort := request.args.get('s'):
            params["sort"] = sort

        rev = request.args.get('r')
        if rev is not None:
            if rev == "False":
                rev = False
                params["direction"] = "ASC"
            elif rev == "True":
                rev = True
                params["direction"] = "DESC"

        with DatabaseSession(logger) as db_session:
            config = AugurConfig(logger, db_session)

            pagination_offset = config.get_value("frontend", "pagination_offset")

        data = current_user.get_group_repos(group, **params)[0]
        page_count = (current_user.get_group_repo_count(group)[0]) or 0
        page_count //= pagination_offset

        if not data:
            return render_message("Error Loading Group", "Either the group you requested does not exist, the group has no repos, or an unspecified error occurred.")

        #if not cacheFileExists("repos.json"):
        #    return renderLoading("repos/views/table", query, "repos.json")

        # return renderRepos("table", None, data, sort, rev, params.get("page"), True)
        return render_module("user-group-repos-table", title="Repos", repos=data, query_key=None, activePage=params["page"], pages=page_count, offset=pagination_offset, PS="user_group_view", reverse = rev, sorting = params.get("sort"), group=group)

    """ ----------------------------------------------------------------
    Admin dashboard:
        View the admin dashboard.
    """
    @server.app.route('/dashboard')
    def dashboard_view():
        empty = [
            { "title": "Placeholder", "settings": [
                { "id": "empty",
                    "display_name": "Empty Entry",
                    "value": "NULL",
                    "description": "There's nothing here 👻"
                }
            ]}
        ]

        backend_config = requestJson("config/get", False)

        return render_template('admin-dashboard.j2', sections = empty, config = backend_config)
