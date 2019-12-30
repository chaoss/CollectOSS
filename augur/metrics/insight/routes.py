#SPDX-License-Identifier: MIT

def create_insight_routes(server):

    metrics = server._augur.metrics

    """
    @api {get} /top-insights Top Insights
    @apiName top-insights
    @apiGroup Utility
    @apiDescription Get all the downloaded repo groups.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "rg_name": "Rails",
                            "rg_description": "Rails Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:25.000Z"
                        },
                        {
                            "repo_group_id": 23,
                            "rg_name": "Netflix",
                            "rg_description": "Netflix Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:36.000Z"
                        }
                    ]
    """
    server.addRepoGroupMetric(metrics.top_insights, 'top-insights')
