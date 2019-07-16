Metric Status Worker
===================

Augur Worker that collects Metric Status data.

This worker is integrated into Augur's worker architecture and can receieve tasks through the broker.

Usage
-----

Running this Worker
********

To run this worker execute the following command

.. code:: bash

    python -m metric_status_worker.runtime


**Note:** Make sure the broker is running before running the worker

Sending Tasks
********

To send a task to this worker manually, send a POST request to the endpoint ``/task``
with the following json. Change ``git_url`` to the url of the GitHub repository you wish
to run the worker against.

.. code:: javascript

    {
        'job_type': 'UPDATE',
        'models': ['chaoss_metric_status'],
        'given': {}
    }

Scheduling Tasks
********
To make this worker run periodically add a Housekeeper job in ``augur.config.json``.
To do so, in your ``augur.config.json``, in the Housekeeper section add the following:

.. code:: javascript

    {
        "model": "chaoss_metric_status",
        "delay": 60,
    }

Set ``delay`` to specify the interval (in seconds) the worker waits before running again.


Successful Log File
-----
Here is an example of ``worker.log``

.. code-block::

INFO:root:Making database connections...
INFO:root:Starting Flask App with pid: 90461...
INFO:werkzeug: * Running on http://localhost:51238/ (Press CTRL+C to quit)
INFO:root:Sending to work on task: {'job_type': 'UPDATE', 'models': ['chaoss_metric_status'], 'given': {}}
INFO:root:Running...
INFO:werkzeug:127.0.0.1 - - [16/Jul/2019 18:44:05] "POST /AUGWOP/task HTTP/1.1" 200 -
INFO:root:While filtering duplicates, we reduced the data size from 137 to 137

INFO:root:Count of contributors needing insertion: 137

INFO:root:Primary key inserted into the metrics table: [732]
INFO:root:Primary key inserted into the metrics table: [733]
INFO:root:Primary key inserted into the metrics table: [734]
INFO:root:Primary key inserted into the metrics table: [735]
