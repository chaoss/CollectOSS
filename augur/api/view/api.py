from flask import Flask, render_template, render_template_string, request, abort, jsonify, redirect, url_for, session, flash
from flask_login import current_user, login_required
from augur.util.repo_load_controller import parse_org_url, parse_repo_url
from .utils import *

def create_routes(server):
    @server.app.route('/cache/file/')
    @server.app.route('/cache/file/<path:file>')
    def cache(file=None):
        if file is None:
            return redirect(url_for('root', path=getSetting('caching')))
        return redirect(url_for('root', path=toCacheFilepath(file)))

    @server.app.route('/account/repos/add', methods = ['POST'])
    @login_required
    def av_add_user_repo():
        url = request.form.get("url")
        group = request.form.get("group_name")

        if group == "None":
            group = current_user.login_name + "_default"

        if not url or not group:
            flash("Repo or org URL must not be empty")
        elif parse_org_url(url):
            current_user.add_org(group, url)
            flash("Successfully added org")
        elif parse_repo_url(url):
            current_user.add_repo(group, url)
            flash("Successfully added repo")
        else:
            flash("Invalid repo or org url")
        
        return redirect(url_for("user_settings") + "?section=tracker")

    @server.app.route('/account/update', methods = ['POST'])
    @login_required
    def user_update_password():
        old_password = request.form.get("password")
        new_password = request.form.get("new_password")

        if current_user.update_password(old_password, new_password):
            flash(f"Account {current_user.login_name} successfully updated")
        else:
            flash("An error occurred updating the account")
        
        return redirect(url_for("user_settings"))
    
    @server.app.route('/account/group/add', methods = ['POST'])
    @login_required
    def user_add_group():
        group = request.form.get("group_name")

        if not group:
            flash("No group name provided")
        elif current_user.add_group(group):
            flash(f"Successfully added group {group}")
        else:
            flash("An error occurred adding group")
        
        return redirect(url_for("user_settings") + "?section=tracker")

    @server.app.route('/account/group/remove')
    @login_required
    def user_remove_group():
        group = request.args.get("group_name")

        if not group:
            flash("No group name provided")
        elif current_user.remove_group(group):
            flash(f"Successfully removed group {group}")
        else:
            flash("An error occurred removing group")
        
        return redirect(url_for("user_settings") + "?section=tracker")

    @server.app.route('/account/repo/remove')
    @login_required
    def user_remove_repo():
        group = request.args.get("group_name")
        repo = request.args.get("repo_id")

        if not repo:
            flash("No repo id provided")
        if not group:
            flash("No group name provided")

        repo = int(repo)


        if current_user.remove_repo(group, repo)[0]:
            flash(f"Successfully removed repo {repo} from group {group}")
        else:
            flash("An error occurred removing repo from group")
        
        return redirect(url_for("user_group_view") + f"?group={group}")
    
    @server.app.route('/account/application/deauthorize')
    @login_required
    def user_app_deauthorize():
        token = request.args.get("token")

        if not token:
            flash("No application provided")
        elif current_user.invalidate_session(token):
            flash("Successfully deauthorized application")
        else:
            flash("Invalid application token")
        
        return redirect(url_for("user_settings") + "?section=application")
    
    @server.app.route('/account/application/create', methods = ['POST'])
    @login_required
    def user_app_create():
        name = request.form.get("app_name")
        url = request.form.get("app_url")

        if not name or not url:
            flash("Must provide app name and redirect URL")
        elif current_user.add_app(name, url):
            flash("Successfully created app")
        else:
            flash("Could not create app")
        
        return redirect(url_for("user_settings") + "?section=application")

    
    """ ----------------------------------------------------------------
    Locking request loop:
        This route will lock the current request until the
        report request completes. A json response is guaranteed.
        Assumes that the requested repo exists.
    """
    @server.app.route('/requests/report/wait/<id>')
    def wait_for_report_request(id):
        requestReports(id)
        return jsonify(report_requests[id])
