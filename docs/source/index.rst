Augur
==================================

Welcome to Augur's official documentation!

Below is a brief primer on our project and our goals. If you're new to the project, we recommend giving it a once-over as a gentle introduction.
Otherwise, feel free to hop right into the docs!

.. toctree::
   :maxdepth: 2
   
   getting-started/toc
   docker/toc
   development-guide/toc
   rest-api/api
.. library-documentation/toc
.. schema/toc
.. deployment/toc


What is Augur?
~~~~~~~~~~~~~~~~

Augur is a software suite for collecting and measuring structured data about free and open source software (`FOSS <https://en.wikipedia.org/wiki/Free_and_open-source_software>`_) communities. We gather trace data for a group of repositories, normalize it into our data model, and provide a variety of metrics about said data. The structure of our data model enables us to synthesize data across various platforms to provide meaningful context for meaningful questions about the way these communities evolve.

We are a `CHAOSS <https://chaoss.community>`_ project, and many of our metrics are implementations of the metrics defined by our community. You can find more information about how to get involved in our community `here <https://chaoss.community/participate/>`_.

Augur is focused on making sense of data using
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
- `Carter Landis <https://github.com/ccarterlandis>`_

