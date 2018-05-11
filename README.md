# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/OSSHealth/augur.svg?branch=master)](https://travis-ci.org/OSSHealth/augur)
   dev | [![Build Status](https://travis-ci.org/OSSHealth/augur.svg?branch=dev)](https://travis-ci.org/OSSHealth/augur)

Augur is focused on prototyping open source software metrics. 

Functionally, [Augur is a prototyped implementation](http://augurlabs.io) of Linux Foundation's [CHAOSS Project](http://chaoss.community) on [open source software metrics](https://github.com/CHAOSS/metrics). Technically, Augur is a Python library and REST server that presents metrics on open source software development project health and sustainability. Hosting the Augur project requires 
    - The [GHTorrent database](http://ghtorrent.org/downloads.html). 
     - You can use the *much smaller [MSR14 dataset](http://ghtorrent.org/msr14.html) for a quick look or to perform development.  

To **get Augur up and running quickly**, install our docker image. [Installation Instructions for Docker Image of Augur](./docker-install.md)

To **contribute to our code base routinely**, we recommended that developers configure Augur on their local workstations.  [Installation Instructions for Developers](./dev-install.md)

**Both configurations require a MariaDB database with a subset of the GHTorrent dataset** 

Roadmap
-------
Our technical, outreach, and academic goals [roadmap](https://github.com/OSSHealth/augur/wiki/Release-Schedule).


License and Copyright
---------------------
Copyright © 2018 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
