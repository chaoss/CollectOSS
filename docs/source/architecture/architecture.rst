Architecture
============

Augur's architecture consists of 5 primary pieces:

----------
Backend
----------

1. Workers (``workers`` in the root ``augur/`` directory) which are responsible for collecting data and inserting it into our unified data model 
2. Broker (``augur.routes.broker``) which is reponsible for distributing data collection tasks to the correct workers
3. Housekeeper (``augur.housekeeper.housekeeper.Housekeeper``) which is responsible for keeping the data up to date
4. A main class that's in charge of caching, registering plugins, and
   reading the configuration file (``augur.Application``)
5. A WSGI server built with `Flask <http://flask.pocoo.org/>`__ that exposes the datasources as a REST
   API (``augur.Server``, ``augur.runtime``)

Technologies
-------------

-  `Python <https://docs.python.org/3/index.html>`__
-  `Pandas <http://pandas.pydata.org/pandas-docs/stable/>`__
-  `Flask <http://flask.pocoo.org/>`__
-  `Requests <http://docs.python-requests.org/en/master/>`__
-  `MySQL <https://dev.mysql.com/doc/refman/8.0/en/select.html>`__
-  `Gunicorn <http://docs.gunicorn.org/en/stable/>`__
-  `Docker <https://docs.docker.com/>`__
-  `pytest <https://docs.pytest.org/en/latest/>`__
-  `Sphinx <http://www.sphinx-doc.org/en/master/>`__
-  `apidocjs <http://apidocjs.com/>`__


----------
Frontend
----------

4. Vue frontend to display visualizations and controls
5. Visualizations made with Vega-Lite for the metrics exposed by the
   backend

Technologies
-------------

-  `VueJS <https://vuejs.org/v2/guide/>`__
-  `Vega-Lite <https://vega.github.io/vega-lite/>`__
-  `Brunch <https://brunch.io/>`__
-  `Stylus <http://stylus-lang.com/>`__
-  `Babel <https://babeljs.io/docs/setup/>`__
