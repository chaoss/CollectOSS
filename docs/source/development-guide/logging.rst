Logging
=========

Augur's log output can be configured with some basic verbosity and log levels. If you are contributing to Augur,
we recommend you set the ``debug`` flag in the ``Logging`` section of your config file to ``1``. This will
turn the verbosity up, capture **all** logs of every level, and it will allow the data collection tasks to print their output to the screen
if they are being run manually in a separate terminal.

The verbosity and minimum log level can be controlled with the ``verbose`` (boolean flag) and ``log_level``
(one of ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, or ``CRITICAL``) options respectively. There is also
a ``quiet`` flag that will disable all logging output entirely.

If you need to change where the logs are written to, you can use the ``logs_directory`` option. If there is
no ``/`` at the beginning, Augur assumes you are specifying a path relative to the root augur directory, otherwise
it will set the log location to be exactly what you configured. The log directory itself will be created if it doesn't exist,
but only if its parent DOES already exist.
