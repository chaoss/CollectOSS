from flask import Response, request
from augur.metrics_status import Metric
import json

def filterBy(status, key, value):
	if value is not None:
		return [metric for metric in status if metric[key].lower() == value.lower()]
	else:
		return status

def create_routes(server):

	metrics_status = server.augur_app.metrics_status()
	metrics_status.create_metrics_status()
	metrics_status_URL = "metrics/status"

	@server.app.route("/{}/{}".format(server.api_version, metrics_status_URL))
	def metrics_status_view():

		response = metrics_status.raw_metrics_status

		if request.args.get('metadata') is not None:
			if request.args.get('metadata').lower() == 'true':
				response = metrics_status.metrics_status_with_metadata

		return Response(response=json.dumps(response),
						status=200,
						mimetype="application/json")

	@server.app.route("/{}/{}/filter".format(server.api_version, metrics_status_URL))
	def filtered_metrics_status_view():

		filtered_metrics_status = metrics_status.raw_metrics_status

		valid_filters = [key for key in Metric().__dict__.keys() if key != 'name' and key != 'endpoint' and key != 'url']

		for valid_filter in valid_filters:
			filtered_metrics_status = filterBy(filtered_metrics_status, valid_filter, request.args.get(valid_filter))

		return Response(response=json.dumps(filtered_metrics_status),
						status=200,
						mimetype="application/json")
