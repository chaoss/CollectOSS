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

_**Note: we only support UNIX systems.**_
If you would like to use Augur but only have access to a Windows system, we recommend setting up a VM if you can. If this is not feasible for you, please reach out to us at [p9j0r6s0m4a0t8v5@augurlabs.slack.com](mailto:p9j0r6s0m4a0t8v5@augurlabs.slack.com) and we will try to help you come up with a solution.

### Dependencies
------------

#### Backend and data collection
----------------
- [Git client](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [GitHub Access Token](https://github.com/settings/tokens) (no write access required)
- [Python 3.6 or higher](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [PostgreSQL 11](https://www.postgresql.org/download/) installation with the [Augur schema](https://github.com/chaoss/augur/blob/dev/augur/persistence_schema/new-augur.0.0.77.8-release.sql) installed
<!-- TODO: I don't think the SQL link is right -->

#### Frontend
----------------
- [Vue.js]()
- [vue-cli]()
- [npm]()
 
### Installation
----------------

0. Clone the repository and switch to the `osd-2019` branch.
```bash
git clone https://github.com/chaoss/augur.git
cd augur/
git checkout osd-2019
```

1. Create a virtual environment in your home environment. Be sure to use the correct `python` command for your installation of Python 3.6+
```bash
python -m venv $HOME/.virtualenvs/augur_env
```


2. Being the installation process.
```bash
make install
```

This procces will:
- install augur's backend and its dependencies
- install data collection workers and their dependencies (you will be able to select which workers you would like: we recommend all of them)
- optionally install augur's frontend and its dependencies
- generate documentation
- prompt the user for **connection credentials for a Postgres 11 installation**

After Augur is installed, given that you provided a correct set of credentials you should have a functioning version of Augur. 

### Usage
----------------
To start the frontend and backend processes together, run `make dev`. The output should like something like this (note that your process IDs and network will be different):  
```
sending SIGTERM to node (Brunch) at PID 9239; bash: line 0: kill: (9239) - No such process
sending SIGTERM to python (Gunicorn) at PID 9224; bash: line 0: kill: (9224) - No such process

Server     Description       Log                   Monitoring                   PID
------------------------------------------------------------------------------------------
Frontend   Brunch            logs/frontend.log     make monitor-backend         9339
Backend    Augur/Gunicorn    logs/backend.log      make monitor-frontend        9324

Monitor both:  make monitor
Restart and monitor: make dev
Restart servers:  make dev-start
Stop servers:  make dev-stop

==> logs/backend.log <==

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

==> logs/frontend.log <==

    ...
    ...
    ...

  Version: typescript 3.5.3, tslint 5.18.0
  Time: 9311ms

  App running at:
  - Local:   http://localhost:8080/
  - Network: http://192.168.1.141:8080/
```
_Note: there will be a lot of linting warnings in the frontend section (indicated here by the ...). Don't worry about them: it's the last 3 lines that indicate success._

Once you see this you're good to go! Head to the local URL specified in the frontend logs section (in this example it's `http://localhost:8080/`) to check it out!

**Important note: if you chose to set up your own database & installed the frontend dependencies, please make sure you've added a few repositories to collect data for (instructions for which are directly below), as otherwise the frontend will not have any data to display!**

### Data Collection
----------------

<!-- TODO: edit these -->
You can follow instructions for collecting data about specific repositories of interest, **OR** use our sample dataset to get going faster.
    - Option 1: [Configure Augur to get Data for your repositories of interest.](./docs/setup/augur-get-commit-data.md) *or*
    - Option 2: [Load up a sample database we built to get new developers going quickly](./docs/setup/augur-load-data.md)

If you are collecting data of your own, you must [start up the workers](./docs/setup/augur-get-workers-going.md).

If you have any issues, please feel free to request to email straight into our slack channel [p9j0r6s0m4a0t8v5@augurlabs.slack.com](mailto:p9j0r6s0m4a0t8v5@augurlabs.slack.com) for new developer support!!

## Contributing
----------------

To contribute to Augur, please follow the guidelines found in our [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md). Augur is a welcoming development community that is open to anyone and everyone of every skill level!

Check out our [documentation](https://oss-augur.readthedocs.io/en/documentation/) for information about our system.

Please note we require all commits to be signed off with a [Developer Certificate of Origin](https://developercertificate.org/) in accordance with the [CHAOSS Project Charter section 8.2.1](https://chaoss.community/about/charter/#user-content-8-intellectual-property-policy). This can be easily done by using the `-s` flag when using `git commit`, e.g. `git commit -s -m "Update README.md"`. **Any pull request containing commits that are not signed off will not be eligible to be merged until all commits are signed off.** 

## License, Copyright, and Funding
----------------

Copyright © 2019 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the [LICENSE](LICENSE) file for more details.

This work has been funded through the Alfred P. Sloan Foundation.
