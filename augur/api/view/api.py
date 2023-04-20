from flask import Flask, render_template, render_template_string, request, abort, jsonify, redirect, url_for, session, flash
from flask_login import current_user, login_required
from augur.application.db.models import Repo
from .utils import *
from ..server import app

@app.route('/cache/file/')
@app.route('/cache/file/<path:file>')
def cache(file=None):
    if file is None:
        return redirect(url_for('static', filename="cache"))
    return redirect(url_for('static', filename="cache/" + toCacheFilename(file, False)))

@app.route('/account/repos/add', methods = ['POST'])
@login_required
def av_add_user_repo():

    urls = request.form.get('urls')
    group = request.form.get("group_name")

    if not urls:
        flash("No URLs provided")
        return redirect(url_for("user_settings") + "?section=tracker")
    
    # split on commas, carriage returns, and whitespace
    urls = re.split(r'[,\r\s]+', urls)

    # Remove duplicates and empty strings
    # passing None to fitler removes any 
    # values that don't evaluate to true
    urls = list(filter(None, set(urls)))

    if group == "None":
        group = current_user.login_name + "_default"


    added_orgs = 0
    added_repos = 0
    for url in urls:

        # matches https://github.com/{org}/ or htts://github.com/{org}
        if Repo.parse_github_org_url(url):
            added = current_user.add_org(group, url)
            if added:
                added_orgs += 1

        # matches https://github.com/{org}/{repo}/ or htts://github.com/{org}/{repo}
        elif Repo.parse_github_repo_url(url)[0]:
            print("Adding repo")
            added = current_user.add_repo(group, url)
            if added:
                print("Repo added")
                added_repos += 1

        # matches /{org}/{repo}/ or /{org}/{repo} or {org}/{repo}/ or {org}/{repo}
        elif (match := re.match(r'^\/?([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)\/?$', url)):
            org, repo = match.groups()
            repo_url = f"https://github.com/{org}/{repo}/"
            added = current_user.add_repo(group, repo_url)
            if added:
                added_repos += 1

        # matches /{org}/ or /{org} or {org}/ or {org}
        elif (match := re.match(r'^\/?([a-zA-Z0-9_-]+)\/?$', url)):
            org = match.group(1)
            org_url = f"https://github.com/{org}/"
            added = current_user.add_org(group, org_url)
            if added:
                added_orgs += 1


    if not added_orgs and not added_repos:
        flash(f"Unable to add any repos or orgs")
    else:
        flash(f"Successfully added {added_repos} repos and {added_orgs} orgs")
            
    return redirect(url_for("user_settings") + "?section=tracker")

@app.route('/account/update', methods = ['POST'])
@login_required
def user_update_password():
    old_password = request.form.get("password")
    new_password = request.form.get("new_password")

    if current_user.update_password(old_password, new_password):
        flash(f"Account {current_user.login_name} successfully updated")
    else:
        flash("An error occurred updating the account")
    
    return redirect(url_for("user_settings"))

@app.route('/account/group/add', methods = ['POST'])
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

@app.route('/account/group/remove')
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

@app.route('/account/repo/remove')
@login_required
def user_remove_repo():
    group = request.args.get("group_name")
    repo = request.args.get("repo_id")

    if not repo:
        flash("No repo id provided")
    if not group:
        flash("No group name provided")

    repo = int(repo)

    result = current_user.remove_repo(group, repo)[0]

    if result:
        flash(f"Successfully removed repo {repo} from group {group}")
    else:
        flash("An error occurred removing repo from group")
    
    return redirect(url_for("user_group_view") + f"?group={group}")

@app.route('/account/application/deauthorize')
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

@app.route('/account/application/create', methods = ['POST'])
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
@app.route('/requests/report/wait/<id>')
def wait_for_report_request(id):
    requestReports(id)
    return jsonify(report_requests[id])
