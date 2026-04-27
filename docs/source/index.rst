CollectOSS Documentation
==================================

:doc:`Welcome! <getting-started/Welcome>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   getting-started/Welcome
   quick-start
   about-augur/toc
   deployment/toc
   getting-started/toc
   development-guide/toc
   rest-api/api
   docker/toc
   schema/toc
   login
   procedures/toc
.. 

..
  deployment/toc
..
  schema/toc

.. image:: development-guide/images/augur-architecture-2.png
  :width: 700
  :alt: Development guide image overview of CollectOSS


What is CollectOSS?
~~~~~~~~~~~~~~~~
CollectOSS is a software tool that helps you collect and measure information about `open source <https://opensource.com/resources/what-open-source>`_ software projects. CollectOSS focuses on collecting data from public git-based code hosting platforms ("Forges") such as GitHub and GitLab to produce data about the health and sustainability of software projects based on the relevant CHAOSS metrics.

The main goal of CollectOSS is to understand how healthy and sustainable a project is. Healthy projects are easier to rely on, and they are important because many software organizations or companies depend on open-source software.

How CollectOSS works
---------------

1. CollectOSS looks at the project’s repositories (the place where the project’s code and files live).
2. It collects data about activity that is happening in the project, including issues, comments, code changes, etc.
3. It organizes this data into a standard format called a data model.
4. Then it calculates metrics that tell you about the project’s health.

Example of a metric: Burstiness
-------------------------------
- Burstiness is one of CollectOSS’s metrics.
- It shows periods when a project has a lot of activity in a short time, followed by periods when activity goes back to normal.
- This helps you see a project’s focus, update patterns, and stability.
- In other words, you can tell how often big changes happen and whether the project works in a steady, predictable way.

CollectOSS calculates many other metrics, which you can see in the `full list <https://chaoss.community/metrics/>`_.

Who develops CollectOSS
--------------------

- CollectOSS is developed as part of CHAOSS (Community Health Analytics in Open Source Software).
- Many of CollectOSS’s metrics come directly from the CHAOSS community.
- If you want to get involved, visit the `CHAOSS website <https://chaoss.community>`_.

For the current list of CollectOSS maintainers and contributors, please refer to the
`CREDITS.md <https://github.com/chaoss/collectoss/blob/main/CREDITS.md>`_
file.

See it in action
-------------------

- You can check out CollectOSS live on the `CHAOSS instance <https://ai.chaoss.io>`_.
