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

[Grab the source tarball for the latest release](https://github.com/xxx) and use `pip` to install
it as a package. Replace `0.x.x` with the latest release version number.

We recommend doing this inside a Python [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/), but it
is not a requirement. If you are not inside a virtualenv you may have to run `pip` as root (not recommended!).

    $ tar xf 0.x.x.tar.gz
    $ pip install ./GHData.x.x

Then run the install script for the default system:

    $ ./GHData.x.x/scripts/install-ghdata.sh

### Step 2 (Optional) - Change the default configuration

Not required, but strongly recommended, is to generate an initial config file:


### Step 3 (Optional) - Add MySQL configuration


### Step 4 - Database setup

Finally, to create all necessary tables and views in the database:

    $ ghdata dbinit

You only need to do this once. **This command will drop all existing tables from your GHData database, so be careful!**

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
