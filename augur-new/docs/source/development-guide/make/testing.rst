Testing
=======

**THIS SECTION IS UNDER CONSTRUCTION.**

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues

These commands are used to run specific subsets of unit tests. We use ``tox`` to manage the test environments, and ``pytest`` as the test runner. Each of these commands except for ``make test-pythons-versions`` will use your default Python version, while ``make test-python-versions`` will test all supported Python versions. 

--------------

``make test``
-------------
This command runs ALL available tests for both the metric functions and their API endpoints.

Example\:

.. code-block:: bash

  $ make test

--------------

``make test-metrics``
------------------------
This command will run ALL unit tests for the metric functions.

Example\:

.. code-block:: bash

  $ make test-metrics

--------------

``make test-metrics-api``
--------------------------
The above command runs ALL tests for the metrics API.

Example\:

.. code-block:: bash

  $ make test-metrics-api

--------------

``make test-python-versions``
-----------------------------
The above command runs all tests under all currently supported versions of **Python 3.6 and above**.

Example\:

.. code-block:: bash

  $ make test-python-versions
