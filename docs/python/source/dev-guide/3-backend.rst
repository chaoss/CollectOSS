Backend
=============================================

Structure of the Backend
------------------------

Augur utilizes a plugin architecture. Plugins can be found in two
directories: ``plugins/`` and ``datasources/``. ``plugins/`` is for
generic plugins, while ``datasources/`` is specifically for plugins that
provide a new datsource, like ``ghtorrent`` or ``facade``.

Inside each plugin directory are 4 required files: ``__init__.py``
``plugin_name.py`` ``routes.py`` ``test_plugin_name.py``

We will go over these more in-depth in the following sections.

Setting up your environment
---------------------------

Before you begin, make sure to activate the augur Anaconda environment
by running ``conda activate augur``. If this environment doesn't exist,
try running ``make install-dev`` again and watch out for any errors.

Writing a Plugin
----------------

In this section, we'll walk through the process of creating a sample
data source plugin called ``Chaoss`` from beginning to end.

Setting up a plugin
~~~~~~~~~~~~~~~~~~~

``__init__.py`` contains the plugin class, any code that is needed to
initialize the datasource, plugin metadata, and the code needed to
register the plugin. ``__init__.py`` must also contain a
``create_routes`` function that takes in a ``flask_app``, which is
responsible for adding the plugin's data source routes to the API.

The ``ChaossPlugin`` class will implement the ``AugurPlugin`` class. Be
sure to include any imports your plugin might need for initialization,
as well as your plugin's license. Your class definiton should look
something like this:

.. code:: python

    #SPDX-License-Identifier: MIT 
    from augur.application import Application
    from augur.augurplugin import AugurPlugin
    from augur import logger

    class ChaossPlugin(AugurPlugin):
        # plugin goes here

The ``__init__`` function will look like this:

.. code:: python

        def __init__(self, augur):
            self.__chaoss = None
            # _augur will be set by the super init
            super().__init__(augur)

Code needed for initialization should be in the ``__call__`` function
like so:

.. code:: python

    def __call__(self):
        from .chaoss import Chaoss
        if self.__chaoss is None:
            logger.debug('Initializing Chaoss')
            self.__chaoss = Chaoss(
                config_value=self._augur.read_config('config_section', 'config_key', 'environment_value', 'default_value'),
            )
        return self.__chaoss

To create a plugin's routes:

.. code:: python

        def create_routes(self, flask_app):
            from .routes import create_routes
            create_routes(flask_app)

To set a plugin's metadata:

.. code:: python

    chaoss.augur_plugin_meta = {
        'name': 'chaoss',
        'datasource': True # include this line if it's a data source
        # include any other metadata you wish to, i.e. the author or a short description
    }

And to register the plugin:

.. code:: python

    Application.register_plugin(chaoss)

For a good example, see the ``__init__.py`` file of the ``ghtorrent``
plugin
`here <https://github.com/chaoss/augur/blob/dev/augur/datasources/ghtorrent/__init__.py>`__:

--------------

Defining a plugin's functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``chaoss.py`` contains the plugin's functionality, i.e. the plugin's
metrics, if it's a data source.

This file should contain the ``Chaoss`` class, which will define your
plugin's functionality (however it needs to do so).

For our sample plugin, we'll define a trivial metric. Each metric
function should return a pandas DataFrame, which will later be
serialized into JSON.

.. code:: python

    import pandas as pd

    class Chaoss(object):

        # sample "metric"
        def hello_world(self, owner, repo):
            data = {"hello": [owner], "world": [repo]}
            return pd.DataFrame.from_dict(data)

Annotation
          

If a function is a new metric that will have an endpoint, it needs to be
annotated so that its metadata is updated. Right above the function
definition, call the ``@annotate`` decorator as follows:

.. code:: python

    @annotate(metric_name='hello-world')
    def hello_world(self, owner, repo):

It is currently standard practice to pass in the ``tag``, which should
the same as the function name with dashes filling the whitespace between
words.

Later on, when you add the endpoint to ``routes.py``, more metadata will
be automatically generated for you. For metrics, Augur automatically
generates: - ``ID``, which is a concatentation of the metric's ``tag``
and it's ``source`` - ``display_name``, which is the name used when
displaying the metric - ``group``, which CHAOSS metrics category it
belongs to - ``endpoint``, which is the endpoint URL - ``data_source``,
which is the name of the metric's data source - ``metric_type``,
indicating what classification of metric it is (``metric``,
``timeseries``, or ``git``) - ``documentation_url``, which is a link to
a CHAOSS-defined metric’s documentation page (if it exists) -
``backend_status``, indicating backend implementation status -
``frontend_status``, indicating frontend implementation status

Documentation
             

When writing a new Python function, include a docstring as the first
thing after the function definition. The docstring should look something
like this:

.. code:: python

    """
    Subgroup: <the metric's subgroup, if it has one>

    <generic description of what the function does; usually, a general idea of the metric's definition>

    :param <parameter_name>:<parameter_description>
    :return: <description of the function's return value> 
    """

Adding dependencies
                   

If you need to add a dependency to Augur for your function, simply add
the import statment to the file as usual, then in ``setup.py`` add the
dependency to the ``install_requires`` list. For example, if my new
function uses a package called ``mizzou``, I would find the
``install_requires`` list:

.. code:: python

    install_requires=['beautifulsoup4', 'flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent', 'gunicorn'],

and add ``mizzou`` as such:

.. code:: python

    install_requires=['beautifulsoup4', 'flask', 'flask-cors', 'PyMySQL', 'requests', 'python-dateutil', 'sqlalchemy', 'pandas', 'pytest', 'PyGithub', 'pyevent', 'gunicorn', 'mizzou'],

--------------

Adding API routes
~~~~~~~~~~~~~~~~~

``routes.py`` contains one function, ``create_routes``, which takes a
``server``. In this function, define the plugin's API routes, if it
provides any.

Route creation for metrics and timeseries can be easily done like so:

.. code:: python

    server.addTimeseries(file_name.function_name, 'endpoint')

If the metric is not a timeseries metric, replace ``AddTimeseries()``
with ``AddMetric()`` (a timeseries is a series of numeric data points of
some particular metric over time, e.g. # of commits / week). Later, once
you have finalized the metric, **go back and add documentation.** Follow
the format already outlined to build your documentation.

So for our sample plugin:

.. code:: python

    from flask import request, Response

    def create_routes(server):  

        # this calls the already instatiated version of chaoss that we can use for adding our endpoints
        chaoss = server._augur['chaoss']()

        # to add our sample metric:
        server.AddMetric(chaoss.hello_world, 'chaoss')

--------------

Writing tests
~~~~~~~~~~~~~

Augur uses ``pytest`` for tests. The tests for our sample ``Chaoss``
class are contained in the ``test_chaoss.py`` file inside the plugin's
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

--------------

Using the Python Debugger
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to use an iPython shell to test your functions during
development, in the root directory, first execute ``augur util shell``, which
will drop you into an iPython shell and automatically give you an Augur
application called ``app``.

You can then test your function by first creating a new instance of that
class, and then running your function. For example:
``gh = app.ghtorrent(); gh.closed_issues('rails', 'rails')`` will let
you test the ``closed_issues`` function without actually having to run
the server.

However, it is recommended that you test your function in a Jupyter
notebook, which takes care of that setup for you. Accessing
preconfigured Jupyter notebooks is done by running ``make jupyter`` in
the root directory of the project (make sure to create a jupyter
enviroment by running ``make create-jupyter-env`` first).
