Testing
===============


CollectOSS aims to have a comprehensive set of tests to enable more rapid iteration and greater confidence that changes have not caused new breakage.


Types of Testing 
-----------------

The tests of the CollectOSS app fall into one of several general types.
* unit tests - standalone tests that are simple to run and test single units of functionality (often individual functions or classes)
* integration tests - small subsystem tests that require bringing up additional pieces, such as redis or a database, to perform the test
* end-to-end tests - complete system tests that require running everything

Unit Tests
~~~~~~~~~~~

Unit tests are implemented via pytest and tagged as ``unit`` to make them easy to run.

To run the unit tests, clone the CollectOSS repository and run ``uv run pytest -m unit``


Integration Tests
~~~~~~~~~~~~~~~~~~
Unit tests are also implemented via pytest and tagged as ``integration``.
Because they require additional components, they are not quite as easy to run.


To run the integration tests you will need to start up the associated services. This can be done as follows:

1. Enter the tests directory with ``cd tests/``, this ensures you use the correct dockerfile.
2. Bring up the associated services using the ``docker-compose.yml`` file by running ``docker compose up`` or the podman equivalent.
3. The tests can now be run in a new terminal using ``uv run pytest -m integration``

End to End (E2E) Tests
~~~~~~~~~~~~~~~~~~~~~~~

The end to end tests are currently run as part of a CI job in github actions that is run on pull request.

The main form of end to end test is the smoke test. This test brings up and runs the full container stack for three minutes.
A script monitors the output logs and looks for specific log statements that indicate that CollectOSS is coming up and behaving as expected.

Future end to end tests may also run CollectOSS to the point of fully collecting on some smaller repositories and validating that the database is as expected.


If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/collectoss/issues
