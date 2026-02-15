Augur Documentation
==================================

:doc:`Welcome! <getting-started/Welcome>`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. toctree::
   :maxdepth: 2

   getting-started/Welcome
   quick-start
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
  :alt: Development guide image overview of augur


What is Augur?
~~~~~~~~~~~~~~~~
Augur is a software tool that helps you collect and measure information about `open source <https://opensource.com/resources/what-open-source>`_ software projects. Augur focuses on collecting data from public git-based code hosting platforms ("Forges") such as GitHub and GitLab to produce data about the health and sustainability of software projects based on the relevant CHAOSS metrics.

The main goal of Augur is to understand how healthy and sustainable a project is. Healthy projects are easier to rely on, and they are important because many software organizations or companies depend on open-source software.

How Augur works
---------------

1. Augur looks at the project’s repositories (the place where the project’s code and files live).
2. It collects data about activity that is happening in the project, including issues, comments, code changes, etc.
3. It organizes this data into a standard format called a data model.
4. Then it calculates metrics that tell you about the project’s health.

Example of a metric: Burstiness
-------------------------------
- Burstiness is one of Augur’s metrics.
- It shows periods when a project has a lot of activity in a short time, followed by periods when activity goes back to normal.
- This helps you see a project’s focus, update patterns, and stability.
- In other words, you can tell how often big changes happen and whether the project works in a steady, predictable way.

Augur calculates many other metrics, which you can see in the `full list <https://chaoss.community/metrics/>`_.

Who develops Augur
--------------------

- Augur is developed as part of CHAOSS (Community Health Analytics in Open Source Software).
- Many of Augur’s metrics come directly from the CHAOSS community.
- If you want to get involved, visit the `CHAOSS website <https://chaoss.community>`_.

See it in action
-------------------

- You can check out Augur live on the `CHAOSS instance <https://ai.chaoss.io>`_.


Current maintainers
--------------------
- `Derek Howard <https://github.com/howderek>`_
- `Andrew Brain <https://github.com/ABrain7710>`_
- `Isaac Milarsky <https://github.com/IsaacMilarky>`_
- `John McGinnes <https://github.com/Ulincys>`_
- `Sean P. Goggins <https://github.com/sgoggins>`_



Former maintainers
--------------------
- `Carter Landis <https://github.com/ccarterlandis>`_
- `Gabe Heim <https://github.com/gabe-heim>`_
- `Matt Snell <https://github.com/Nebrethar>`_
- `Christian Cmehil-Warn <https://github.com/christiancme>`_
- `Jonah Zukosky <https://github.com/jonahz5222>`_
- `Carolyn Perniciaro <https://github.com/CMPerniciaro>`_
- `Elita Nelson <https://github.com/ElitaNelson>`_
- `Michael Woodruff <https://github.com/michaelwoodruffdev/>`_
- `Max Balk <https://github.com/maxbalk/>`_

Contributors
--------------------
- `Dawn Foster <https://github.com/geekygirldawn/>`_
- `Ivana Atanasova <https://github.com/ivanayov/>`_
- `Georg J.P. Link <https://github.com/GeorgLink/>`_

GSoC 2022 participants
-----------------------
- `Kaxada <https://github.com/kaxada>`_
- `Mabel F <https://github.com/mabelbot>`_
- `Priya Srivastava <https://github.com/Priya730>`_
- `Ramya Kappagantu <https://github.com/RamyaKappagantu>`_
- `Yash Prakash <https://gist.github.com/yash-yp>`__

GSoC 2021 participants
-----------------------
- `Dhruv Sachdev <https://github.com/Dhruv-Sachdev1313>`_
- `Rashmi K A <https://github.com/Rashmi-K-A>`_
- `Yash Prakash <https://github.com/yash2002109/>`__
- `Anuj Lamoria <https://github.com/anujlamoria/>`_
- `Yeming Gu <https://github.com/gymgym1212/>`_
- `Ritik Malik <https://gist.github.com/ritik-malik>`_

GSoC 2020 participants
-----------------------
- `Akshara P <https://github.com/aksh555/>`_
- `Tianyi Zhou <https://github.com/tianyichow/>`_
- `Pratik Mishra <https://github.com/pratikmishra356/>`_
- `Sarit Adhikari <https://github.com/sarit-adh/>`_
- `Saicharan Reddy <https://github.com/mrsaicharan1/>`_
- `Abhinav Bajpai <https://github.com/abhinavbajpai2012/>`_

GSoC 2019 participants
-----------------------
- `Bingwen Ma <https://github.com/bing0n3/>`_
- `Parth Sharma <https://github.com/parthsharma2/>`_

GSoC 2018 participants
-----------------------
- `Keanu Nichols <https://github.com/kmn5409/>`_
