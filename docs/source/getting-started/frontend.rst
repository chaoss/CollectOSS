Augur's Frontend
=================

To compile Augur's frontend for deployment in a production environment (i.e., behind an nginx server), you must go through the folowing steps
    1. Run ``augur config init-frontend`` from within your python virtual environment. 
    2. Enter Augur's home directory 
    3. Run ``npm install``, and then ``npm run build`` in the frontend directory. 
    4. After that, follow the instructions for configuring Augur behind Nginx. 

Augur's frontend source code can be found at ``<root_augur_directory>/frontend/src/``. It uses Vue.js as its primary architecture framework, and Vega/Vega-Lite for its visualizations. It's configured via the ``frontend.config.json`` file in ``<root_augur_directory>/frontend/``.

**THIS SECTION IS UNDER CONSTRUCTION.**

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues
