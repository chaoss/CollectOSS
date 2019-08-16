import json
from flask import Flask, request, Response, send_from_directory, redirect, flash, jsonify
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email
from ..models import User, Repo, RepoGroup


class RepoForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])
    vcs = PasswordField('vcs')

class RepoGroupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])



def create_repo_routes(server):

    @server.app.route('/{}/repo_group'.format(server.api_version), methods=['POST', 'GET'])
    def repo_groups():
        if request.method == 'GET':
            all_repo_groups = RepoGroup.query.all()
            return jsonify([{'repo_group_id': grp.id, 'name': grp.name} for grp in all_repo_groups])
        elif request.method == 'POST':
            form = RepoGroupForm(request.form)
            if form.validate():
                repogroup = RepoGroup(name=form.name.data)
                server._augur.session.add(repogroup)
                server._augur.session.commit()
                jsn = {'repo_group_id': repogroup.id}
                return jsonify(jsn)



    @server.app.route('/{}/repo_group/:repo_group_id/repos'.format(server.api_version), methods=['GET', 'PUT', 'POST'])
    def repo_group_repos(repo_group_id):
        repo_group = RepoGroup.query.filter_by(id=repo_group_id).first()
        if not repo_group:
            return Response(response={'error': f'Repo group {repo_group_id} does not exist'},
                            status=404,
                            mimetype="application/json")
        
        if request.method == 'PUT':
            # TODO: make sure random users can't do this
            form = RepoForm(request.form)
            if form.validate():
                repo = Repo.query.filter_by(url=form.url.data).all()
                repo_group.projects.append(repo)
                server._augur.session.commit()

        if request.method == 'POST':
            # TODO: make sure random users can't do this
            form = RepoForm(request.form)
            if form.validate():
                repo = Repo(url=form.url.data)
                repo_group.projects.append(Repo)
                server._augur.session.commit()

        json = [{'url': p.url, 'vcs': p.vcs} for p in repo_group.projects]
        return Response(response=json,
                        status=200,
                        mimetype="application/json")



    @server.app.route('/{}/repo'.format(server.api_version), methods=['POST', 'GET'])
    def repos():
        if request.method == 'GET':
            all_repos = Repo.query.all()
            all_repos = [{'url': r.url, 'vcs': r.vcs} for r in all_repos]
            return jsonify(all_repos)
        elif request.method == 'POST':
            form = RepoForm(request.form)
            if form.validate():
                repo = Repo(url=form.url.data, vcs=form.vcs.data)
                server._augur.session.add(repo)
                server._augur.session.commit()
                return jsonify({'repo_url': repo})

    @server.app.route('/{}/repo/:repoid'.format(server.api_version), methods=['GET', 'PUT', 'DELETE'])
    @login_required
    def repo():
        pass