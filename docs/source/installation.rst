============================
Installation
============================

0. Clone the repository.

.. code:: bash

   git clone https://github.com/chaoss/augur.git
   cd augur/

1. Create a virtual environment in your home environment. Be sure to use
   the correct ``python`` command for your installation of Python 3.6+

.. code:: bash

   python -m venv $HOME/.virtualenvs/augur_env
   source $HOME/.virtualenvs/augur_env/bin/activate
   # if you installed it somewhere else this path will be different

Note: please do not install it in the Augur directory itself, as if you do so it will get checked our repository.

2. Bring the installation process.

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

