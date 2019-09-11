facade_worker
===================

.. image:: https://img.shields.io/pypi/v/facade_worker.svg
    :target: https://pypi.python.org/pypi/facade_worker
    :alt: Latest PyPI version

.. image:: False.png
   :target: False
   :alt: Latest Travis CI build status

Augur Worker that collects GitHub data

Usage
-----

There are two ways to stat the facade worker. 

1. The first involves setting your facade worker block in your augur.config.json file with the "switch" set to "1". Which starts it automatically. 
2. You can start it yourself, after you start Augur, in one of two ways: 
    - `facade_worker_start` 
    - `nohup facade_worker_start >facade.log 2>facade.err &` to run in the background. 


Installation
------------

Requirements
^^^^^^^^^^^^

Compatibility
-------------

Licence
-------

Authors
-------

`facade_worker` was written by `Augur Team <s@goggins.com>`_.
