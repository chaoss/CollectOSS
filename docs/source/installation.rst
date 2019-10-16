============================
Installation
============================

0. Clone the repository.

.. code:: bash

   git clone https://github.com/chaoss/augur.git
   cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+

Example\:

.. code:: bash

    # create the virtual environment
    python -m venv $HOME/.virtualenvs/augur_env

    # activate the virtual environment
    source $HOME/.virtualenvs/augur_env/bin/activate

Note: please do not install it in the Augur directory itself, as if you do so it will get checked our repository.

2. Begin the installation process.

.. code:: bash

   make install

This procces will: 

- install Augur’s backend and its dependencies 
- install data collection workers and their dependencies
- optionally install augur’s frontend and its dependencies 
- set up the user's configuration file