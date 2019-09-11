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

There are two ways to start the facade worker. 

1. The first involves setting your facade worker block in your augur.config.json file with the "switch" set to "1". Which starts it automatically. 
2. You can start it yourself, after you start Augur, in one of two ways: 

    >facade_worker_start 
    
    >nohup facade_worker_start >facade.log 2>facade.err & 


Installation
------------

The Facade Worker is installed automatically with the regular Augur installation. 


Requirements
^^^^^^^^^^^^

Requirements are handled by the regular Augur installation. 

Compatibility
-------------

Our most recent database schema is in Postgres. Our benchmarks show that Facade performs between 20% and 30% faster on Postgres than MySQL or MariaDb. 

Licence
-------

Facade is currently license with an Apache 2 License. https://github.com/brianwarner/facade/blob/master/LICENSE Brian Warner and his team are considering conversion to the MIT license.  The only other comments we have right now are 1) we are going to make sure the Linux Foundation, Augur users, and Brian are happy, regardless of how that works out, and 2) Brian is unlikely to recognize the code, as we have substantially modified this version for Augur's unified data model, and aside from the .git-log mining capabilities and analysis tables, our worker is a significant modification to Facade that, at this point, could not be merged back into the main project without a lot of effort of Brian's part. We love Brian. Viva la Brian Warner!

Authors
-------

Facade was written by Brian Warner. The `facade_worker` was writtenby the `Augur Team <s@goggins.com>`_.
