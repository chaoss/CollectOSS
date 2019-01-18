Architecture
============

Augur's architecture consists of 5 primary pieces:

Backend:
~~~~~~~~

1. Python plugins that know how to produce metrics from a given
   datasource (``augur.datasources.GHTorrent``,
   ``augur.datasources.Facade``, etc.) or provide a given functionality
2. A main class that's in charge of caching, registering plugins, and
   reading the configuration file (``augur.Application``)
3. A WSGI server built with Flask that exposes the datasources as a REST
   API (``augur.Server``, ``augur.runtime``)

Frontend:
~~~~~~~~~

4. Vue frontend to display visualizations and controls, compiled with
   Brunch
5. Visualizations made with Vega-Lite for the metrics exposed by the
   backend

Technologies
------------

Backend:
~~~~~~~~

-  `Python <https://docs.python.org/3/index.html>`__
-  `Pandas <http://pandas.pydata.org/pandas-docs/stable/>`__
-  `Flask <http://flask.pocoo.org/>`__
-  `Requests <http://docs.python-requests.org/en/master/>`__
-  `MySQL <https://dev.mysql.com/doc/refman/8.0/en/select.html>`__
-  `Gunicorn <http://docs.gunicorn.org/en/stable/>`__
-  `Docker <https://docs.docker.com/>`__
-  `pytest <https://docs.pytest.org/en/latest/>`__

Frontend:
~~~~~~~~~

-  `VueJS <https://vuejs.org/v2/guide/>`__
-  `Vega-Lite <https://vega.github.io/vega-lite/>`__
-  `Brunch <https://brunch.io/>`__
-  `Stylus <http://stylus-lang.com/>`__
-  `Babel <https://babeljs.io/docs/setup/>`__

Documentation:
~~~~~~~~~~~~~~

-  `Sphinx <http://www.sphinx-doc.org/en/master/>`__
-  `apidocjs <http://apidocjs.com/>`__
