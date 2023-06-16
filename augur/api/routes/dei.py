"""
Creates routes for DEI badging functionality
"""

import logging
from flask import request, Response, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from augur.application.db.session import DatabaseSession
from augur.tasks.github.util.github_task_session import GithubTaskSession
from augur.util.repo_load_controller import RepoLoadController
from augur.api.util import api_key_required
from augur.api.util import ssl_required

from augur.application.db.models import User, ClientApplication, CollectionStatus, Repo, RepoGroup, BadgingDEI
from augur.application.config import get_development_flag
from augur.tasks.init.redis_connection import redis_connection as redis
from augur.tasks.github.util.util import get_repo_weight_by_issue
from augur.tasks.util.collection_util import start_block_of_repos, get_enabled_phase_names_from_config, core_task_success_util
from augur.tasks.start_tasks import prelim_phase, primary_repo_collect_phase
from ..server import app, engine

logger = logging.getLogger(__name__)
Session = sessionmaker(bind=engine, autocommit=True)

from augur.api.routes import AUGUR_API_VERSION
from augur.application.db.models.augur_operations import FRONTEND_REPO_GROUP_NAME

@app.route(f"/{AUGUR_API_VERSION}/dei/repo/add", methods=['POST'])
@ssl_required
@api_key_required
def dei_track_repo(application: ClientApplication):
    dei_id = request.args.get("id")
    level = request.args.get("level")
    repo_url = request.args.get("url")

    if not (dei_id and level and repo_url):
        return jsonify({"status": "Missing argument"}), 400
    
    session = Session()
    repo: Repo = session.query(Repo).filter(url=repo_url).first()
    if repo:
        # Making the assumption that only new repos will be added with this endpoint
        return jsonify({"status": "Repo already exists"})
    
    frontend_repo_group: RepoGroup = session.query(RepoGroup).filter(RepoGroup.rg_name == FRONTEND_REPO_GROUP_NAME).first()
    repo_id = Repo.insert(session, repo_url, frontend_repo_group.repo_group_id, "API.DEI")
    if not repo_id:
        return jsonify({"status": "Error adding repo"})
    
    repo = Repo.get_by_id(session, repo_id)
    repo_git = repo.repo_git
    pr_issue_count = get_repo_weight_by_issue(session.logger, repo_git)

    record = {
        "repo_id": repo_id,
        "issue_pr_sum": pr_issue_count,
        "core_weight": -9223372036854775808,
        "secondary_weight": -9223372036854775808
    }

    collection_status_unique = ["repo_id"]
    session.insert_data(record, CollectionStatus, collection_status_unique, on_conflict_update=False)

    record = {
        "badging_id": dei_id,
        "level": level,
        "repo_id": repo_id
    }

    enabled_phase_names = get_enabled_phase_names_from_config(session.logger, session)

    #Primary collection hook.
    primary_enabled_phases = []

    #Primary jobs
    if prelim_phase.__name__ in enabled_phase_names:
        primary_enabled_phases.append(prelim_phase)
    
    primary_enabled_phases.append(primary_repo_collect_phase)

    #task success is scheduled no matter what the config says.
    def core_task_success_util_gen(repo_git):
        return core_task_success_util.si(repo_git)
    
    primary_enabled_phases.append(core_task_success_util_gen)

    session.insert_data(record, BadgingDEI, on_conflict_update=False)
    start_block_of_repos(logger, session, [repo_id], primary_enabled_phases, "new")

    return jsonify({"status": "Success"})

@app.route(f"/{AUGUR_API_VERSION}/dei/report", methods=['POST'])
@ssl_required
@api_key_required
def dei_report(application: ClientApplication):
    dei_id = request.args.get("id")

    if not dei_id:
        return jsonify({"status": "Missing argument"}), 400
    
    # TODO what goes in the report?

    return jsonify({"status": "Endpoint not implemented"})