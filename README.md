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
- MySQL 5.x or later version (can be on a separate machine)
- GHTorrent in database (can be installed with `ghdata install --historical` on Linux/OS X machines)
  - 50GB download, requires ~1TB free space for the database

Optional:
- Running version of GHTorrent (can be installed with `ghtorrent install`)
  - Requires Ruby and Git

Python libraries:
- All Python dependencies are handled automatically by `pip`.


Installation
------------

### Step 1 - Download and install

To install stable version: `pip install --upgrade https://github.com/OSSHealth/ghdata/archive/master.zip`

To install development version: `pip install --upgrade https://github.com/OSSHealth/ghdata/archive/dev.zip`

### Step 2 (Optional if using command line arguments) - Change the default configuration

The command to create the default configuration file is not yet working.

### Step 3 (Optional if you are able to get the full database) - Install a small, local testing database

Go to: http://ghtorrent.org/msr14.html

Download the MySQL database dump

Extract it (for example using 7-zip)

Extracted file will be named msr14-mysql

The site provides instructions on how to restore it.  Here are some alternate instructions:

  Rename the extracted file to end with .sql
  
  Create a new schema/database
  
  Import the extracted file into the new schema (For example, use MySQL Workbench by clicking Server -> Data Import and then following the instructions in the wizard)

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
