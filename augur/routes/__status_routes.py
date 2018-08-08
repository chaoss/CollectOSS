from flask import Response
import json

def create_routes(server):

	metrics_status = server.augur_app.metrics_status()
	metrics_status.create_metrics_status()
	all_metrics_status_response = metrics_status.getAllMetricsStatus()

	@server.app.route("/{}/metrics/status".format(server.api_version))
	def all_metrics_status():
		return Response(response=json.dumps(all_metrics_status_response),
						status=200,
						mimetype="application/json")

	@server.app.route("/{}/metrics/status/<ID>/".format(server.api_version))
	def individual_metrics_status(ID):

		individual_metrics_status = next((metric for metric in all_metrics_status_response if metric['ID'] == ID), None)

		return Response(response=json.dumps(individual_metrics_status),
						status=200,
						mimetype="application/json")
