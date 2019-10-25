Starting Data Collection Workers
================================

Workers are continuous collection processes that populate parts of Augur's data model. Each worker follows a consistent design that includes: 

1. Having the housekeeper notify the broker of what work needs to be done (1), the worker notifying the housekeeper that its ready to work when it starts (2), the broker passing work to the worker (3), and the worker letting the broker know when its finished (4). 

.. image:: workflow.png
  :alt: Housekeeper, Broker & Worker  

2. Until the worker starts, the broker listens for the worker on a port specified in the worker block of the augur.config.json file. 
   

3. The data collected by the worker is determined by the models listed in the housekeeper block of the augur.config.json file. 


.. _workers-dir:

--------------------
Locating the Workers: Augur's Oompa Loompas 
--------------------
.. image:: workers-dir.png
  :alt: Augur Workers 

.. note:: 

  You'll likely see some linting warnings in the frontend section
  (indicated here by the …). Don’t worry about them: it’s the last 3 lines
  that indicate success.