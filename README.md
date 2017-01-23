# GHData

branch | status
--- | ---
master | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=master)](https://travis-ci.org/OSSHealth/ghdata)
dev | [![Build Status](https://travis-ci.org/OSSHealth/ghdata.svg?branch=dev)](https://travis-ci.org/OSSHealth/ghdata)

GHData aims to provide an interface to data related to GitHub repositories. This project requires the GHTorrent database. [Backups of this database are avaliable](http://ghtorrent.org/downloads.html) and [it can be synchronized with current data](https://github.com/OSSHealth/ghtorrent-sync). Support for all event types reported by the [GitHub Events API](https://developer.github.com/v3/activity/events/) are planned for the version 1.0.0 milestone.

GHData is under heavy development; expect frequent backwards-incompatible changes until a 1.x.x release!


License and Copyright
---------------------

Copyright © 2017 University of Nebraska at Omaha and the University of Missouri

GHData is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file LICENSE for more details.

All associated documentation is licensed under the terms of the Creative Commons Attribution Share-Alike 4.0 license. See the file CC-BY-SA-4.0 for more details.


Dependencies
------------

- Python 3.4.x

Optional:
- MySQL 5.x or later version (can be on a separate machine)

Python libraries:
- All Python dependencies are handled automatically by `pip`.


Installation
------------

### Step 1 - Download and install

To install stable version: `pip install --upgrade https://github.com/OSSHealth/ghdata/archive/master.zip`
To install development version: `pip install --upgrade https://github.com/OSSHealth/ghdata/archive/dev.zip`

### Step 2 (Optional if using command line arguments) - Change the default configuration

Not required, but strongly recommended, is to generate an initial config file: `ghdata create-default-config`

Edit `default.cfg` with your database settings. Run with `ghdata --config default.cfg [commands]` 

Usage
-----


DFD Descritpion of GHData
---------------------------------------

DFD Image Here


History
-------




Maintainers
-----------



(This work has been funded through the Alfred P. Sloan Foundation)
