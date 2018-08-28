from flask import Response, request
from augur.metrics_status import Metric
import json

def filterBy(status, key, value):
	if value == "all" or value == '' or value is None:
		return status
	elif value is not None:
		return [metric for metric in status if metric[key].lower() == value.lower()]

def create_routes(server):

	metrics_status = server.augur_app.metrics_status()
	metrics_status.create_metrics_status()
	metrics_status_URL = "metrics/status"

	"""
	@api {get} metrics/status Metrics Status
	@apiName metrics-status 
	@apiGroup Metrics-Status
	@apiDescription Information about the Augur implementation status of CHAOSS metrics.

	@apiSuccessExample {json} Success-Response:
	                [
	                	{
	                    
	                        "ID": "ghtorrent-fakes",
	                        "tag": "fakes",
	                        "name": "Fakes",
	                        "group": "experimental",
	                        "backend_status": "implemented",
	                        "frontend_status": "implemented",
	                        "endpoint": "/api/unstable/<owner>/<repo>/timeseries/fakes",
	                        "source": "ghtorrent",
	                        "metric_type": "timeseries",
	                        "url": "/",
	                        "is_defined": "false"
	                    },
	                    {
	                        "ID": "ghtorrentplus-closed-issue-resolution-duration",
	                        "tag": "closed-issue-resolution-duration",
	                        "name": "Closed Issue Resolution Duration",
	                        "group": "experimental",
	                        "backend_status": "implemented",
	                        "frontend_status": "unimplemented",
	                        "endpoint": "/api/unstable/<owner>/<repo>/issues/time_to_close",
	                        "source": "ghtorrentplus",
	                        "metric_type": "metric",
	                        "url": "activity-metrics/closed-issue-resolution-duration.md",
	                        "is_defined": "true"
	                    },
	                    {
	                        "ID": "githubapi-lines-of-code-changed",
	                        "tag": "lines-of-code-changed",
	                        "name": "Lines Of Code Changed",
	                        "group": "experimental",
	                        "backend_status": "implemented",
	                        "frontend_status": "implemented",
	                        "endpoint": "/api/unstable/<owner>/<repo>/timeseries/lines_changed",
	                        "source": "githubapi",
	                        "metric_type": "timeseries",
	                        "url": "activity-metrics/lines-of-code-changed.md",
	                        "is_defined": "true"
	                    }
	                ]
	"""
	@server.app.route("/{}/{}".format(server.api_version, metrics_status_URL))
	def metrics_status_view():
		return Response(response=json.dumps(metrics_status.raw_metrics_status),
						status=200,
						mimetype="application/json")

	"""
	@api {get} metrics/status/metadata Metrics Status Metadata
	@apiName metrics-status-metadata
	@apiGroup Metrics-Status
	@apiDescription Metadata about the Augur implemntation status of CHAOSS metrics.

	@apiSuccessExample {json} Success-Response:
	                [
	                	{
	                    	"groups": [
	                            {
	                                "diversity-inclusion": "Diversity and Inclusion",
	                                "growth-maturity-decline": "Growth, Maturity, and Decline",
	                                "risk": "Risk",
	                                "value": "Value",
	                                "activity": "Activity",
	                                "experimental": "Experimental"
	                            }
	                        ],
	                        "sources": [
	                            "ghtorrent",
	                            "ghtorrentplus",
	                            "githubapi",
	                            "downloads",
	                            "facade",
	                            "publicwww",
	                            "librariesio",
	                            "git"
	                        ],
	                        "metric_types": [
	                            "timeseries",
	                            "metric",
	                            "git"
	                        ],
	                        "tags": {
	                            "listening": "diversity-inclusion",
	                            "speaking": "diversity-inclusion",
	                            ...
	                        }
	                	}
	                ]
	"""
	@server.app.route("/{}/{}/metadata".format(server.api_version, metrics_status_URL))
	def metrics_status_metadata_view():
		return Response(response=json.dumps(metrics_status.metadata),
						status=200,
						mimetype="application/json")

	"""
	@api {get} metrics/status/filter?ID=:ID&tag=:tag&group=:group&backend_status=:backend_status&frontend_status=:frontend_status&source=:source&metric_type=:metric_type&is_defined=:is_defined Filtered Metrics Status 
	@apiName filter-metrics-status
	@apiGroup Metrics-Status
	@apiDescription Metrics Status that allows for filtering of the results via the query string. Filters can be combined.

	@apiParam {string} [ID] Returns the status of the metric that matches this ID
	@apiParam {string} [tag] Returns all the statuses of all metrics that have this tag
	@apiParam {string} [group] Returns all the metrics in this metric grouping
	@apiParam {string="unimplemented", "undefined", "implemented"} [backend_status]
	@apiParam {string="unimplemented", "implemented"} [frontend_status]
	@apiParam {string} [source] Returns the statuses of all metrics from this data source
	@apiParam {string} [metric_type] Returns the statuses of the metrics of this metric type
	@apiParam {string="true", "false"} [is_defined] Returns the statuses of metrics that are or aren't defined

	@apiParamExample {string} Sample Query String: 
	metrics/status/filter?group=growth-maturity-decline&metric_type=metric
					

	@apiSuccessExample {json} Success-Response:
	                [
	                    {
	                        "ID": "ghtorrentplus-closed-issue-resolution-duration",
	                        "tag": "closed-issue-resolution-duration",
	                        "name": "Closed Issue Resolution Duration",
	                        "group": "growth-maturity-decline",
	                        "backend_status": "implemented",
	                        "frontend_status": "unimplemented",
	                        "endpoint": "/api/unstable/<owner>/<repo>/issues/time_to_close",
	                        "source": "ghtorrentplus",
	                        "metric_type": "metric",
	                        "url": "activity-metrics/closed-issue-resolution-duration.md",
	                        "is_defined": "true"
	                    },
	                    {
	                        "ID": "ghtorrent-contributors",
	                        "tag": "contributors",
	                        "name": "Contributors",
	                        "group": "growth-maturity-decline",
	                        "backend_status": "implemented",
	                        "frontend_status": "implemented",
	                        "endpoint": "/api/unstable/<owner>/<repo>/contributors",
	                        "source": "ghtorrent",
	                        "metric_type": "metric",
	                        "url": "activity-metrics/contributors.md",
	                        "is_defined": "true"
	                    }
	                ]
	"""
	@server.app.route("/{}/{}/filter".format(server.api_version, metrics_status_URL))
	def filtered_metrics_status_view():

		filtered_metrics_status = metrics_status.raw_metrics_status

		valid_filters = [key for key in Metric().__dict__.keys() if key != 'name' and key != 'endpoint' and key != 'url']

		for valid_filter in valid_filters:
			filtered_metrics_status = filterBy(filtered_metrics_status, valid_filter, request.args.get(valid_filter))

		return Response(response=json.dumps(filtered_metrics_status),
						status=200,
						mimetype="application/json")
