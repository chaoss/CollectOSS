#SPDX-License-Identifier: MIT
"""
Creates routes for the facade data source plugin
"""

from flask import Response, request

def create_routes(server):

    facade = server._augur['facade']()

	@server.app.route('/{}/facade/cli_add_project'.format(server.api_version))
	def cli_add_project():
		name = request.args.get('name')
		description = request.args.get('description')
		website = request.args.get('website')
		
		data = server.transform(facade.cli_add_project, args=([]), name=name, kwargs=({'description': description, 'website': website}))
		
		return Response(response=data,
	                       status=200,
	                       mimetype="application/json")


	@server.app.route('/{}/facade/cli_delete_project/<project_id>'.format(server.api_version))
	def cli_delete_project():
		project_id=request.args.get('project_id')

		data = server.transform(facade.cli_delete_project, args=([]), kwargs=({'project_id': project_id}))

		return Response(response=data,
	                       status=200,
	                       mimetype="application/json")

	@server.app.route('/{}/facade/cli_add_repo/'.format(server.api_version))
	def cli_add_repo()
		project_id = request.args.get('project_id')
		git_repo = request.args.get('git_repo')

		data = server.transform(facade.cli_add_repo, args=([]), kwargs({'project_id': project_id, 'git_repo': git_repo}))

		return Response(response=data,
	                       status=200,
	                       mimetype="application/json")


	@server.app.route('/{}/facade/cli_delete_repo/<git_repo>'.format(server.api_version))
	def cli_delete_repo():
		git_repo = request.args.get('git_repo')

		data = server.transform(facade.cli_delete_repo, args([]), kwargs({'git_repo': git_repo}))

		return Response(response=data,
	                       status=200,
	                       mimetype="application/json")


	@server.app.route('/{}/facade/cli_add_alias'.format(server.api_version))
	def cli_add_alias():
		alias = request.args.get('alias')
		canonical = request.args.get('canonical')

		data = server.transform(facade.cli_add_alias, args([]), kwargs({'alias': alias, 'canonical': canonical}))
		
		return Response(response=data,
	                       status=200,
	                       mimetype="application/json")


	@server.app.route('/{}/facade/cli_delete_alias/<alias_id>'.format(server.api_version))
	def cli_delete_alias():
			alias_id = request.args.get('alias_id')

			data = server.transform(facade.cli_delete_alias, args([]), kwargs({'alias_id': alias_id}))

			return Response(response=data,
	                       status=200,
	                       mimetype="application/json")


	@server.app.route('/{}/facade/cli_add_affiliation'.format(server.api_version))
	def cli_add_affiliation():
		domain = request.args.get('domain')
		affiiliation = request.args.get('affiiliation')
		start_date = request.args.get('start_date')

		data = server.transform(facade.cli_add_affiliation, args([]), kwargs({'domain': domain, 'affiiliation': affiiliation, 'start_date': start_date}))


		return Response(response=data,
	                   status=200,
	                   mimetype="application/json")

	@server.app.route('/{}/facade/cli_delete_affiliation/<affiiliation_id>'.format(server.api_version))
	def cli_delete_affiliation():
		affiiliation_id = request.args.get('affiiliation_id')

		data = server.transform(facade.cli_delete_affiliation, args([]), kwargs({'affiiliation_id': affiiliation_id}))

		return Response(response=data,
	                   status=200,
	                   mimetype="application/json")

    
