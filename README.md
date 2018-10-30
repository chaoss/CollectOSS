# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=master)](https://travis-ci.org/chaoss/augur)
   dev | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=dev)](https://travis-ci.org/chaoss/augur)



## About Augur

Augur is focused on prototyping open source software metrics. 

Functionally, Augur is a prototyped implementation of the Linux Foundation's [CHAOSS Project](http://chaoss.community) on [open source software metrics](https://github.com/CHAOSS/metrics). Technically, Augur is a [Flask Web Application](http://augurlabs.io), [Python library](https://osshealth.github.io/augur/python/build/html/index.html) and [REST server](https://osshealth.github.io/augur/api/index.html) that presents metrics on open source software development project health and sustainability. Hosting the Augur project requires 



## Installing Augur 

#### Dependencies
 - The [GHTorrent database](http://ghtorrent.org/downloads.html). 
    - You can use the *much* smaller [MSR14 dataset](http://ghtorrent.org/msr14.html) for a quick look or to perform development.
 - A [GitHub Access Token (no write access required)](https://github.com/settings/tokens)

#### Docker Installation
To get Augur up and running quickly, [install our Docker image](./docs/docker-install.md).

#### Local Installation
To contribute to our code base routinely, we recommended that developers configure Augur on their local workstations. Get started with our [installation instructions for developers](docs/dev-install.md), and then check out our [development guide](docs/dev-guide/dev-guide-overview.md)

**Both configurations require a MariaDB database with a subset of the GHTorrent dataset** 



## Augur Development
To contribute to Augur, check out our [tutorial](docs/tutorial.md), [development guide](docs/dev-guide/dev-guide-overview.md) and [notes on making contributions](CONTRIBUTING.md). Also, please note our [code of conduct](CODE_OF_CONDUCT.md). We want Augur to be a welcoming development community that is open for everyone. 



## Roadmap
Our technical, outreach, and academic goals [roadmap](https://github.com/OSSHealth/augur/wiki/Release-Schedule).



## License and Copyright
Copyright © 2018 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
