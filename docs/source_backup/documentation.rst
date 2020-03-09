Documentation
==============

Currently, Augur maintains 2 distinct sets of documentation for each release. The first is the API 
documentation located on each hosted instance, and the second is the 
`library and usage documentation <https://oss-augur.readthedocs.io/en/master/>`_.

API Documentation
-----------------
The API documenation is written inline using `apiDoc <https://apidocjs.com/>`_. Each public API route is 
decorated with a documenation block of the following format:

  .. code-block:: 
    :linenos:

    """
    @api {method} /path/:param/endpoint-name Endpoint Name
    @apiName endpoint-name
    @apiGroup endpoint-group (usually a CHAOSS group)
    @apiDescription Short description of endpoint, with links to relevant CHAOSS metric documentation if applicable.
    @apiParam {type} name description
    ...
    @apiParam {type} name description
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "value": 100,
                            "date": 12/17/19
                        }
                    ]
    <route definition function>
    """

  .. note::
    The name of the ``param`` in the endpoint path on line 2 should match the name of the corresponding 
    ``@apiParam`` on the lines below.

Example
~~~~~~~~

The following example would be accpetable documentation for the ``issues-new`` ``repo_group`` method in ``issue/routes.py``.

.. code-block:: 
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
    <route definition function>
    """

Building
~~~~~~~~~
To see your changes and make sure everything rendered correctly, run ``make api-docs`` in the root 
``augur/`` directory, and then open ``frontend/public/api_docs/index.html`` in your web browser to view it. 
After opening it once, just run ``make api-docs`` and refresh the page in your browser to see the changes.

Hosting
~~~~~~~
Each installation of augur will have its own API docs available under ``<host>/api_docs/`` (`example <http://augur.osshealth.io/api_docs/>`_)


Library and Usage Documentation
--------------------------------

The rest of the documenation is written using `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ 
and built with `Sphinx <http://www.sphinx-doc.org/en/master/index.html>`_. 

For simplicity's sake we'll avoid going over reStructuredText in detail here, 
but `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`__ is a good reference document.

Similarly, we'll avoid going over Sphinx in great detail as well; `here <http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`__ is a good reference document for the
most commonly used directives.

Building
~~~~~~~~
To see your changes and make sure everything rendered correctly, run ``make library-docs`` in the root 
``augur/`` directory, and then open ``docs/build/html/index.html`` in your web browser to view it. 
After opening it once, just run ``make library-docs`` and refresh the page in your browser to see the changes.

Hosting
~~~~~~~
This documentation is hosted by `Read the Docs <https://oss-augur.readthedocs.io/en/master/>`_.

Enabled branches of the main ``chaoss/augur`` repository will each have their own documentation, with the 
default ``master`` corresponding to ``master`` on the readthedocs. The documentation will automatically be 
built and deployed on a push to one of these branches, but please don't forget to check before you push!
