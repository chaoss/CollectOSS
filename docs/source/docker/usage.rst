Interacting with the containers
================================

Once the containers are up and running, you have a few options for interacting with them. They will automatically collect data for your repositories - but how do you add repositories? We're glad you asked!


Accessing the containers
---------------------------

If you need to access a running container (perhaps to check the worker logs) or run a CLI command, you can use the following helpful command, replacing ``<service_name>`` with the appropriate value:

.. code-block:: bash

    $ docker exec -it <service_name> /bin/bash

You can also step into a running container at every step of the build process and see the status of the container. (This is typically used for debugging)

First, build the image to output build stages.

.. code-block::bash
    $ cd augur/
    $ docker build -t <service_name> -f util/docker/backend/Dockerfile .

Then, run any stage by using the hash that the relevant stage prints out during the build process. The arguments are the same as a normal ``docker run``

.. code-block::bash
    $ docker run -i -t -p <relevant_port>:<relevant_port> --add-host=database:<database_if_backend> --env-file <env_file> <build_hash> bash


Viewing container logs
-------------------------

By default, the only logs shown by the container are the logs of Augur's main data collection process. If you started your container(s) in the background, and want to view these logs again, run the following command in the root ``augur`` directory\:

.. code-block:: bash

    # to quickly view the most recent logs
    $ docker compose logs

    # to watch the logs in real-time (like tail -f)
    $ docker compose logs -f


As for worker logs. They are currently a work in progress to be made easier to view. Shortly, they will automatically populate on the host machine and it will not be necessary to step inside the container.


Conclusion
-----------

This wraps up the Docker section of the Augur documentation. We hope it was useful! Happy hacking!

