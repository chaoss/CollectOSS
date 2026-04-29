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

## Who uses CollectOSS?

CollectOSS metrics are used by many other visualization and metrics projects, such as:

- [8Knot](https://github.com/oss-aspen/8Knot)

*If you would like your project or organization listed here, please file a Pull Request!*

## License, Copyright, and Funding

CollectOSS is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the [LICENSE](LICENSE) file for more details.



## Credits

Refer to [CREDITS.md](./CREDITS.md) for detailed information about the people and funding that have helped make this project possible.
