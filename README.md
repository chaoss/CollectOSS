# Augur

branch | status
   --- | ---
master | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=master)](https://travis-ci.org/chaoss/augur)
   dev | [![Build Status](https://travis-ci.org/chaoss/augur.svg?branch=dev)](https://travis-ci.org/chaoss/augur)

## About Augur

Augur is focused on prototyping open source software metrics. 

Functionally, Augur is a prototyped implementation of the Linux Foundation's [CHAOSS Project](http://chaoss.community) on [open source software metrics](https://github.com/chaoss/metrics). Technically, Augur is a [Flask web application](http://augurlabs.io), [Python library](http://augur.augurlabs.io/static/docs/) and [REST server](http://augur.augurlabs.io/static/api_docs/) that presents metrics on open source software development project health and sustainability. 


## Development 
-------------------
### Vagrant
**The quickest way to get started working on Augur is by using [Vagrant](https://www.vagrantup.com/)** to spin up a virtual machine (VM) that comes with Augur already installed. We'll do all the work of setting up and installing dependencies, leaving you free to jump right into contributing something awesome. 

*Caveat: if you’re a super nerd who likes to have total control over your development environment, there’s a local installation link at the bottom of this page. For the rest of you, Vagrant is the way to go, especially if you've had trouble getting all the dependcies installed locally, are not comfortable installing them yourself, or are using an OS for which we don't currently support local installation. We currently only support local installation for macOS and most flavors of Linux.*

#### Dependencies

- [Vagrant](https://www.vagrantup.com/)
- [Virtualbox](https://www.virtualbox.org/)
- Local installation of Augur
- [GitHub Access Token](https://github.com/settings/tokens) (no write access required)

To get started, you'll need a VM provider- we currently only support [Virtualbox](https://www.virtualbox.org/). You'll also need to install [Vagrant](https://www.vagrantup.com/downloads.html). To begin, clone the repository, enter the root directory, and run `make vagrant`.

```bash
# on your local machine
git clone https://github.com/chaoss/augur.git
cd augur
make vagrant
```

The first time you run this command, Vagrant will need to download the base box configuration. After that, it will provision the VM and then install Augur and its dependencies. Note: you'll probably see a fair bit of errors during this provisioning process as Augur is getting installed. Don't worry about them, most of them are harmless. *Probably.*

After this process has completed, the VM should be up and running. You'll then be automatically logged in to your newly provisioned VM. Log in as `root` with `sudo su -` and then navigate to `/vagrant/augur`. This folder is where you'll be working, as it's synced with your local version of Augur, meaning you won't have to worry about losing your changes after you shutdown the VM. You'll also be able to use your preferred editor. During the provisioning process, Augur will create a lightweight version of both the [Facade](facade-oss.org) and [GHTorrent](http://ghtorrent.org/) datasets, both of which we rely on for a lot of our metrics. You'll need to provide Augur with a [GitHub Access Token](https://github.com/settings/tokens) (no write access required). 

```bash
# inside the vagrant VM
sudo su -
cd /vagrant/augur
```

Once you've reached this point, you're ready to start developing! To start the backend, run `augur`. After you run the this command for the first time, a default configuration file called `augur.config.json` will automatically be generated. Reference the sample configuration file (`sample.config.json`) on how to set up the server, development, and cache configurations, as well as the plugin connections.

```bash
augur # to create an augur.config.json
# send SIGINT to the VM to stop augur so you can edit the config (usually this is CTRL+C)  
```

If you're interested in adding a new plugin, data source, or metric, check out the [backend development guide](http://augur.augurlabs.io/static/docs/dev-guide/3-backend.html). If new visualizations are more your speed, you'll want the [frontend development guide](http://augur.augurlabs.io/static/docs/dev-guide/4-frontend.html).

##### TL;DR
```bash
# on your local machine
git clone https://github.com/chaoss/augur.git
cd augur
make vagrant

# inside the vagrant VM
sudo su -
cd /vagrant/augur

# you might to install the Python dependencies again- vagrant can be weird
pip3 install -e .

augur # to create an augur.config.json

# add your GitHub personal access token to augur.config.json
# full steam ahead!
```

### Local Installation
To contribute to our code base routinely, we recommended that developers configure Augur on their local workstations. Start [here](http://augur.augurlabs.io/static/docs/dev-guide/1-overview.html) to get a primer on the project, or jump straight into our [local installation instructions](http://augur.augurlabs.io/static/docs/dev-guide/2-install.html) for developers.

## Guidelines
To contribute to Augur, please check out our [development guide](http://augur.augurlabs.io/static/docs/dev-guide/1-overview.html) and [notes on making contributions](CONTRIBUTING.md). Also, please note our [code of conduct](CODE_OF_CONDUCT.md). We want Augur to be a welcoming development community that is open to everyone. 

## Roadmap
Our technical, outreach, and academic goals [roadmap](https://github.com/chaoss/augur/wiki/Release-Schedule).

## License and Copyright
Copyright © 2018 University of Nebraska at Omaha, University of Missouri and CHAOSS Project at the Linux Foundation

Augur is free software: you can redistribute it and/or modify it under the terms of the MIT License as published by the Open Source Initiative. See the file [LICENSE](LICENSE) for more details.

(This work has been funded through the Alfred P. Sloan Foundation)
