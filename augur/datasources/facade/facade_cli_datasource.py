#SPDX-License-Identifier: MIT
"""
Creates routes for the facade data source plugin
"""

from flask import Response, request, jsonify

def create_routes(server):

    facade = server._augur['facade']()

    @server.app.route('/{}/facade/cli_add_project'.format(server.api_version), methods=['POST'])
    def cli_add_project():
        name = request.args.get('name')
        description = request.args.get('description')
        website = request.args.get('website')      

        return jsonify(facade.cli_add_project(name, description, website))

    @server.app.route('/{}/facade/cli_delete_project/<project_id>'.format(server.api_version))
    def cli_delete_project():
        project_id = request.args.get('project_id')

        return jsonify(facade.cli_delete_project(project_id))

    @server.app.route('/{}/facade/cli_add_repo/'.format(server.api_version))
    def cli_add_repo():
        project_id = request.args.get('project_id')
        git_repo = request.args.get('git_repo')

        return jsonify(facade.cli_add_repo(project_id, git_repo))


    @server.app.route('/{}/facade/cli_delete_repo/<git_repo>'.format(server.api_version))
    def cli_delete_repo():
        git_repo = request.args.get('git_repo')

        return jsonify(facade.cli_delete_repo(git_repo))


    @server.app.route('/{}/facade/cli_add_alias'.format(server.api_version))
    def cli_add_alias():
        alias = request.args.get('alias')
        canonical = request.args.get('canonical')

        return jsonify(facade.cli_add_alias(alias, canonical))
    
    @server.app.route('/{}/facade/cli_delete_alias/<alias_id>'.format(server.api_version))
    def cli_delete_alias():
        alias_id = request.args.get('alias_id')

        return jsonify(facade.cli_delete_alias(alias_id))


    @server.app.route('/{}/facade/cli_add_affiliation'.format(server.api_version))
    def cli_add_affiliation():
        domain = request.args.get('domain')
        affiiliation = request.args.get('affiiliation')
        start_date = request.args.get('start_date')

        return jsonify(facade.cli_add_affiliation(domain, affiiliation, start_date))

    @server.app.route('/{}/facade/cli_delete_affiliation/<affiiliation_id>'.format(server.api_version))
    def cli_delete_affiliation():
        affiiliation_id = request.args.get('affiiliation_id')

        return jsonify(facade.cli_delete_affiliation(affiiliation_id))
        