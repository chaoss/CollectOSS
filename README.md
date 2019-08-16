# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=master)](https://travis-ci.org/chaoss/augur)
   dev | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=dev)](https://travis-ci.org/chaoss/augur)

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2788/badge)](https://bestpractices.coreinfrastructure.org/projects/2788)

## About Augur

We welcome new developers!  We are prototyping a new installation on our `dev` branch now, so if something breaks or seems weird, we will respond quickly if you email us here: p9j0r6s0m4a0t8v5@augurlabs.slack.com ... Drops straight into our Slack channel for support!

Augur is focused on prototyping open source software metrics.

Functionally, Augur is a prototyped implementation of the Linux Foundation's [CHAOSS Project](http://chaoss.community) on [open source software metrics](https://github.com/chaoss/metrics). Technically, Augur is a [Flask web application](http://augurlabs.io), [Python library](http://augur.augurlabs.io/static/docs/) and [REST server](http://augur.augurlabs.io/static/api_docs/) that presents metrics on open source software development project health and sustainability.


## Getting Started
-------------------

Windows installation instructions using Vagrant can be found [here](docs/python/source/windows-install.md).

Dependencies
------------
-   [Git client](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
-   [GitHub Access Token](https://github.com/settings/tokens) (no write access required)


### Developer Setup
1. [Install and configure Augur.](./docs/setup/installing-augur.md)
2. You can follow instructions for collecting data about specific repositories of interest, **OR** use our sample dataset to get going faster.
    - Option 1: [Configure Augur to get Data for your repositories of interest.](./docs/setup/augur-get-commit-data.md) *or*
    - Option 2: [Load up a sample database we built to get new developers going quickly](./docs/setup/augur-load-data.md)
3. If you are collecting data of your own, you  [Start up the Augur Workers](./docs/setup/augur-get-workers-going.md)
4. If you have any issues, please feel free to request to email straight into our slack channel! p9j0r6s0m4a0t8v5@augurlabs.slack.com for new developer support!!  


## Guidelines
To contribute to Augur, please check out our [development guide](http://augur.augurlabs.io/static/docs/dev-guide/1-overview.html) and [notes on making contributions](CONTRIBUTING.md). Also, please note our [code of conduct](CODE_OF_CONDUCT.md). We want Augur to be a welcoming development community that is open to everyone.

Please note we require all commits to be signed off with a [Developer Certificate of Origin](https://developercertificate.org/) in accordance with the [CHAOSS Project Charter section 8.2.1](https://chaoss.community/about/charter/#user-content-8-intellectual-property-policy). This can be easily done by using the `-s` flag when using `git commit`. For example: `git commit -s -m "Update README.md"`.


## License and Copyright
Copyright © 2019 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
