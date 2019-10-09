# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=master)](https://travis-ci.org/chaoss/augur)
   dev | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=dev)](https://travis-ci.org/chaoss/augur)

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2788/badge)](https://bestpractices.coreinfrastructure.org/projects/2788)

## About Augur

Augur is focused on prototyping open source software metrics.

Functionally, Augur is a prototyped implementation of the Linux Foundation's [CHAOSS Project](http://chaoss.community) on [open source software metrics](https://github.com/chaoss/metrics). Technically, Augur is a [Flask web application](http://augurlabs.io), [Python library](http://augur.augurlabs.io/static/docs/) and [REST server](http://augur.augurlabs.io/static/api_docs/) that presents metrics on open source software development project health and sustainability.

## Getting Started
-------------------

_**Note: we currently only support MacOS and Linux.**_

Dependencies
------------
- [Git client](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [GitHub Access Token](https://github.com/settings/tokens) (no write access required)
- [Python 3.6 or higher](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [PostgreSQL 11](https://www.postgresql.org/download/) installation with the [Augur schema](https://github.com/chaoss/augur/blob/dev/augur/persistence_schema/new-augur.0.0.77.8-release.sql) installed
 
### Installation
----------------

To get started, first clone the repository and switch to the `dev` branch.
```
git clone https://github.com/chaoss/augur.git
cd augur/
git checkout dev
```

Next, install the project:
```
make install
```

This will install Augur and its data collection workers, as well as prompt you for **credentials for a connection to a Postgres 11 database with the Augur schema installed**.

You will also be prompted to install the the frontend dependencies. If you want to use the visualizations that come with Augur, please select "Yes", otherwise please select "No".

After this is done, you should have a \*mostly\* functioning version of Augur. To double check, run `augur_localstart.sh` like so:
```
./augur_localstart.sh
```
and then check the log files. After a moment, here's about what you should see in `logs/augur_backend.log`:
```
2019-09-04 12:39:28 parsec augur[19051] INFO Booting broker and its manager...
2019-09-04 12:39:29 parsec augur[19051] INFO Booting housekeeper...
2019-09-04 12:39:51 parsec root[19051] INFO Starting update processes...
2019-09-04 12:39:52 parsec root[19083] INFO Housekeeper spawned issues model updater process for subsection 0 with PID 19083
2019-09-04 12:39:52 parsec augur[19051] INFO Starting server...
2019-09-04 12:39:52 parsec root[19084] INFO Housekeeper spawned pull_requests model updater process for subsection 0 with PID 19084
[2019-09-04 12:39:52 -0500] [19051] [INFO] Starting gunicorn 19.9.0
[2019-09-04 12:39:52 -0500] [19051] [INFO] Listening at: http://0.0.0.0:5000 (19051)
[2019-09-04 12:39:52 -0500] [19051] [INFO] Using worker: sync
[2019-09-04 12:39:52 -0500] [19085] [INFO] Booting worker with pid: 19085
[2019-09-04 12:39:52 -0500] [19086] [INFO] Booting worker with pid: 19086
[2019-09-04 12:39:52 -0500] [19087] [INFO] Booting worker with pid: 19087
[2019-09-04 12:39:53 -0500] [19088] [INFO] Booting worker with pid: 19088
[2019-09-04 12:39:53 -0500] [19089] [INFO] Booting worker with pid: 19089
[2019-09-04 12:39:53 -0500] [19090] [INFO] Booting worker with pid: 19090
[2019-09-04 12:39:53 -0500] [19091] [INFO] Booting worker with pid: 19091
[2019-09-04 12:39:53 -0500] [19092] [INFO] Booting worker with pid: 19092
127.0.0.1 - [04/Sep/2019:12:40:04 -0500] - GET /api/unstable HTTP/1.1
```
And at **the bottom** of in `logs/augur_frontend.log`:
```
  App running at:
  - Local:   http://localhost:8080/
  - Network: http://192.168.1.141:8080/
```

If the two above examples look similar to your own output, then you're good to go! Head to the link specified in the frontend file (in this example it's `http://localhost:8080/`) it out!

**Important note: if you chose to use your own database, please make sure you've added a few repositories to collect data for (instructions for which are directly below), as otherwise the frontend will not display anything!**

## Data Collection
----------------

You can follow instructions for collecting data about specific repositories of interest, **OR** use our sample dataset to get going faster.
    - Option 1: [Configure Augur to get Data for your repositories of interest.](./docs/setup/augur-get-commit-data.md) *or*
    - Option 2: [Load up a sample database we built to get new developers going quickly](./docs/setup/augur-load-data.md)

If you are collecting data of your own, you must [start up the workers](./docs/setup/augur-get-workers-going.md)

If you have any issues, please feel free to request to email straight into our slack channel! p9j0r6s0m4a0t8v5@augurlabs.slack.com for new developer support!!  

## Guidelines
----------------

To contribute to Augur, please check out our [development guide](http://augur.augurlabs.io/static/docs/dev-guide/1-overview.html) and [notes on making contributions](CONTRIBUTING.md). Also, please note our [code of conduct](CODE_OF_CONDUCT.md). We want Augur to be a welcoming development community that is open to everyone.

Please note we require all commits to be signed off with a [Developer Certificate of Origin](https://developercertificate.org/) in accordance with the [CHAOSS Project Charter section 8.2.1](https://chaoss.community/about/charter/#user-content-8-intellectual-property-policy). This can be easily done by using the `-s` flag when using `git commit`. For example: `git commit -s -m "Update README.md"`.


## License and Copyright
----------------

Copyright © 2019 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
