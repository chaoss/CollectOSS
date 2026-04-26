# CollectOSS

[![standard-readme compliant](https://img.shields.io/badge/standard--readme-OK-green.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme) [![Build Docker images](https://github.com/chaoss/collectoss/actions/workflows/build_docker.yml/badge.svg)](https://github.com/chaoss/collectoss/actions/workflows/build_docker.yml) [![Hits-of-Code](https://hitsofcode.com/github/chaoss/collectoss?branch=release)](https://hitsofcode.com/github/chaoss/collectoss/view?branch=release) [![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/2788/badge)](https://bestpractices.coreinfrastructure.org/projects/2788)

## What is CollectOSS?
CollectOSS is a software suite for collecting structured data
about [free](https://www.fsf.org/about/) and [open-source](https://opensource.org/docs/osd) software (FOSS) communities via git forges.

CollectOSS's main focus is to measure the overall health and sustainability of open source projects, as these types of projects are system critical for nearly every software organization or company.

The data CollectOSS collects covers more than just code contributions and extends to anything that can be derived from forge data, including comments, change reviews, releases, and other project activity or interactions. This data is stored in a relational database (PostgreSQL), enabling large-scale data aggregation across any number of repositories to provide context about the way these communities evolve.

CollectOSS is part of [CHAOSS](https://chaoss.community), which is a Linux Foundation® project. Many of our metrics are implementations of the [metrics](https://chaoss.community/metrics/) defined by the CHAOSS community.

## Versions and support
CollectOSS is a Python project distributed via container images and aims to support all currently-supported versions of Python on macOS and Linux platforms. Docker is the primary supported container runtime, but Podman is also supported and used by some maintainers, although it requires configuring some extra permissions to run correctly.

Our `main` branch is our development branch that all pull requests should be based on. The `release` branch is where we merge and tag new versions and is the branch we recommend using in production. You can see tagged versions and corresponding release notes on the [releases page](https://github.com/chaoss/collectoss/releases).

## Installation
Basic initial setup can be completed in a few minutes as follows:

1. Clone the repository - `git clone https://github.com/chaoss/collectoss`
2. (optional) if you want to build the development version, run `docker compose build`
3. Copy the `environment.txt` file to a new file called `.env` and fill in values for the required variables
4. Run `docker compose up` to start the containers

Check out the [CollectOSS Documentation](https://collectoss.readthedocs.io) for more detailed setup instructions and troubleshooting steps.

## Contributing
We strongly believe that communities are what makes open source so impactful. We invite you to join our community, regardless of your experience level or coding abilities! 

Check out the [CHAOSS Getting Started guide](https://chaoss.community/kb-getting-started/) to join Slack and learn more about CHAOSS. After you arrive, we recommend:
- Joining the **#wg-collectoss-8knot** channel (or ask for help finding it)
- Subscribing to the CHAOSS Software meetings in your calendar using the links on the [CHAOSS Calendar](https://chaoss.community/chaoss-calendar/) page

Information about contribution guidelines, building from source, and testing can be found in our [CONTRIBUTING.md](CONTRIBUTING.md). 

## Collecting Data

CollectOSS aims to support the current officially supported Python versions (currently centered around **Python 3.11**). We use [uv](https://github.com/astral-sh/uv) to manage the Python environment because it is fast and takes care of virtual environments for you. To run a command, such as `pytest` in the python environment, you would write:

```bash
uv run pytest
```

The first time this is run, `uv` will automatically download and install the python dependencies for you.

CollectOSS's main focus is to measure the overall health and sustainability of open source projects.

CollectOSS collects more data about open source software projects than any other available software. 

One of CollectOSS's core tenets is a desire to openly gather data that people can trust, and then provide useful and well-defined metrics that help give important context to the larger stories being told by that data.

We do this in a variety of ways, one of which is doing all our own data collection in house. We currently collect data from a few main sources:

1. Raw Git commit logs (commits, contributors)
2. GitHub's API (issues, pull requests, contributors, releases, repository metadata)
3. The Linux Foundation's [Core Infrastructure Initiative](https://www.coreinfrastructure.org/) API (repository metadata)
4. [Succinct Code Counter](https://github.com/boyter/scc), a blazingly fast Sloc, Cloc, and Code tool that also performs COCOMO calculations

This data is collected by dedicated data collection workers controlled by CollectOSS, each of which is responsible for querying some subset of these data sources.
We are also hard at work building workers for new data sources. If you have an idea for a new one, [please tell us](https://github.com/chaoss/collectoss/issues/new?template=feature_request.md) - we'd love your input!


## Getting Started

If you're interested in collecting data with our tool, the CollectOSS team has worked hard to develop a detailed guide to get started with our project which can be found [in our documentation](https://collectoss.readthedocs.io/en/main/getting-started/toc.html).

If you're looking to contribute to CollectOSS's code, you can find installation instructions, development guides, architecture references (coming soon), best practices and more in our [developer documentation](https://collectoss.readthedocs.io/en/main/development-guide/toc.html). 

Please know that while it's still rather sparse right now,
but we are actively adding to it all the time.

If you get stuck, please feel free to [ask for help](https://github.com/chaoss/collectoss/issues/new)!

## Who uses CollectOSS?

CollectOSS metrics are used by many other visualization and metrics projects, such as:

- [8Knot](htps://github.com/oss-aspen/8Knot)

*If you would like your project or organization listed here, please file a Pull Request!*

## License, Copyright, and Funding

Copyright © 2026 University of Missouri, Sean Goggins, and Derek Howard.

CollectOSS is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the [LICENSE](LICENSE) file for more details.

This work has been funded through the Alfred P. Sloan Foundation, Mozilla, The Reynolds Journalism Institute, contributions from VMWare, Red Hat Software, Grace Hopper's Open Source Day, GitHub, Microsoft, Twitter, Adobe, the Gluster Project, Open Source Summit (NA/Europe), and the Linux Foundation Compliance Summit.

Significant design contributors include Kate Stewart, Dawn Foster, Duane O'Brien, Remy Decausemaker, others omitted due to the  memory limitations of project maintainers, and 15 Google Summer of Code Students. 
## Maintainers & Contributors

Refer to [CONTRIBUTORS.md](./CONTRIBUTORS.md) for detailed information about project maintainers, contributors, and GSoC participants.
