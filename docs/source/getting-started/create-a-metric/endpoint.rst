--------------------------------------
Create a Metric Endpoint
--------------------------------------

.. note::

  In this context "route" and "endpoint" both refer to a full endpoint exposed through our REST API.

After implementing the metric function, you must define an API endpoint to be able access the metric remotely. 

Routes for the metrics are defined in the ``routes.py`` file in the ``augur/metrics/<model>/`` directory, where ``<model>`` is the same model in which the metric is implemented.

``repo``/``repo_group`` endpoints
---------------------------------

Augur provides two helper methods for defining ``repo``/``repo_group`` metrics.

For the ``repo_group`` form of a metric, use ``server.addRepoGroupMetric(metrics.<metric>, '<endpoint>')``. This will create the endpoint ``/repo-groups/:repo_group_id/<endpoint>`` which exposes the ``<metric>`` metric function.

Example:

  .. code-block:: python

    # this line will add the endpoint /repo-groups/:repo_group_id/issues-new, which exposes the issues_new function we wrote in the previous section
    # the given :repo_group_id will automatically be passed to the issues_new function 
    server.addRepoGroupMetric(metrics.issues_new, 'issues-new')


For the ``repo`` form of a metric, use ``server.addRepoMetric(metrics.<metric>, '<endpoint>')``. This will create the endpoint ``/repos/:repo_id/<endpoint>`` which exposes the ``<metric>`` metric function.

Example:

  .. code-block:: python

    # this line will add the endpoint /repos/:repo_id/issues-new, which exposes the issues_new function we wrote in the previous section
    # the given :repo_group_id and :repo_id will automatically be passed to the issues_new function 
    server.addRepoMetric(metrics.issues_new, 'issues-new')

Other endpoints
----------------

Metrics which are not ``repo``/``repo_group`` metrics must define the routes manually. Let's first look at a template, then we'll see an example.

  .. code-block:: python
    :linenos:

    @server.app.route('/{}/<route_parameter>/metric_name'.format(server.api_version))
    def metric_name(route_parameter):
        response = server.transform(metrics.metric, args=[route_parameter])
        return Response(response=response, status=200, mimetype="application/json")

Let's break it down line by line:

  .. code-block:: python
    :lineno-start: 1

    @server.app.route('/{}/<route_parameter>/metric_name'.format(server.api_version))

This line adds the endpoint in the Flask app located on Augur's server. You must provide a valid, unique route, and it *must* start with ``server.api_version``.
You can also specify route parameters with angle brackets (``<`` and ``>``) in their corresponding place in the route. These will be automatically passed to the view function defined on the next line.

For example, if the ``server.api_version`` was ``api/unstable``, and if our ``metric_name`` was ``issues_new`` and our ``route_parameter`` name was ``repo_id``, we could add the route like so\:

  .. code-block:: python

    @server.app.route('/{}/<repo_id>/issues_new'.format(server.api_version))

An example of a call to this endpoint would look something like ``<server>/api/unstable/20/issues_new``.

To define the route's behavior\:

  .. code-block:: python
    :lineno-start: 2

    def metric_name(route_parameter):

This line defines the view function associated with the route defined on the previous line: whenever that route is hit, this is the function that will execute. It will accept as arguments all route parameters
specified on the line above.

.. note::

  No matter what model it is defined in, each view function name **must** be unique.

Now, to execute the metric function\:

  .. code-block:: python
    :lineno-start: 3

    response = server.transform(metrics.metric, args=[route_parameter])

This line takes the given metric (``metrics.metric``) function and the desired arguments to said function and passes them to ``server.transform``.
This is a helper function that takes the DataFrame returned by the metric function and transforms it into a JSON object.

  .. code-block:: python
    :lineno-start: 4

    return Response(response=response, status=200, mimetype="application/json")

The final line returns a Flask response object, which contains the body of the response (the ``response`` variable from the line above), and sets 2 headers: one for the status code (``200``, indicating success) and the ``mimetype`` which lets the calling program know what kind of response to expect when parsing the body (in this case, ``application/json``).
All endpoints should return a ``200`` status code and ``application/json`` as their ``mimetype``.

.. note::

  The helper functions defined in the previous section are just wrappers for this process of manually creating endpoints.

Documentation
-------------

All API endpoints must be documented. We use `apidocjs <http://apidocjs.com>`_ for our API documentation.
The following parameters are required:

- ``@api``
- ``@apiName``
- ``@apiGroup``
- ``@apiDescription``
- ``@apiParam`` (as many as there are route parameters)
- ``@apiSuccessExample``

Please refer to their `documentation <http://apidocjs.com/#params>`_ for specific and in-depth descriptions for each one of these. However, in most cases will probably suffice to just adapt the format of an already existing endpoint.

For our ``issues_new`` metric the documentation would look something like this:

  .. code-block:: python
    :linenos:

    """
    @api {get} /repo-groups/:repo_group_id/issues-new Issues New (Repo Group)
    @apiName issues-new-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of new issues opened during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 318
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2009-01-01T00:00:00.000Z",
                            "issues": 1
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2010-01-01T00:00:00.000Z",
                            "issues": 7
                        }
                    ]
    """
    # actual route definition goes here

.. note:: 

  The documentation must come *before* the creation of the route.

Congratulations! You've successfully implemented your first Augur metric!
