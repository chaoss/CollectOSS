# GHData

branch | status
--- | ---
master | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=master)](https://travis-ci.org/OSSHealth/ghdata)
dev | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=dev)](https://travis-ci.org/OSSHealth/ghdata)

GHData is a Python library and REST server that provides data related to GitHub repositories. Hosting GHData project requires the GHTorrent database. [Backups of this database are avaliable](http://ghtorrent.org/downloads.html) and [it can be synchronized with current data](https://github.com/OSSHealth/ghtorrent-sync). Support for all event types reported by the [GitHub Events API](https://developer.github.com/v3/activity/events/) are planned for the version 1.0.0 milestone.

GHData is under heavy development; expect frequent backwards-incompatible changes until a 1.x.x release!

Roadmap
-------

Our technical, outreach, and academic goals [roadmap](docs/roadmap.md).


License and Copyright
---------------------

Copyright © 2017 University of Nebraska at Omaha and the University of Missouri

GHData is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file LICENSE for more details.

All associated documentation is licensed under the terms of the Creative Commons Attribution Share-Alike 4.0 license. See the file CC-BY-SA-4.0 for more details.


Dependencies
------------

- Python 3.4.x and `pip`
- MySQL 5.x or later with the [GHTorrent database](http://ghtorrent.org/) [MSR14 dataset](http://ghtorrent.org/) for testing
  - [Installation instructions](https://github.com/gousiosg/github-mirror/tree/master/sql)

Installation
------------

First, install ghdata

- Stable: `pip install --upgrade https://github.com/OSSHealth/ghdata/archive/master.zip`
- Development: `git clone -b dev https://github.com/OSSHealth/ghdata/ && pip install --upgrade ./ghdata/`

Then, run `ghdata` to create a new config file. Edit the generated `ghdata.cfg` file with your database settings.

Run `ghdata` again. For development, use `make run-debug`, that will start the server with Werkzeug's debugging on.

Usage
-----

To run GHData as a server: 
  1. Type `ghdata` in a terminal. A config file named ghdata.cfg will be generated. 
  2. Edit the ghdata.cfg file with your database settings. 
  3. Type `ghdata` again to start the server.


To use as a Python package:
```python
from ghdata import GHData

client = GHData('mysql+pymysql://<user>:<pass>@<host>:<port>/<database name>')
railsID = client.repoid(owner='rails', repo='rails')
railsStars = client.stargazers(railsID)
```

TODO: More/Better API documentation

DFD Descritpion of GHData
---------------------------------------

DFD Image Here


History
-------




Maintainers
-----------


(This work has been funded through the Alfred P. Sloan Foundation)

