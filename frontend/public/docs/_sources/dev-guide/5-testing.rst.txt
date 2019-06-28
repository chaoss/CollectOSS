Testing
====================================

To test augur, set up your environment for testing:

.. code:: bash

    export DB_TEST_URL=mysql+pymysql://<username>:<pass>@<host>:<post>/<database>

After that, run ``make test`` to run the plugin/data source unit tests and the Python API tests.

To run the Python data source unit tests alone: ``make test-functions``.
To run the Python API tests alone: ``make test-routes``.

For both these plugins, you can specify a single plugin for which to run the designated tests. You can do this
like so: ``make test-routes PLUGIN=<plugin_name>``. The plugin name should exactly match the name of the plugin directory.

Metrics
*********
Augur uses ``pytest`` for its data source unit tests. The tests for our sample ``Chaoss``
class are contained in the ``test_chaoss_functions.py`` file inside the plugin's
directory. You can use pytest fixtures and environment variables to pass
data to tests.

.. code:: python

    @pytest.fixture
    def chaoss():
        import augur
        chaoss = os.getenv("PLUGIN_TEST_URL")
        assert chaoss is not None and len(chaoss) > 8
        return augur.Chaoss(chaoss)

Now any test that tests functions in the Chaoss class will be able to
access an instance of the class.

.. code:: python

    def test_data_source(chaoss):
        assert chaoss.data_source('argument').isin(['expected_value']).any

Make sure every function you write has a test.


Endpoints
**********

As with our unit tests, we write our API tests in Python using the ``pytest`` framework.

API tests for a plugin live in the ``test_<plugin_name>_routes.py`` folder in the ``<plugin_name>/`` directory.
In this file, you'll need the following boilerplate:

.. code:: python

    import pytest
    import requests

    @pytest.fixture(scope="module")
    def <plugin_name>_routes():
        pass

The web server will be automatically spun up and down when running your tests.

For the actual tests, for the most part not much logic is needed. Each endpoint should already have a unit test asserting that the 
metric is being calculate correctly: in most cases the endpoint tests exist primarily to make sure they're reachable and that the routes
we've documented are correct. These unit tests should not be strictly re-implemented, but each test needs to make sure that the output of the
corresponding metric is correct: since most endpoints are nothing more than a wrapper this usually means the test will just mirror the test cases of the corresponding unit test.

In some cases, endpoints will provide additional functionality beyond just the metric they're mapped to
(e.g. aggregation and filtering), and in these scenarios test cases are needed to cover these capabilities.

Let's look at a sample test:

.. code:: python

    def test_api_status(metrics_status):
        response = requests.get('http://localhost:5000/api/unstable').json()
        assert response['status'] == 'OK'
        assert response.status_code == 200


This is just making sure that the API is up and running by parsing the response from the ``/api/unstable``
health check endpoint. In this case simply checking the status code and that the response is not empty/has some data in it
is all that's really needed. If this were a metric endpoint, an appropriate assertion might be something like
``assert response[0]['commits'] = 20``.
