from flask import Flask, render_template, redirect, url_for, session, request, jsonify
from flask_login import LoginManager
from .utils import *
from .url_converters import *
from .init import logger

# from .server import User
from augur.application.db.models import User, UserSessionToken
from augur.application.db.session import DatabaseSession
from augur.api.routes import AUGUR_API_VERSION
from augur.api.util import get_bearer_token

import time

login_manager = LoginManager()

def create_routes(server):

    login_manager.init_app(server.app)

    server.app.secret_key = getSetting("session_key")

    server.app.url_map.converters['list'] = ListConverter
    server.app.url_map.converters['bool'] = BoolConverter
    server.app.url_map.converters['json'] = JSONConverter

    # Code 404 response page, for pages not found
    @server.app.errorhandler(404)
    def page_not_found(error):
        if AUGUR_API_VERSION in str(request.url_rule):
            return jsonify({"status": "Not Found"}), 404

        return render_template('index.j2', title='404', api_url=getSetting('serving')), 404

    @server.app.errorhandler(405)
    def unsupported_method(error):

        if AUGUR_API_VERSION in str(request.url_rule):
            return jsonify({"status": "Unsupported method"}), 405
        
        return render_message("405 - Method not supported", "The resource you are trying to access does not support the request method used"), 405

    @login_manager.unauthorized_handler
    def unauthorized():

        if AUGUR_API_VERSION in str(request.url_rule):

            with DatabaseSession(logger) as db_session:

                token_str = get_bearer_token()
                token = db_session.query(UserSessionToken).filter(UserSessionToken.token == token_str).first()
                if not token:
                    return jsonify({"status": "Session expired"})

            return jsonify({"status": "Login required"})

        session["login_next"] = url_for(request.endpoint, **request.args)
        return redirect(url_for('user_login'))

    @login_manager.user_loader
    def load_user(user_id):

        db_session = DatabaseSession(logger)

        user = User.get_user(db_session, user_id)
        groups = user.groups
        for group in groups:
            repos = group.repos

        if not user:
            return None

        # The flask_login library sets a unique session["_id"]
        # when login_user() is called successfully
        if session.get("_id") is not None:
        
            user._is_authenticated = True
            user._is_active = True

        return user

    @login_manager.request_loader
    def load_user_request(request):

        print(f"Current time of user request: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
        token = get_bearer_token()
        session = DatabaseSession(logger)

        current_time = int(time.time())
        token = session.query(UserSessionToken).filter(UserSessionToken.token == token, UserSessionToken.expiration >= current_time).first()
        if token:

            print("Valid user")

            user = token.user
            user._is_authenticated = True
            user._is_active = True

            return user
            
        return None

    @server.app.template_filter('as_datetime')
    def as_datetime(seconds):
        time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(seconds))