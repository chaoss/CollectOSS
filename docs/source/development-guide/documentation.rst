Writing documentation
======================

Currently, we maintain a set of library and usage documentation (which is what you are reading!) that
we update with each release. The following sections briefly outline how to contribute to our documentation.

.. note::

    **All** PRs which require a documentation change will not be merged until that change has been made.

Library and Usage Documentation
--------------------------------

The library documentation is written using `reStructuredText <https://docutils.sourceforge.io/rst.html>`_ for the raw markdown and then built into web pages using `Sphinx <http://www.sphinx-doc.org/en/master/index.html>`_. 

We'll avoid going over reStructuredText in detail here, 
but `here <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`__ is a good reference document.

Similarly, we'll avoid going over Sphinx in great detail as well; `here <http://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`__ is a good reference document for the
most commonly used directives.

Building
~~~~~~~~

To see your changes and make sure everything rendered correctly, First activate the python virtual enivroment and run ``make docs`` in the root 
``augur/`` directory, and then open ``docs/build/html/index.html`` in your web browser to view it. 

.. code-block:: bash
     
    $ cd augur 
    $ python3 -m venv $HOME/.virtualenvs/augur_env
    $ source $HOME/.virtualenvs/augur_env/bin/activate
    $ make docs

Or, you can use the shortcut which does exactly this:

.. code-block:: bash

    # to build and then open to the locally built documentation
    $ make docs-view


After opening it once, Make your changes in the regular ``docs/source`` folder and just run ``make docs`` Everytime you make any change and refresh the browser

.. code-block:: bash

    # after opening the documentation
    $ make docs

Hosting
~~~~~~~
Our documentation is graciously hosted by `Read the Docs <https://readthedocs.org/>`_.

Enabled branches of the main ``chaoss/augur`` repository will each have their own documentation, with the 
default ``main`` corresponding to ``main`` on the readthedocs. The documentation will automatically be 
built and deployed on a push to one of these branches or on any incoming PR, but please don't forget to check before you push!
