# GHData

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=master)](https://travis-ci.org/OSSHealth/ghdata)
   dev | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=dev)](https://travis-ci.org/OSSHealth/ghdata)

GHData is a Python library and REST server that provides data related to GitHub repositories. Hosting the GHData project requires a copy of the [GHTorrent database](http://ghtorrent.org/downloads.html).

GHData is under heavy development; expect frequent backwards-incompatible changes until a 1.x.x release!



Roadmap
-------
Our technical, outreach, and academic goals [roadmap](https://github.com/OSSHealth/ghdata/wiki/Release-Schedule).



Installation with Docker
------------------------
  1. Clone the repo
  2. `docker-compose build`
  3. `docker-compose up`



Installation without Docker
---------------------------
### Dependencies
- Python 3.4.x and `pip`
- MySQL 5.x or later with the [GHTorrent database](http://ghtorrent.org/)
  - You can use the [MSR14 dataset](http://ghtorrent.org/msr14.html) for testing
- [Installation instructions](https://github.com/gousiosg/github-mirror/tree/master/sql)

After restoring GHTorrent (or msr14) to MySQL, it is recommended you create a user for GHData. GHData only needs `SELECT` privileges.

Once the database is set up, clone GHData (`git clone https://github.com/OSSHealth/ghdata/` then install `cd ghdata && pip install -U .`

Run `ghdata` to create the configuration file (ghdata.cfg). Edit the file to reflect your database credentials.

Move ./ghdata/ghdata/static/ to a static host on the same domain. If you would like GHData to serve the files itself, set the "developer" flag to 1 in ghdata.cfg. *`ghdata` must be run in the base of the repo if it is serving the static files*

Run `ghdata` to start the backend.



License and Copyright
---------------------
Copyright © 2017 University of Nebraska at Omaha and the University of Missouri

GHData is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file LICENSE for more details.

(This work has been funded through the Alfred P. Sloan Foundation)

