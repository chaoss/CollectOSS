#SPDX-License-Identifier: MIT
"""
Creates routes for the metrics status plugin
"""

import json
from flask import Response, request
from .metrics_status import Metric

def filter_by(status, key, value):
    if value == "all" or value == '' or value is None:
        return status
    if value is not None:
        return [metric for metric in status if (metric[key] or 'none').lower() == value.lower()]

def create_routes(server):

    metrics_status = server._augur['metrics_status']()

    metrics_status_url = "metrics/status"

    """
    @api {get} metrics/status Metrics Status
    @apiName metrics-status 
    @apiGroup Metrics-Status
    @apiDescription Information about the Augur implementation status of CHAOSS metrics.

    @apiSuccessExample {json} Success-Response:
                    [
                         {  
                            "tag":"committers",
                            "group":"wg-risk",
                            "name":"Committers",
                            "backend_status":"implemented",
                            "frontend_status":"unimplemented",
                            "endpoint_repo":"/api/unstable/repo-groups/<repo_group_id>/repos/<repo_id>/committers",
                            "endpoint_rg":"/api/unstable/repo-groups/<repo_group_id>/committers",
                            "source":"augur_db",
                            "metric_type":"metric",
                            "is_defined":true,
                            "working_group":"wg-risk"
                        },
                        {  
                            "tag":"pull-requests-merged",
                            "group":"wg-evolution",
                            "name":"Pull Requests Merged",
                            "backend_status":"unimplemented",
                            "frontend_status":"unimplemented",
                            "endpoint_repo":null,
                            "endpoint_rg":null,
                            "source":null,
                            "metric_type":null,
                            "is_defined":false,
                            "working_group":"wg-evolution"
                        }
                    ]
    """
    @server.app.route("/{}/{}".format(server.api_version, metrics_status_url))
    def metrics_status_view():
        return Response(response=(metrics_status.get_metrics_status().to_json(orient='records')),
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
                            "groups":{  
                            "evolution":"Evolution",
                            "diversity-inclusion":"Diversity and Inclusion metrics",
                            "value":"Value",
                            "risk":"Risk",
                            "common":"Common",
                            "experimental":"Experimental",
                            "all":"All"
                        },
                        "data_sources":[  
                            "githubapi",
                            "librariesio",
                            "ghtorrent",
                            "downloads",
                            "facade",
                            "augur_db"
                        ],
                        "metric_types":[  
                            "timeseries",
                            "git",
                            "metric"
                        ],
                        "tags":[  
                            "\"alternative-packages\"",
                            "\"organizations\"",
                            "\"contribution-type\"",
                                ...
                            }
                        }
                    ]
    """
    @server.app.route("/{}/{}/metadata".format(server.api_version, metrics_status_url))
    def metrics_status_metadata_view():
        return Response(response=json.dumps(metrics_status.get_metrics_metadata()),
                        status=200,
                        mimetype="application/json")

    """
    @api {get} metrics/status/filter?ID=:ID&tag=:tag&group=:group&backend_status=:backend_status&frontend_status=:frontend_status&source=:source&metric_type=:metric_type&is_defined=:is_defined Filtered Metrics Status 
    @apiName filter-metrics-status
    @apiGroup Metrics-Status
    @apiDescription Metrics Status that allows for filtering of the results via the query string. Filters can be combined.

    @apiParam {string} [tag] Returns all the statuses of all metrics that have this tag
    @apiParam {string} [group] Returns all the metrics in this metric grouping
    @apiParam {string="unimplemented", "undefined", "implemented"} [backend_status]
    @apiParam {string="unimplemented", "implemented"} [frontend_status]
    @apiParam {string} [source] Returns the statuses of all metrics from this data source
    @apiParam {string} [metric_type] Returns the statuses of the metrics of this metric type
    @apiParam {string="true", "false"} [is_defined] Returns the statuses of metrics that are or aren't defined

    @apiParamExample {string} Sample Query String: 
    metrics/status/filter?group=evolution&metric_type=metric
                    

    @apiSuccessExample {json} Success-Response:
                    [  
                        {  
                            "tag":"reviews-duration",
                            "group":"evolution",
                            "name":"Reviews_Duration",
                            "backend_status":"unimplemented",
                            "frontend_status":"unimplemented",
                            "endpoint_repo":null,
                            "endpoint_rg":null,
                            "source":null,
                            "metric_type":null,
                            "is_defined":true,
                            "working_group":"evolution"
                        },
                        {  
                            "tag":"pull-requests-merged",
                            "group":"evolution",
                            "name":"Pull Requests Merged",
                            "backend_status":"unimplemented",
                            "frontend_status":"unimplemented",
                            "endpoint_repo":null,
                            "endpoint_rg":null,
                            "source":null,
                            "metric_type":null,
                            "is_defined":false,
                            "working_group":"evolution"
                        }
                    ]
    """
    @server.app.route("/{}/{}/filter".format(server.api_version, metrics_status_url))
    def filtered_metrics_status_view():

        filtered_metrics_status = metrics_status.get_metrics_status().to_dict('records')

        valid_filters = [key for key in Metric().__dict__ if key not in ('name', 'url')]

        for valid_filter in valid_filters:
            filtered_metrics_status = filter_by(filtered_metrics_status, valid_filter, request.args.get(valid_filter))

        return Response(response=json.dumps(filtered_metrics_status),
                        status=200,
                        mimetype="application/json")
