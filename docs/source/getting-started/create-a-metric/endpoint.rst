--------------------------------------
Create a Metric Endpoint
--------------------------------------

2. **Adding Routes**

After implementing the metric, you must add an API endpoint to access the metric remotely. Routes for the metrics are added in the ``routes.py`` file in the ``augur/metrics/<model>/<model>.py`` directory.
In the ``create_routes`` function in ``routes.py`` file you can add routes using the following two methods:

``server.addRepoGroupMetric(metrics.<metric>, '<endpoint>')`` to add the endpoint ``/repo-groups/:repo_group_id/<endpoint>`` corresponding to the metric implementation function ``<metric>``.
``server.addRepoMetric(metrics.<metric>, '<endpoint>')`` to add the endpoint ``/repo-groups/:repo_group_id/repos/:repo_id/<endpoint>`` corresponding to the metric implementation function ``<metric>``

Consider the following example:

  .. code-block:: python
    :linenos:

      """
      @api {get} /repo-groups/:repo_group_id/code-changes
      @apiName Code Changes
      @apiGroup Evolution
      @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
      @apiParam {String} repo_group_id Repository Group ID
      @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
      @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
      @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
      @apiSuccessExample {json} Success-Response:
                      [
                          {
                              "commit_date": "2018-01-01T00:00:00.000Z",
                              "repo_id": 1,
                              "commit_count": 5140
                          },
                          {
                              "commit_date": "2019-01-01T00:00:00.000Z",
                              "repo_id": 1,
                              "commit_count": 711
                          },
                          {
                              "commit_date": "2015-01-01T00:00:00.000Z",
                              "repo_id": 25001,
                              "commit_count": 1071
                          }
                      ]
      """
      server.addRepoGroupMetric(metrics.code_changes, 'code-changes')


The last line ``server.addRepoGroupMetric(metrics.code_changes, 'code-changes')`` is what actually creates the ``/repo-groups/:repo_group_id/code-changes`` endpoint and links it to ``code_changes`` metric implementation function.
The rest is just annotation used to create documentation.

After you've completed these two steps, run ``make dev`` in the root of your directory and navigate to ``https:localhost:<port>api/unstable/repo-groups/:repo_group_id/code-changes`` where ``<port>`` is the port of backend is running on (default ``5000``) and ``repo_group_id`` is the ID of the repo group about which you wish to learn.

