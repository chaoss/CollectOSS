.. Augur documentation master file, created by
   sphinx-quickstart on Tue Oct 24 12:27:08 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Augur
==================================

Augur is a software suite that provides open source health and sustainability metrics through a web app, REST API, and Python library. See :doc:`architecture` for more information about our architecture. 

The latest version of Augur includes an :doc:`images/Augur-Unified-Data-Model` that brings together data from : 


1. git repositories, including GitHub
2. issue trackers
3. mailing lists
4. library dependency trees
5. the Linux Foundation's badging program
6. code complexity and contribution counting ... and MUCH MUCH MORE. 
   

What is Augur?
============================================

Our project is focused on building **human centered open source software
health metrics** defined by collaborations with the Linux Foundation's
`CHAOSS Project <http://chaoss.community>`__ and other open source
stakeholders. augur is software focused on making sense of data using
Four key **human centered data science** strategies: 

1. **Enable comparisons**. People navigate complex unknowns analogically. Let folks see how their project compares with others they are familiar with. - This is not ranking - If you start thinking about "metrics" like "rankings", you are probably going to create suboptimal metrics. 
2. Make **time a fundamental dimension in all metrics** from the start. "Point in time scores" are useful. They are more useful if we can see how they compare historically and can be used to anticipate a trajectory. 
3. All **data** driving visualizations **should be down-loadable** as a .csv or other data exchange format. This is because - People trust metrics when they can see the underlying data - Proving traceability back to the CHAOSS Project's metrics standards requires easy transparency. 
4. Make **all the visualizations downloadable as .svg's**. People want to put your visualizations in reports to explain things they care about. And ask for money. Give them the tools. That's what makes folks care about metrics.

Our core team has a long standing interest in social computing, software engineering measurement and the ethical instrumentation of online human behavior.

.. toctree::
   :maxdepth: 1

   installation
   create-a-metric
   
   dev-guide-toc
   deployment
   architecture
   python
   

   docker-install
   windows-install

   ghtorrent-restore
   use-cases-toc


