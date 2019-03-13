Windows Installation
====================

We currently don\'t support local installation of Augur for Windows.
However, we do provide a Vagrant box which can be used to spin up an
Ubuntu VM with Augur pre-installed.

Dependencies
------------

-   [Git
    client](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
-   [Vagrant](https://www.vagrantup.com/)
-   [Virtualbox](https://www.virtualbox.org/)
-   [GitHub Access Token](https://github.com/settings/tokens) (no write
    access required)

To get started, you'll need a VM provider- we currently only support
[Virtualbox](https://www.virtualbox.org/). You'll also need to install
[Vagrant](https://www.vagrantup.com/downloads.html) and a Git client. To
begin, clone the repository using your Git client, enter the root
directory of the repo using Command Prompt, and run `vagrant up`.

```bash
# on your local machine

# using your Git client: 
git clone https://github.com/chaoss/augur.git

# using Command Prompt
cd augur
vagrant up
vagrant ssh
```

The first time you run this command, Vagrant will need to download the
base box configuration. After that, it will provision the VM and then
install Augur and its dependencies. Note: you'll probably see a fair bit
of errors during this provisioning process as Augur is getting
installed. Don't worry about them, most of them are harmless.
*Probably.*

After this process has completed, the VM should be up and running. Log
in to the VM `vagrant ssh`. Log in as `root` with `sudo su -` and then
navigate to `/vagrant/augur`. This folder is where you'll be working, as
it's synced with your local version of Augur, meaning you won't have to
worry about losing your changes after you shutdown the VM. You'll also
be able to use your preferred editor. During the provisioning process,
Augur will create a lightweight version of both the
[Facade](facade-oss.org) and [GHTorrent](http://ghtorrent.org/)
datasets, both of which we rely on for a lot of our metrics. You'll need
to provide Augur with a [GitHub Access Token](https://github.com/settings/tokens\) (no write access
required).

```bash
# inside the vagrant VM
sudo su -
cd /vagrant/augur

# due to vagrant weirdness, we have to manually install the python packages
sudo $AUGUR_PIP install --upgrade .
```

Augur will automatically create a config file called
`augur.config.json`. Add your GitHub API key to this file under the
section `GitHub`. At this point, you\'re ready to start developing! Run
the backend with `augur`, or the frontend and backend together with
`make dev`.

```bash
make dev
```

If you're interested in adding a new plugin, data source, or metric, check out the [backend development guide](http://augur.augurlabs.io/static/docs/dev-guide/3-backend.html). If new visualizations are more your speed, you'll want the [frontend development guide](http://augur.augurlabs.io/static/docs/dev-guide/4-frontend.html\).

### TL;DR

```bash
# on your local machine

# using your Git client: 
git clone https://github.com/chaoss/augur.git

# using Command Prompt
cd augur
vagrant up
vagrant ssh

# inside the vagrant VM
sudo su -
cd /vagrant/augur

# due to vagrant weirdness, we have to manually install the python packages
sudo $AUGUR_PIP install --upgrade .

# add your GitHub personal access token to augur.config.json

make dev
# full steam ahead!
```
