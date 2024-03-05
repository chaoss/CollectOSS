from flask import request, jsonify, redirect, url_for, flash, current_app
import re
from flask_login import current_user, login_required
from augur.application.db.models import Repo, RepoGroup, UserGroup, UserRepo
from augur.tasks.frontend import add_org_repo_list, parse_org_and_repo_name, parse_org_name
from .utils import *
from ..server import app
from augur.application.db.session import DatabaseSession

@app.route('/cache/file/')
@app.route('/cache/file/<path:file>')
def cache(file=None):
    if file is None:
        return redirect(url_for('static', filename="cache"))
    return redirect(url_for('static', filename="cache/" + toCacheFilename(file, False)))


def add_existing_repo_to_group(session, user_id, group_name, repo_id):

    logger.info("Adding existing repo to group")

    group_id = UserGroup.convert_group_name_to_id(session, user_id, group_name)
    if group_id is None:
        return False
    
    result = UserRepo.insert(session, repo_id, group_id)
    if not result:
        return False
    
def add_existing_org_to_group(session, user_id, group_name, rg_id):

    logger.info("Adding existing org to group")

    group_id = UserGroup.convert_group_name_to_id(session, user_id, group_name)
    if group_id is None:
        return False
    
    repos = session.query(Repo).filter(Repo.repo_group_id == rg_id).all()
    logger.info("Length of repos in org: " + str(len(repos)))
    for repo in repos:
        result = UserRepo.insert(session, repo.repo_id, group_id)
        if not result:
            logger.info("Failed to add repo to group")
    


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

    invalid_urls = []

    with DatabaseSession(logger, current_app.engine) as session:
        for url in urls:  

            # matches https://github.com/{org}/ or htts://github.com/{org}
            if (org_name := Repo.parse_github_org_url(url)):
                rg_obj = RepoGroup.get_by_name(session, org_name)
                if rg_obj:
                    # add the orgs repos to the group
                    add_existing_org_to_group(session, current_user.user_id, group, rg_obj.repo_group_id)

            # matches https://github.com/{org}/{repo}/ or htts://github.com/{org}/{repo}
            elif Repo.parse_github_repo_url(url)[0]:
                org_name, repo_name = Repo.parse_github_repo_url(url)
                repo_git = f"https://github.com/{org_name}/{repo_name}"
                repo_obj = Repo.get_by_repo_git(session, repo_git)
                if repo_obj:
                    add_existing_repo_to_group(session, current_user.user_id, group, repo_obj.repo_id)

            # matches /{org}/{repo}/ or /{org}/{repo} or {org}/{repo}/ or {org}/{repo}
            elif (match := parse_org_and_repo_name(url)):
                org, repo = match.groups()
                repo_git = f"https://github.com/{org}/{repo}"
                repo_obj = Repo.get_by_repo_git(session, repo_git)
                if repo_obj:
                    add_existing_repo_to_group(session, current_user.user_id, group, repo_obj.repo_id)
            
            # matches /{org}/ or /{org} or {org}/ or {org}
            elif (match := parse_org_name(url)):
                org_name = match.group(1)
                rg_obj = RepoGroup.get_by_name(session, org_name)
                logger.info(rg_obj)
                if rg_obj:
                    # add the orgs repos to the group
                    add_existing_org_to_group(session, current_user.user_id, group, rg_obj.repo_group_id)

            # matches https://gitlab.com/{org}/{repo}/ or http://gitlab.com/{org}/{repo}
            elif Repo.parse_gitlab_repo_url(url)[0]:

                org_name, repo_name = Repo.parse_github_repo_url(url)
                repo_git = f"https://gitlab.com/{org_name}/{repo_name}"

                # TODO: gitlab ensure the whole repo git is inserted so it can be found here
                repo_obj = Repo.get_by_repo_git(session, repo_git)
                if repo_obj:
                    add_existing_repo_to_group(session, current_user.user_id, group, repo_obj.repo_id)
                
            else:
                invalid_urls.append(url)

    if urls:
        urls = [url.lower() for url in urls]
        add_org_repo_list.si(current_user.user_id, group, urls).apply_async()

    flash("Adding repos and orgs in the background")
            
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
