Testing
====================================

To test augur, set up your environment for testing:

.. code:: bash

    export DB_TEST_URL=mysql+pymysql://<username>:<pass>@<host>:<post>/<database>

After that, run ``make test`` to run the plugin/data source unit tests.

To test the Augur API, run ``make test-api``. - You will need to add a Postman API key to your ``augur.config.json``.
It'll look like this: 

.. code:: bash

    ...
    "Postman": {
        "apikey": "your apikey goes here"
    },
    ...
