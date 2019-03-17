Windows Installation
====================

We currently don't support local installation of Augur for Windows.
However, we do provide a Vagrant box which can be used to spin up an
Ubuntu VM with Augur pre-installed.

Dependencies
------------

-  `Git
   client <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
-  `Vagrant <https://www.vagrantup.com/>`__
-  `Virtualbox <https://www.virtualbox.org/>`__
-  `GitHub Access Token <https://github.com/settings/tokens>`__ (no
   write access required)

1. Clone the repository and start the VM.

.. code:: bash

   # on your local machine

   # using your Git client: 
   git clone https://github.com/chaoss/augur.git

   # using Command Prompt
   cd augur
   vagrant up # this might take a while
   vagrant ssh

Note: you’ll probably see a fair bit of errors during this provisioning
process. Don’t worry about them, most of them are harmless. *Probably.*

2. Log in as ``root`` and navigate to ``/vagrant/augur``. This folder is
   synced with your local clone of ``augur``, meaning you’ll be able to
   use your preferred local editor and just use the VM to run augur.

.. code:: bash

   # inside the vagrant VM
   sudo su -
   cd /vagrant/augur

   # due to vagrant weirdness, we have to manually install the python packages. This might take a while
   $AUGUR_PIP install --upgrade .

3. Add your GitHub API key to the ``augur.config.json`` file under the
   section ``GitHub``.

4. Start both the backend and frontend servers with ``make dev``.

.. code:: bash

   make dev

5. When you’re done working in the VM, type ``exit`` twice: once to log
   out of ``root``, and another to log out of the VM. Don’t forget to
   shut down the VM with ``vagrant halt``.

If you’re interested in adding a new plugin, data source, or metric,
check out the `backend development
guide <http://augur.augurlabs.io/static/docs/dev-guide/3-backend.html>`__.
If new visualizations are more your speed, you’ll want the [frontend
development
guide](http://augur.augurlabs.io/static/docs/dev-guide/4-frontend.html).

TL;DR
~~~~~

.. code:: bash

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
   $AUGUR_PIP install --upgrade .

   # add your GitHub personal access token to augur.config.json

   # start the frontend and backend servers
   make dev
   # full steam ahead!
