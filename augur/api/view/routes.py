import logging
from flask import Flask, render_template, render_template_string, request, abort, jsonify, redirect, url_for, session, flash
from sqlalchemy.orm.exc import NoResultFound
from .utils import *
from flask_login import login_user, logout_user, current_user, login_required

from augur.application.db.models import User, Repo, ClientApplication
from .server import LoginException
from augur.tasks.init.redis_connection import redis_connection as redis
from augur.application.util import *
from augur.application.config import AugurConfig
from ..server import app, db_session
from augur.application.services.email import get_email_provider

logger = logging.getLogger(__name__)


# ROUTES -----------------------------------------------------------------------

""" ----------------------------------------------------------------
root:
    This route returns a redirect to the application root, appended
    by the provided path, if any.
"""
@app.route('/root/')
@app.route('/root/<path:path>')
def root(path=""):
    return redirect(getSetting("approot") + path)

""" ----------------------------------------------------------------
logo:
    this route returns a redirect to the application logo associated
    with the provided brand, otherwise the inverted Augur logo if no
    brand is provided.
"""
@app.route('/logo/')
@app.route('/logo/<string:brand>')
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
@app.route('/')
@app.route('/repos/views/table')
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

    config = AugurConfig(logger, db_session)

    pagination_offset = config.get_value("frontend", "pagination_offset")
    
    if current_user.is_authenticated:
        data = current_user.get_repos(page = page, sort = sorting, direction = direction, search=query)[0]
        page_count = (current_user.get_repo_count(search = query)[0] or 0) // pagination_offset
    else:
        data = get_all_repos(page = page, sort = sorting, direction = direction, search=query)[0]
        page_count = (get_all_repos_count(search = query)[0] or 0) // pagination_offset
    
    #if not cacheFileExists("repos.json"):
    #    return renderLoading("repos/views/table", query, "repos.json")

    # return renderRepos("table", query, data, sorting, rev, page, True)
    return render_module("repos-table", title="Repos", repos=data, query_key=query, activePage=page, pages=page_count, offset=pagination_offset, PS="repo_table_view", reverse = rev, sorting = sorting)

""" ----------------------------------------------------------------
card:
    This route returns the repository card view
"""
@app.route('/repos/views/card')
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
# @app.route('/groups')
# @app.route('/groups/<group>')
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
@app.route('/collection/status')
def status_view():
    return render_module("status", title="Status")

""" ----------------------------------------------------------------
login:
    Under development
"""
@app.route('/account/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            remember = request.form.get('remember') is not None
            password = request.form.get('password')
            register = request.form.get('register')

            if username is None:
                raise LoginException("A login issue occurred")

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

                result = User.create_user(username, password, email, first_name, last_name, admin)
                if not result[0]:
                    raise LoginException("An error occurred registering your account")
                else:
                    user = User.get_user(db_session, username)
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
@app.route('/account/logout')
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
@app.route('/user/authorize')
@login_required
def authorize_user():
    client_id = request.args.get("client_id")
    state = request.args.get("state")
    response_type = request.args.get("response_type")

    if not client_id or response_type != "code":
        return render_message("Invalid Request", "Something went wrong. You may need to return to the previous application and make the request again.")
    
    # TODO get application from client id
    client = ClientApplication.get_by_id(db_session, client_id)            

    return render_module("authorization", app = client, state = state)

@app.route('/account/delete')
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
@app.route('/account/settings')
@login_required
def user_settings():
    if not current_user.email_verified:
        return redirect(url_for("user_verify_email"))
    
    return render_template("settings.j2")

""" ----------------------------------------------------------------
email verification:
    Under development
"""
@app.route('/account/verify')
@login_required
def user_verify_email():
    email = get_email_provider()

    if not email:
        return render_message("Email Verification Disabled", "Email verification has not been enabled on this instance.")
    elif current_user.email_verified:
        return redirect(url_for("user_settings"))
    
    email.user_verify(current_user)

    return render_module("verify-email")

""" ----------------------------------------------------------------
email verification:
    Under development
"""
@app.route('/account/password/reset')
def user_password_reset():
    email_body = """<strong>This link expires in 5 minutes.</strong>

    {}

    <small>If you did not make this request, you can disregard this message.</small>"""

    if not config.get_value("service", "email"):
        return render_message("Email Service Disabled", "Email has not been enabled on this instance.")
    elif key := request.args.get("key"):
        return redirect(url_for("user_settings"))
    elif True: #not redis.get(current_user.email):
        OTP = secrets.token_hex()

        # TODO: finish setup

        message = Mail(
            from_email=config.get_value("email.service", "source_email"),
            to_emails=current_user.email,
            subject='Augur password reset',
            html_content=email_body.format(OTP))
        logger.info(str(message))
        try:
            sg = SendGridAPIClient(config.get_value("email.service", "provider_key"))
            response = sg.send(message)
            logger.info(response.status_code)
            logger.info(response.body)
            logger.info(response.headers)
        except Exception as e:
            logger.error(e.message)

        redis.set(current_user.email, OTP, ex = 5 * 60)

    return render_module("reset-password")

""" ----------------------------------------------------------------
report page:
    This route returns a report view of the requested repo (by ID).
"""
@app.route('/repos/views/repo/<id>')
def repo_repo_view(id):
    # For some reason, there is no reports definition (shouldn't be possible)
    if reports is None:
        return render_message("Report Definitions Missing", "You requested a report for a repo on this instance, but a definition for the report layout was not found.")

    repo = Repo.get_by_id(db_session, id)

    return render_module("repo-info", reports=reports.keys(), images=reports, title="Repo", repo=repo, repo_id=id)

""" ----------------------------------------------------------------
default:
table:
    This route returns the groups view for the logged in user.
"""
@app.route('/user/groups/')
@login_required
def user_groups_view():
    params = {}

    config = AugurConfig(logger, db_session)

    pagination_offset = config.get_value("frontend", "pagination_offset")

    params = {}
    
    if query := request.args.get('q'):
        params["search"] = query

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

    try:
        activepage = int(request.args.get('p')) if 'p' in request.args else 0
    except:
        activepage = 0

    (groups, status) = current_user.get_groups_info(**params)

    # if not groups and not query:
    #     return render_message("No Groups Defined", "You do not have any groups defined, you can add groups on you profile page.")
    # elif not groups:
    #     return render_message("No Matching Groups", "Your search did not match any group names.")

    page_count = len(groups)
    page_count //= pagination_offset
    current_page_start = activepage * pagination_offset
    current_page_end = current_page_start + pagination_offset

    groups = groups[current_page_start : current_page_end]

    return render_module("groups-table", title="Groups", groups=groups, query_key=query, activePage=activepage, pages=page_count, offset=pagination_offset, PS="user_groups_view", reverse = rev, sorting = sort)


""" ----------------------------------------------------------------
default:
table:
    This route returns the groups view for the logged in user.
"""
@app.route('/user/group/<group>')
@login_required
def user_group_view(group = None):
    if not group:
        return render_message("No Group Specified", "You must specify a group to view this page.")

    params = {}

    try:
        params["page"] = int(request.args.get('p') or 0)
    except:
        params["page"] = 1
    
    if query := request.args.get('q'):
        params["search"] = query

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

    config = AugurConfig(logger, db_session)

    pagination_offset = config.get_value("frontend", "pagination_offset")

    data = current_user.get_group_repos(group, **params)[0]
    page_count = current_user.get_group_repo_count(group, search = query)[0] or 0
    page_count //= pagination_offset

    # if not data:
    #     return render_message("Error Loading Group", "Either the group you requested does not exist, the group has no repos, or an unspecified error occurred.")

    #if not cacheFileExists("repos.json"):
    #    return renderLoading("repos/views/table", query, "repos.json")

    # return renderRepos("table", None, data, sort, rev, params.get("page"), True)
    return render_module("user-group-repos-table", title="Repos", repos=data, query_key=query, activePage=params["page"], pages=page_count, offset=pagination_offset, PS="user_group_view", reverse = rev, sorting = params.get("sort"), group=group)

@app.route('/error')
def throw_exception():
    raise Exception("This Exception intentionally raised")

""" ----------------------------------------------------------------
Admin dashboard:
    View the admin dashboard.
"""
@app.route('/dashboard')
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
