"""
Creates routes for DEI badging functionality
"""

import logging, subprocess

from flask import request, jsonify, render_template, send_file, current_app
from pathlib import Path

from augur.api.util import api_key_required, ssl_required

from augur.application.db.models import ClientApplication, CollectionStatus, Repo, RepoGroup, BadgingDEI
from augur.application.db.session import DatabaseSession

from augur.tasks.util.collection_util import CollectionRequest,AugurTaskRoutine, get_enabled_phase_names_from_config, core_task_success_util
from augur.tasks.start_tasks import prelim_phase, primary_repo_collect_phase
from augur.tasks.github.util.util import get_repo_weight_by_issue

from ..server import app

logger = logging.getLogger(__name__)

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
    
    repo_url = repo_url.lower()
    
    session = DatabaseSession(logger, engine=current_app.engine)
    session.autocommit = True
    repo: Repo = session.query(Repo).filter(Repo.repo_git==repo_url).first()
    if repo:
        # Making the assumption that only new repos will be added with this endpoint
        return jsonify({"status": "Repo already exists"})
    
    frontend_repo_group: RepoGroup = session.query(RepoGroup).filter(RepoGroup.rg_name == FRONTEND_REPO_GROUP_NAME).first()
    repo_id = Repo.insert_github_repo(session, repo_url, frontend_repo_group.repo_group_id, "API.DEI", repo_type="")
    if not repo_id:
        return jsonify({"status": "Error adding repo"})
    
    repo = Repo.get_by_id(session, repo_id)
    repo_git = repo.repo_git
    pr_issue_count = get_repo_weight_by_issue(logger, repo_git)

    record = {
        "repo_id": repo_id,
        "issue_pr_sum": pr_issue_count,
        "core_weight": -9223372036854775808,
        "secondary_weight": -9223372036854775808,
        "ml_weight": -9223372036854775808
    }

    collection_status_unique = ["repo_id"]
    session.insert_data(record, CollectionStatus, collection_status_unique, on_conflict_update=False)

    record = {
        "badging_id": dei_id,
        "level": level,
        "repo_id": repo_id
    }

    enabled_phase_names = get_enabled_phase_names_from_config()

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

    record = BadgingDEI(**record)
    session.add(record)
    
    deiHook = CollectionRequest("core",primary_enabled_phases)
    deiHook.repo_list = [repo_url]

    singleRoutine = AugurTaskRoutine(logger, session,[deiHook])
    singleRoutine.start_data_collection()
    #start_block_of_repos(logger, session, [repo_url], primary_enabled_phases, "new")

    session.close()

    return jsonify({"status": "Success"})

@app.route(f"/{AUGUR_API_VERSION}/dei/report", methods=['POST'])
@ssl_required
@api_key_required
def dei_report(application: ClientApplication):
    dei_id = request.args.get("id")

    if not dei_id:
        return jsonify({"status": "Missing argument"}), 400
    
    session = DatabaseSession(logger, engine=current_app.engine)

    project: BadgingDEI = session.query(BadgingDEI).filter(BadgingDEI.badging_id==dei_id).first()

    if not project:
        return jsonify({"status": "Invalid ID"})
    
    md = render_template("dei-badging-report.j2", project=project)
    cachePath = Path.cwd() / "augur" / "static" / "cache"

    source = cachePath / f"{project.id}_badging_report.md"
    report = cachePath / f"{project.id}_badging_report.pdf"
    source.write_text(md)

    command = f"mdpdf -o {str(report.resolve())} {str(source.resolve())}"
    converter = subprocess.Popen(command.split())
    converter.wait()
    
    # TODO what goes in the report?

    return send_file(report.resolve())