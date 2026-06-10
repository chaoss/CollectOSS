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


Testing Standards 
-----------------

Different parts of the CollectOSS codebase are held to different standards when it comes to how thoroughly changes are expected to be tested/validated before being allowed to merge.

An approximate, non-exhaustive list of the various levels of testing include:

* **Code Review** - only a code review is needed to make sure things look okay (spelling/grammar, formatting etc). Typically used for README changes or changes to other simple, non-functional text files in the repo
* **Sanity Check** - a simple, automated check, such as a build job, should be run to ensure that syntax is correct and that the changes aren't causing a build failure. Typically used for documentation (what you are reading now)
* **Automated Functional Test** - A more complex automated check, such as unit tests, integration tests, E2E smoke tests, etc should be run to ensure that CollectOSS can at least start up successfully with the new code. Typically used for trivial changes to subcomponents that already have automated tests
* **Manual Functional Test Procedure** - A set of pre-defined testing steps designed to exercise the specific code/problem being changed. This will usually be derived from the reproduction steps for the bug being solved or documented in the related issue/PR before testing so others can reproduce it. Typically used to test fixes for specific bugs
* **Full Collection Test** - The change should be built and run on a small instance (with relevant repos being added to the collection set if necessary) and the instance should be allowed to run to full collection (all collection stages for all repos marked as "success" in the ``collection_status`` operations table). Typically used for basic/generalized behavior changes
* **Difficult Repo Test** - Either the manual functional test or the full collection test can be made more "difficult" by including one or more known-difficult repositories, such as `chaoss/jank <https://github.com/chaoss/jank/>`_ (an artificial repo intended to contain a bunch of examples of problematic git data), or any other repo demonstrating a relevant and extreme/difficult scenario (huge overall size, huge commit count, 50-100k+ commits, etc). Typically used for parsing/performance tests
* **Stress/Scale Test** - the change should be run on an instance (likely pre-existing) with at least 10k diverse repositories for at least one or more full cycles of the collection interval (about 1-2 weeks) to ensure that nothing breaks under load or other scaling-related conditions. Typically used for performance issues, bugs unique to large scale repos, and code thats important enough to require testing on a wide range of different repositories.

Both the final merge decisions as well as decisions about which level of testing is appropriate for a given PR rests with the project maintainers.



If you have questions about testing in CollectOSS or would like to help please reach out via the `CHAOSS Slack <https://chaoss.community/kb-getting-started/>`_ (in the #wg-collectoss-8knot channel) or open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/collectoss/issues
