Installation
=============================================

Local Installation (For Development)
------------------------------------

1. Install Dependencies (OS Specific Instructions Below)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Anaconda
-  NodeJS Version 8.0 or newer, which includes ``npm``

Also remember the database dependency in the `README <http://ghtorrent.org/msr14.html>`__.

1. `Dependency Installation for Ubuntu <#Ubuntu>`__
2. `Dependency Installation for Fedora <#Fedora>`__
3. `Dependency Installation for OS X <#MacOSX>`__

2. `Install Augur <#Install>`__
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ubuntu Dependency Installation Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    # Install NodeSource
    curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -

    # Install NodeJS
    sudo apt-get install -y nodejs

    # Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
    sudo apt-get install -y mariadb-server

    # Install Anaconda
    curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh > Anaconda.sh
    chmod +x Anaconda.sh

    # You must agree to Anaconda's license terms to proceed
    ./Anaconda.sh -b
    rm Anaconda.sh

Fedora Dependency Installation Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    # Install NodeSource
    curl -sL https://rpm.nodesource.com/setup_10.x | sudo -E bash -
    sudo yum install -y nodejs


    # Install NodeJS
    sudo apt-get install -y nodejs

    # Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
    sudo apt-get install -y mariadb-server

    # Install Anaconda
    curl https://repo.anaconda.com/archive/Anaconda3-5.1.0-Linux-x86_64.sh > Anaconda.sh
    chmod +x Anaconda.sh

    # You must agree to Anaconda's license terms to proceed
    ./Anaconda.sh -b
    rm Anaconda.sh

macOS Dependency Installation Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: bash

    # Install Homebrew
    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

    # Install NodeJS 
    brew install wget node

    # Install MariaDB (if needed on the same machine for the GHTorrent/msr14 dataset)
    brew install wget mariadb

    # Install Anaconda
    cd ~/Downloads
    wget https://repo.anaconda.com/archive/Anaconda3-5.1.0-MacOSX-x86_64.pkg
    open Anaconda3-5.1.0-MacOSX-x86_64.pkg


A Note about Anaconda
---------------------
In the past, we've had new developers struggle with getting Anaconda to work, especially on Ubuntu.
Despite these troubles, the development team feels that continuing to support Anaconda is ultimately worthwhile,
as no longer doing so means mainting detailed builds for each package manager, which we'd rather not do.
However, we still want people to work on Augur, and so here are a few tips and tricks to making sure Anaconda
works for you.

1. Make sure Anaconda is installed in your ``PATH``. This varies from shell to shell, so here are a few examples:

.. code:: bash

    # BASH
    # Add this line to your .bash_profile.
    . /Users/carterlandis/anaconda3/etc/profile.d/conda.sh

    # ZSH
    # Add this line to your .zshrc.
    export PATH="/Users/carterlandis/anaconda3/bin:$PATH"

    # FISH
    # Add these lines to your config.fish file.
    set PATH /Users/carterlandis/anaconda3/bin $PATH
    source (conda info --root)/etc/fish/conf.d/conda.fish

2. Make sure your shell is configured to use ``conda activate``. To do so, type ``conda activate``, and one of
two things will happen. Either 1). The ``base`` conda environment will activate, meaning you're good to go, or
2). It will throw some error of some sort, prompting with you with some steps you can take to resolve the issue.

All this being said, it IS possible to work on Augur without using Anaconda to manage the Python environment,
and if you find a workaround that you prefer, by all means, please use that. Just keep in mind that this is what we
officially support and build our installations and ``make`` commands around. Now, on to the fun part!


Augur Installation Instructions
-------------------------------

Clone the repo and install the libraries and tools needed by Augur

.. code:: bash

    git clone https://github.com/chaoss/augur/

    ## Assume you are in the root from which you cloned augur

    cd augur ## To get to augur root, where the make files live

    # If you are going to do active development, please use the dev branch
    git checkout dev

    # Install the Python and Node tools and libraries needed
    sudo make install-dev # some libraries require a root install.

    # Ignore node-pre-gyp install errors asking for cairo library or install cairo library. Augur works either way. 

**Make sure you have a database user that has select access to the
database where you installed `GHTorrent <http://ghtorrent.org/>`__ and
all priviledges on another database for Augur.**

.. code:: sql

    CREATE USER 'augur'@'localhost' IDENTIFIED BY 'password';
    GRANT SELECT ON ghtorrent.* TO 'augur'@'localhost';

    CREATE DATABASE augur;
    GRANT ALL PRIVILEDGES ON augur.* TO 'augur'@'localhost';

Augur runs in an Anaconda environment. To get started, activate the environment and then 
run ``augur run``.

.. code:: bash

    conda activate augur
    augur run

After you run the ``augur run`` command for the first time, a configuration file called ``augur.config.json`` will automatically be generated.

Reference the sample configuration file (``sample.config.json``) on how to 
set up the server, development, and cache options, as well as the plugin connections.

For **all** the API's and visualiazations to work, you will need to include:

-  A `GitHub <https://developer.github.com/v3/>`__ API Key,
-  A connection to a `Facade <https://opendata.missouri.edu>`__ database,
-  A connection to a `GHTorrent <https://ghtorrent.org>`__ database.

For local API testing, you will need a `Postman <https://www.getpostman.com>`__ API key.

**You're ready to rock! To start both the frontend and backend, run:**
``make dev``

macOS High Sierra (and possibly older OS X Versions) Errata:
------------------------------------------------------------

1. If you check the logs/frontend.log and find that "brunch" was not
   found:

   .. code:: bash

       brew install npm
       npm install -g brunch
       brew install yarn

2. If the logs look good but the webpage at localhost:3333 is empty, it
   could be that Yarn installed the wrong version of some libraries. In
   that case:

   .. code:: bash

       cd frontend 
       npm install
