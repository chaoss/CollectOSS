Installation
=============================================

Local Installation
------------------------------------

1. Install Dependencies (OS Specific Instructions Below)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Anaconda
-  NodeJS Version 8.0 or newer, which includes ``npm``

Also remember the database dependency in the `README <http://ghtorrent.org/msr14.html>`__.

1. `Dependency Installation for Ubuntu <#Ubuntu>`__
2. `Dependency Installation for Fedora <#Fedora>`__
3. `Dependency Installation for OS X <#MacOSX>`__
4. `Install Augur <#Install>`__

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

    # [Install Augur](#Install)

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

    # [Install Augur](#Install)

Mac OSX Dependency Installation Instructions
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

    # [Install Augur](#Install)

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
run ``augur``.

.. code:: bash

    conda activate augur
    augur

After you run the ``augur`` command for the first time, a configuration file called ``augur.config.json`` will automatically be generated.

Reference the sample configuration file (``sample.config.json``) on how to 
set up the server, development, and cache options, as well as the plugin connections.

For **all** the API's and visualiazations to work, you will need to include:

-  A `GitHub <https://developer.github.com/v3/>`__ API Key,
-  A connection to a `Facade <https://opendata.missouri.edu>`__ database,
-  A connection to a `GHTorrent <https://ghtorrent.org>`__ database.

For local API testing, you will need a `Postman <https://www.getpostman.com>`__ API key.

**You're ready to rock! To start both the frontend and backend, run:**
``make dev``
