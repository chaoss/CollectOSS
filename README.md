# Augur NEW Release v0.86.0

Augur is primarily a data engineering tool that makes it possible for data scientists to gather open source software community data - less data carpentry for everyone else! 
The primary way of looking at Augur data is through [8Knot](https://github.com/oss-aspen/8knot), a public instance of 8Knot is available [here](https://metrix.chaoss.io) - this is tied to a public instance of [Augur](https://ai.chaoss.io). 

[![first-timers-only](https://img.shields.io/badge/first--timers--only-friendly-blue.svg?style=flat-square)](https://www.firsttimersonly.com/)
We follow the [First Timers Only](https://www.firsttimersonly.com/) philosophy of tagging issues for first timers only, and walking one newcomer through the resolution process weekly. You can find these issues tagged with [first timers only](https://github.com/chaoss/augur/labels/first-timers-only) on our issues list.

[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme) [![Build Docker images](https://github.com/chaoss/augur/actions/workflows/build_docker.yml/badge.svg)](https://github.com/chaoss/augur/actions/workflows/build_docker.yml) [![Hits-of-Code](https://hitsofcode.com/github/chaoss/augur?branch=main)](https://hitsofcode.com/github/chaoss/augur/view?branch=main) [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2788/badge)](https://bestpractices.coreinfrastructure.org/projects/2788)

## NEW RELEASE ALERT!
**If you want to jump right in, the updated docker, docker-compose and bare metal installation instructions are available [here](docs/new-install.md)**.

Augur is now releasing a dramatically improved new version to the ```main``` branch. It is also available [here](https://github.com/chaoss/augur/releases/tag/v0.86.0).


- The `main` branch is a stable version of our new architecture, which features:
  - Dramatic improvement in the speed of large scale data collection (100,000+ repos). All data is obtained for 100k+ repos within 2 weeks.
  - A new job management architecture that uses Celery and Redis to manage queues, and enables users to run a Flower job monitoring dashboard.
  - Materialized views to increase the snappiness of API’s and Frontends on large scale data.
  - Changes to primary keys, which now employ a UUID strategy that ensures unique keys across all Augur instances.
  - Support for [8knot](https://github.com/oss-aspen/8kno) dashboards (view a sample [here](https://eightknot.osci.io/)).
  *beautification coming soon!*
  - Data collection completeness assurance enabled by a structured, relational data set that is easily compared with platform API Endpoints.
- The next release of the new version will include a hosted version of Augur where anyone can create an account and add repos *they care about*.
If the hosted instance already has a requested organization or repository it will be added to a user’s view. If its a new repository or organization, the user will be notified that collection will take (time required for the scale of repositories added). 

## What is Augur?
Augur is a software suite for collecting and measuring structured data
about [free](https://www.fsf.org/about/) and [open-source](https://opensource.org/docs/osd) software (FOSS) communities.

We gather trace data for a group of repositories, normalize it into our data model, and provide a variety of metrics about said data. The structure of our data model enables us to synthesize data across various platforms to provide meaningful context for meaningful questions about the way these communities evolve.

Augur’s main focus is to measure the overall health and sustainability of open source projects, as these types of projects are system critical for nearly every software organization or company. We do this by gathering data about project repositories and normalizing that into our data model to provide useful metrics about your project’s health.

For example, one of our metrics is *burstiness*. Burstiness – how are short timeframes of intense activity, followed by a corresponding return to a typical pattern of activity, observed in a project? 
This can paint a picture of a project’s focus and gain insight into the potential stability of a project and how its typical cycle of updates occurs. 

We are a [CHAOSS](https://chaoss.community) project, and many of our
metrics are implementations of the metrics defined by our awesome community. You can find a full list of them [here](https://chaoss.community/metrics/).

For more information on [how to get involved on the CHAOSS website](https://chaoss.community/participate/).

## Collecting Data

Augur supports ```Python3.7``` through ```Python3.11``` on all platforms. ```Python3.12``` and above do not yet work because of machine learning worker dependencies. On OSX, you can create a ```Python3.11``` environment, by running:
```
$ python3.11 -m venv path/to/venv
```

Augur's main focus is to measure the overall health and sustainability of open source projects.

Augur collects more data about open source software projects than any other available software. Augur's main focus is to measure the overall health and sustainability of open source projects.

One of Augur's core tenets is a desire to openly gather data that people can trust, and then provide useful and well-defined metrics that help give important context to the larger stories being told by that data.

We do this in a variety of ways, one of which is doing all our own data collection in house. We currently collect data from a few main sources:

1. Raw Git commit logs (commits, contributors)
2. GitHub's API (issues, pull requests, contributors, releases, repository metadata)
3. The Linux Foundation's [Core Infrastructure Initiative](https://www.coreinfrastructure.org/) API (repository metadata)
4. [Succinct Code Counter](https://github.com/boyter/scc), a blazingly fast Sloc, Cloc, and Code tool that also performs COCOMO calculations

This data is collected by dedicated data collection workers controlled by Augur, each of which is responsible for querying some subset of these data sources.
We are also hard at work building workers for new data sources. If you have an idea for a new one, [please tell us](https://github.com/chaoss/augur/issues/new?template=feature_request.md) - we'd love your input!


## Getting Started

If you're interested in collecting data with our tool, the Augur team has worked hard to develop a detailed guide to get started with our project which can be found [in our documentation](https://oss-augur.readthedocs.io/en/main/getting-started/toc.html).

If you're looking to contribute to Augur's code, you can find installation instructions, development guides, architecture references (coming soon), best practices and more in our [developer documentation](https://oss-augur.readthedocs.io/en/main/development-guide/toc.html). 

Please know that while it's still rather sparse right now,
but we are actively adding to it all the time.

If you get stuck, please feel free to [ask for help](https://github.com/chaoss/augur/issues/new)!

## Contributing

To contribute to Augur, please follow the guidelines found in our [CONTRIBUTING.md](CONTRIBUTING.md) and our [Code of Conduct](CODE_OF_CONDUCT.md). Augur is a welcoming community that is open to all, regardless if you're working on your 1000th contribution to open source or your 1st.
We strongly believe that much of what makes open source so great is the incredible communities it brings together, so we invite you to join us!

## License, Copyright, and Funding

Copyright © 2025 University of Nebraska at Omaha, University of Missouri, Brian Warner, and the CHAOSS Project.

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the [LICENSE](LICENSE) file for more details.

This work has been funded through the Alfred P. Sloan Foundation, Mozilla, The Reynolds Journalism Institute, contributions from VMWare, Red Hat Software, Grace Hopper's Open Source Day, GitHub, Microsoft, Twitter, Adobe, the Gluster Project, Open Source Summit (NA/Europe), and the Linux Foundation Compliance Summit.

Significant design contributors include Kate Stewart, Dawn Foster, Duane O'Brien, Remy Decausemaker, others omitted due to the  memory limitations of project maintainers, and 15 Google Summer of Code Students. 

Current maintainers
--------------------
- `Derek Howard <https://github.com/howderek>`_
- `Andrew Brain <https://github.com/ABrain7710>`_
- `Isaac Milarsky <https://github.com/IsaacMilarky>`_
- `John McGinnis <https://github.com/Ulincys>`_ 
- `Sean P. Goggins <https://github.com/sgoggins>`_ 

Former maintainers
--------------------
- `Carter Landis <https://github.com/ccarterlandis>`_
- `Gabe Heim <https://github.com/gabe-heim>`_
- `Matt Snell <https://github.com/Nebrethar>`_
- `Christian Cmehil-Warn <https://github.com/christiancme>`_
- `Jonah Zukosky <https://github.com/jonahz5222>`_
- `Carolyn Perniciaro <https://github.com/CMPerniciaro>`_
- `Elita Nelson <https://github.com/ElitaNelson>`_
- `Michael Woodruff <https://github.com/michaelwoodruffdev/>`_
- `Max Balk <https://github.com/maxbalk/>`_

Contributors
--------------------
- `Dawn Foster <https://github.com/geekygirldawn/>`_
- `Ivana Atanasova <https://github.com/ivanayov/>`_
- `Georg J.P. Link <https://github.com/GeorgLink/>`_
- `Gary P White <https://github.com/garypwhite/>`_

GSoC 2022 participants
-----------------------
- `Kaxada <https://github.com/kaxada>`_
- `Mabel F <https://github.com/mabelbot>`_
- `Priya Srivastava <https://github.com/Priya730>`_
- `Ramya Kappagantu <https://github.com/RamyaKappagantu>`_
- `Yash Prakash <https://gist.github.com/yash-yp>`_

GSoC 2021 participants
-----------------------
- `Dhruv Sachdev <https://github.com/Dhruv-Sachdev1313>`_
- `Rashmi K A <https://github.com/Rashmi-K-A>`_
- `Yash Prakash <https://github.com/yash2002109/>`_
- `Anuj Lamoria <https://github.com/anujlamoria/>`_
- `Yeming Gu <https://github.com/gymgym1212/>`_
- `Ritik Malik <https://gist.github.com/ritik-malik>`_

GSoC 2020 participants
-----------------------
- `Akshara P <https://github.com/aksh555/>`_
- `Tianyi Zhou <https://github.com/tianyichow/>`_
- `Pratik Mishra <https://github.com/pratikmishra356/>`_
- `Sarit Adhikari <https://github.com/sarit-adh/>`_
- `Saicharan Reddy <https://github.com/mrsaicharan1/>`_
- `Abhinav Bajpai <https://github.com/abhinavbajpai2012/>`_

GSoC 2019 participants
-----------------------
- `Bingwen Ma <https://github.com/bing0n3/>`_
- `Parth Sharma <https://github.com/parthsharma2/>`_

GSoC 2018 participants
-----------------------
- `Keanu Nichols <https://github.com/kmn5409/>`_
