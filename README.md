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



Installation with Docker (easy to get up and running)
------------------------
  1. Clone the repo
  2. `docker-compose build`
  3. `docker-compose up`



Installation without Docker (recommended for developers)
---------------------------
### Dependencies
- Python 3.4.x/Python 2.7.x and `pip`
- Static web server such as nginx or Apache
- MySQL 5.x or later with the [GHTorrent database](http://ghtorrent.org/)
  - You can use the [MSR14 dataset](http://ghtorrent.org/msr14.html) for testing
  - Our Development team has a public read only database you can request access to
  - If you want to install your own copy of the MSR14 dataset [Installation instructions](https://github.com/gousiosg/github-mirror/tree/master/sql)

After restoring GHTorrent (or msr14) to MySQL, it is recommended you create a user for GHData. GHData only needs `SELECT` privileges.

Once the database is set up, clone GHData
```bash
git clone https://github.com/OSSHealth/ghdata/
cd ghdata && pip install -U .
```
Copy the files in [ghdata repo]/frontend/public to your webserver:

Run `ghdata` to create the configuration file (ghdata.cfg). Edit the file to reflect your database credentials.

Run `ghdata` to start the backend. Visit your front


Developer Installation
----------------------

### Dependencies
- Python 3.4.x and Python 2.7.x with `pip2` and `pip3`
- MySQL 5.x or later with the [GHTorrent database](http://ghtorrent.org/)
  - You can use the [MSR14 dataset](http://ghtorrent.org/msr14.html) for testing
- NodeJS 7.x or newer

#### Ubuntu
```
   ## Python Installs on UBUNUTU
   sudo apt-get install python-pip
   sudo apt-get install python3-pip

   ## For Development you need NodeJS
   sudo apt-get install nodejs
```

First, clone the repo and checkout the dev branch:

```bash
git clone https://github.com/OSSHealth/ghdata/ && cd ghdata && git checkout dev
```

Install the Python and Node developer dependencies:
```bash
make install-dev
```

For futher instructions on how to add to GHData, here is a guide to adding an endpoint [Dev Guide Part 1](docs/dev-guide-pt1.md)

Frontend development guide coming soon!

You're good to go.

In one shell, you'll want to run `ghdata`, in another run `cd frontend/ && brunch watch -s`.

If you have GNU Screen installed. this can be done automatically using `make dev-start`.

The screen sessions can be killed with `make dev-stop`

License and Copyright
---------------------
Copyright © 2017 University of Nebraska at Omaha and the University of Missouri

GHData is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file LICENSE for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
