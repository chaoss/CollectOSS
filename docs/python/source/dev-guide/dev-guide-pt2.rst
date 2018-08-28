Developer Guide Part 2 - The Frontend
=====================================

Structure
---------

Augur uses Vue.js, MetricsGraphics, and Kube for its frontend. The
frontend is stored in the ``frontend`` directory, but the parts that are
relevant to adding new metrics are in the ``frontend/app/`` directory,
which contains the following parts: \* ``frontend/app/AugurAPI.js``
which interfaces with the backend \* ``frontend/app/AugurStats.js``
which performs statistical operations on the data \*
``frontend/app/Augur.js`` which renders the page \*
``frontend/app/assets/`` which contains the assets, such as images, for
the frontend \* ``frontend/app/include/`` which contains the Kube and
MetricsGraphics resources \* ``frontend/styles/`` which contains the
stylesheet for Augur \* ``frontend/components/`` which contains the
Vue.js components (referred to a 'Cards'\*) \*
``frontend/components/charts/`` contains the different chart templetes
\* ``frontend/components/BaseRepoActivityCard.vue`` contains the repo
activity time series charts

\* The Cards that have the name of a metric grouping are each their own
separate tab; pay attention to which card you are adding your graph to!

How to add a new timeseries metric
----------------------------------

In ``frontend/app/AugurAPI.js``, add an attribute to the repo class that
holds a timeseries object at the end of the file like this:

.. code:: javascript

    Timeseries(repo, <endpointName>, <endpoint_name>)

So if your endpoint name is ``foo_bar`` then the attribute would be:

.. code:: javascript

    Timeseries(repo, 'fooBar', 'foo_bar')

How to add a new nontimeseries metric
-------------------------------------

In ``frontend/app/AugurAPI.js``, add an attribute to the repo class that
holds an endpoint object at the end of the file like this:

.. code:: javascript

    Endpoint(repo, <endpointName>, <endpoint_name>)

So if your endpoint name is ``foo_bar`` then the attribute would be:

.. code:: javascript

    Endpoint(repo, 'fooBar', 'foo_bar')

Adding a chart
--------------

**This process is exactly the same whether your metric is a timeseries
or not.**

If your metric is a new Growth-Maturity-Decline metric, in
``frontend/app/components/GrowthMaturityDeclineCard.vue``, in the
template in the section tag, add a div like this:

.. code:: html

        <div class="row">
          <div class="col col-'width'>
            <line-chart source="endpointName" 
                        title="Chart title" 
                        cite-url="Optional link to explanation"
                        cite-text="Optional link title">
            </line-chart>
          </div>

(Note the ``source`` attribute; this is the ``endpointName`` you defined
in the previous step. So, if your ``endpointName`` was ``fooBar``, the
source attribute would look like ``source="fooBar"`` - don't forget the
quotes! )

The recommended width is 6 for half width and 12 for full width. So if I
wanted to add the ``foo_bar``\ chart, it would look like this:

.. code:: html

        <div class="row">
          <div class="col col-12>
            <line-chart source="fooBar" 
                        title="Foo Bar" 
                        cite-url="https://foobar.com"
                        cite-text="Link to foo bar explanation">
            </line-chart>
          </div>

Adding Comparison Functionality
-------------------------------

In ``frontend/app/components/BaseRepoActivityCard.vue``, in the template
in the section tag, add a div like this:

.. code:: html

        <div class="row">
          <div class="col col-'width'>
            <line-chart source="endpointName" 
                        title="Chart title" 
                        cite-url="Optional link to explanation"
                        cite-text="Optional link title"
                        v-bind:compared-to="comparedTo">
            </line-chart>
          </div>

The recommended width is 6 for half width and 12 for full width. So if I
wanted to add the ``foo_bar``\ chart, it would look like this:

.. code:: html

        <div class="row">
          <div class="col col-12>
            <line-chart source="fooBar" 
                        title="Foo Bar" 
                        cite-url="https://foobar.com"
                        cite-text="Link to foo bar explination"
                        v-bind:compared-to="comparedTo">
            </line-chart>
          </div>

Adding a chart type
-------------------

In the ``frontend/app/components/charts`` directory, define a new chart
for the metric.

In the appropriate Card, import the chart at the bottom and then export
it so that Vue can use it.

In the same file, in the template in the section tag, add a div like
this:

.. code:: html

        <div class="row">
          <div class="col col-'width'">
            <chart-type source="attributeName"
                        title="Chart title"
                        cite-url="Optional link to explanation"
                        cite-text="Optional link title">
            </chart-type>
          </div>
    ...
    import ChartType from './charts/ChartType'

    module.exports = {
      components: {
        ChartType
      }
    };

The recommended width is 6 for half width and 12 for full width. So if I
wanted to add the ``foo_bar`` chart, it would look like this

.. code:: html

        <div class="row">
          <div class="col col-12">
            <foo-bar source="fooBar"
                        title="Foo Bar"
                        cite-url="https://foobar.com"
                        cite-text="Link to foo bar explanation">
            </foo-bar>
          </div>
    ...
    import FooBar from './charts/FooBar'

    module.exports = {
      components: {
        FooBar
      }
    };
