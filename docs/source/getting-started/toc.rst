==================
Getting Started
==================

What is Augur?
~~~~~~~~~~~~~~~~

Augur is software focused on building **human centered open source software
health metrics** defined by collaborations with the Linux Foundation's
`CHAOSS Project <http://chaoss.community>`__ and other open source
stakeholders. Augur is software focused on making sense of data using
four key **human centered data science** strategies: 

1. **Enable comparisons**. People navigate complex unknowns analogically. Let folks see how their project compares with others they are familiar with. This is not ranking - if you start thinking about "metrics" like "rankings," you are probably going to create suboptimal metrics. 
2. Make **time a fundamental dimension in all metrics** from the start. "Point in time scores" are useful. They are more useful if we can see how they compare historically and can be used to anticipate a trajectory. 
3. All **data** driving visualizations **should be downloadable** as ``.csv`` or some other data exchange format. People trust metrics when they can see the underlying data, and proving traceability back to the CHAOSS Project's metrics standards requires easy transparency. 
4. Make **all the visualizations downloadable as .svg's**. People want to put your visualizations in reports to explain things they care about. And ask for money. Give them the tools. That's what makes folks care about metrics.

Our core team has a long standing interest in social computing, software engineering measurement and the ethical instrumentation of online human behavior.

Our members:

- `Derek Howard <https://howderek.com>`_
- `Sean P. Goggins <http://www.seangoggins.net>`_
- `Matt Germonprez <https://goo.gl/E87KdK>`_
- `Gabe Heim <https://github.com/gabe-heim>`_
- `Matt Snell <https://github.com/Nebrethar>`_
- `Jonah Zukosky <https://github.com/jonahz5222>`_
- `Carolyn Perniciaro <https://github.com/CMPerniciaro>`_
- `Elita Nelson <https://github.com/ElitaNelson>`_
- `Michael Woodruff <https://github.com/michaelwoodruffdev/>`_
- `Max Balk <https://github.com/maxbalk/>`_
- `Andrew Brain <https://github.com/ABrain7710>`_
- `Carter Landis <https://carterlandis.com>`_


Overview
~~~~~~~~~~~~~~~~

This documentation is intended as an entry-level introduction for the Augur project, complete with installation, usage, and configuration guides. To set up
Augur, we'll need to do a few things, namely:

- Setup a PostgreSQL 10 database instance to store the data collected by Augur
- Install Augur's data collection workers and metrics API
- Configure Augur to collect data
- Start Augur using the built-in command line interface (CLI)

If you want to get Augur up and running locally just to test it out, we have a `Docker image available <../docker/toc.html>`_. If you're looking to install Augur on a server or for development, follow the instructions below.

.. toctree::
   :maxdepth: 1

   database
   installation
   collecting-data
   configuration-file-reference
   command-line-interface/toc