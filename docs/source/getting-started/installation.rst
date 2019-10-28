============================
Installation
============================

Dependencies
----------------

Backend and data collection:

-  `Git client <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`__
-  `GitHub Access Token <https://github.com/settings/tokens>`__ (no write access required)
-  `Python 3.6 or higher <https://www.python.org/downloads/>`__
-  `pip <https://pip.pypa.io/en/stable/installing/>`__
-  A `PostgreSQL 11 <https://www.postgresql.org/download/>`__ installation.

Note: in most cases, the installation process will automatically create the schema for you. However, if you so choose,
you can in `install it yourself <../architecture/data-model.html#creating-the-schema>`_.

Frontend:

-  `Vue.js <https://vuejs.org/>`__
-  `vue-cli <https://cli.vuejs.org/>`__
-  `node <https://nodejs.org/en/>`__
-  `npm <https://www.npmjs.com/>`__

0. Clone the repository.

.. code:: bash

   git clone https://github.com/chaoss/augur.git
   cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+ - on most systems, this is ``python3``,
   but yours may differ.

.. code:: bash

    # to create the environment
    python3 -m venv $HOME/.virtualenvs/augur_env

    # to activate it in bash
    source $HOME/.virtualenvs/augur_env/bin/activate

2. Begin the installation process.

.. code:: bash

   make install

This process will:

- install Augur’s backend and its dependencies 
- install the included data collection workers and their dependencies
- generate documentation
- set up the configuration file
- optionally install Augur’s frontend and its dependencies 

Now that you've got everything installed, it's time to test it out!