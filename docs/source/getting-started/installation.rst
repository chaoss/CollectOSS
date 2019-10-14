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
   the correct ``python`` command for your installation of Python 3.6+.

.. code:: bash

    # to create the environment
    python -m venv $HOME/.virtualenvs/augur_env

    # to activate it in bash
    source $HOME/.virtualenvs/augur_env/bin/activate

Note: please do not install it in the Augur directory itself, as if you do so it will get checked our repository.

2. Begin the installation process.

.. code:: bash

   make install

This procces will: - install augur’s backend and its dependencies -
install data collection workers and their dependencies (you will be able
to select which workers you would like: we recommend all of them) -
optionally install augur’s frontend and its dependencies - generate
documentation - prompt the user for **connection credentials for a
Postgres 11 installation**

After Augur is installed, given that you provided a correct set of
credentials you should have a functioning version of Augur.

