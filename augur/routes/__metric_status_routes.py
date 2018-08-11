from flask import Response, request
import json

def filterBy(status, key, value):
	return [metric for metric in status if metric[key] == value.lower()]

def create_routes(server):

	metrics_status = server.augur_app.metrics_status()
	metrics_status.create_metrics_status()
	metrics_status_URL = "metrics/status"

	@server.app.route("/{}/{}".format(server.api_version, metrics_status_URL))
	def metrics_status_view():
		return Response(response=json.dumps(metrics_status.getMetricsStatus()),
						status=200,
						mimetype="application/json")

	@server.app.route("/{}/{}/raw".format(server.api_version, metrics_status_URL))
	def raw_metrics_status_view():
		return Response(response=json.dumps(metrics_status.raw_metrics_status),
						status=200,
						mimetype="application/json")

	@server.app.route("/{}/{}/filter".format(server.api_version, metrics_status_URL))
	def filtered_metrics_status():

		filtered_metrics_status = metrics_status.all_metrics_status

		group = request.args.get('group')
		source = request.args.get('source')
		metric_type = request.args.get('metric_type')
		frontend_status = request.args.get('frontend_status')
		backend_status = request.args.get('backend_status')

		if group is not None:
			filtered_metrics_status = filterBy(filtered_metrics_status, "group", group.lower())
		if source is not None:
			filtered_metrics_status = filterBy(filtered_metrics_status, "source", source.lower())
		if  metric_type is not None:
			filtered_metrics_status = filterBy(filtered_metrics_status, "metric_type", metric_type.lower())
		if  frontend_status is not None:
			filtered_metrics_status = filterBy(filtered_metrics_status, "frontend_status", frontend_status.lower())
		if  backend_status is not None:
			filtered_metrics_status = filterBy(filtered_metrics_status, "backend_status", backend_status.lower())

		return Response(response=json.dumps(filtered_metrics_status),
						status=200,
						mimetype="application/json")

	@server.app.route("/{}/{}/<ID>/".format(server.api_version, metrics_status_URL))
	def individual_metrics_status(ID):

		individual_metrics_status = next((metric for metric in metrics_status.all_metrics_status if metric['ID'] == ID), None)

		return Response(response=json.dumps(individual_metrics_status),
						status=200,
						mimetype="application/json")