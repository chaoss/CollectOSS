Create Your First Metric
===============================

.. role:: raw-html-m2r(raw)
   :format: html

To create your first metric, you'll first need some data. The data served by Augur comes from a variety of sources, including Git repositories, issue trackers, mailing lists, Linux Foundation Badging programs, code coverage analysis tools and others. All of this data is persisted by Augur's workers in our unified data model. Once the data is persisted, it's ready to be served through API endpoints; which can be presented in Augur's frontend or by any other presentation environment chosen.

Once you have this data, fully implementing a new metric in Augur involves four main steps. Two steps are in the backend and two are in the frontend. We will go over each of these in great detail, but here they are at a high level overview:

1. Backend:
	- Pull and transform the result set you need out of the data model
	- Define the API Route for the endpoint
2. Frontend
	- Map the route to the front end in ``augurAPI.js``
	- Reference the endpoint from ``augurAPI.js`` as a datasource in a ``.vue`` card.

.. image:: images/new-metric.png


Backend
--------------------------------------
1. **Metric Implementation**

Any new metric you want to implement must be implemented as a standalone method in ``augur/metrics/<model>/<model>.py``, where ``model`` is the name of the conceptual data model for which the metric provides data. For all model definitions please refer to the documentation in the Python guide_.

.. _guide: python.html

Metrics come in 3 forms: ``repo``, ``repo_group``, and ``other``. All ``repo`` and ``repo_group`` metrics have the following signature:

``metric_name(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None)``

By default, specifying only a ``repo_group_id`` will calculate the ``repo_group`` form of the metric across a collection of repositories, while specifying both a ``repo_id`` and a ``repo_group_id`` will calculate the ``repo`` form of the metric for a single repository. We will see that there are APi endpoint creation helper methods written for these types of metrics later in this guide.

All metrics with methods that deviate from this signature fall under the ``other`` and must be defined more explicity when exposing them through an API enpoint.

All metrics must also return the data as a Pandas ``DataFrame`` for ease of computation and usage.

Consider the following metric implementation as an example:

  .. code-block:: python
    :linenos:

    # in augur.metrics.repo_meta.repo_meta.py
    @annotate(tag='code-changes')
    def code_changes(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None):
        """
        Returns a timeseries of the count of code commits.

        :param repo_group_id: The repository's repo_group_id
        :param repo_id: The repository's repo_id, defaults to None
        :param period: To set the periodicity to 'day', 'week', 'month' or 'year', defaults to 'day'
        :param begin_date: Specifies the begin date, defaults to '1970-1-1 00:00:00'
        :param end_date: Specifies the end date, defaults to datetime.now()
        :return: DataFrame of commits/period
        """
        if not begin_date:
            begin_date = '1970-1-1 00:00:00:00'
        if not end_date:
            end_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        code_changes_SQL = ''

        if not repo_id:
            code_changes_SQL = s.sql.text("""
                SELECT
                    date_trunc(:period, cmt_committer_date::DATE) as commit_date,
                    repo_id,
                    COUNT(cmt_commit_hash) as commit_count
                FROM commits
                WHERE repo_id IN (SELECT repo_id FROM repo WHERE repo_group_id=:repo_group_id)
                AND cmt_committer_date BETWEEN :begin_date AND :end_date
                GROUP BY commit_date, repo_id
                ORDER BY repo_id, commit_date
            """)

            results = pd.read_sql(code_changes_SQL, self.db, params={'repo_group_id': repo_group_id, 'period': period,
                                                                     'begin_date': begin_date, 'end_date': end_date})
            return results

        else:
            code_changes_SQL = s.sql.text("""
                SELECT
                    date_trunc(:period, cmt_committer_date::DATE) as commit_date,
                    COUNT(cmt_commit_hash) as commit_count
                FROM commits
                WHERE repo_id = :repo_id
                AND cmt_committer_date BETWEEN :begin_date AND :end_date
                GROUP BY commit_date
                ORDER BY commit_date
            """)

            results = pd.read_sql(code_changes_SQL, self.db, params={'repo_id': repo_id, 'period': period,
                                                                     'begin_date': begin_date, 'end_date': end_date})
            return results

Let's breakdown this example.

The metric being implemented here is the 'Code Changes' metric. This metric falls into the ``repo_meta`` model, so it will go in ``augur/metrics/commit/commit.py``.

The ``@annotate(tag='code-changes')`` decoration denotes the function as a metric, which is required to let Augur know this is a special type of function.

``def  code_changes(self, repo_group_id, repo_id=None, period='day', begin_date=None, end_date=None)`` defines the function ``code_changes`` that implements the metric 'Code Changes.'

The ``code_changes`` function has two SQL queries that query the Unified Augur Database. One query handles repository groups while the other handles single repositories. The function returns a Pandas ``DataFrame``.

2. **Adding Routes**

After implementing the metric, you must add an API endpoint to access the metric remotely. Routes for the metrics are added in the ``routes.py`` file in the ``augur/metrics/<model>/<model>.py`` directory.
In the ``create_routes`` function in ``routes.py`` file you can add routes using the following two methods:

``server.addRepoGroupMetric(metrics.<metric>, '<endpoint>')`` to add the endpoint ``/repo-groups/:repo_group_id/<endpoint>`` corresponding to the metric implementation function ``<metric>``.
``server.addRepoMetric(metrics.<metric>, '<endpoint>')`` to add the endpoint ``/repo-groups/:repo_group_id/repos/:repo_id/<endpoint>`` corresponding to the metric implementation function ``<metric>``

Consider the following example:

  .. code-block:: python
    :linenos:

      """
      @api {get} /repo-groups/:repo_group_id/code-changes
      @apiName Code Changes
      @apiGroup Evolution
      @apiDescription <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
      @apiParam {String} repo_group_id Repository Group ID
      @apiParam {string} period Periodicity specification. Possible values: 'day', 'week', 'month', 'year'. Defaults to 'day'
      @apiParam {string} begin_date Beginning date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to '1970-1-1 0:0:0'
      @apiParam {string} end_date Ending date specification. Possible values: '2018', '2018-05', '2019-05-01', ..., ' 2017-03-02 05:34:19'. Defaults to current date & time.
      @apiSuccessExample {json} Success-Response:
                      [
                          {
                              "commit_date": "2018-01-01T00:00:00.000Z",
                              "repo_id": 1,
                              "commit_count": 5140
                          },
                          {
                              "commit_date": "2019-01-01T00:00:00.000Z",
                              "repo_id": 1,
                              "commit_count": 711
                          },
                          {
                              "commit_date": "2015-01-01T00:00:00.000Z",
                              "repo_id": 25001,
                              "commit_count": 1071
                          }
                      ]
      """
      server.addRepoGroupMetric(metrics.code_changes, 'code-changes')


The last line ``server.addRepoGroupMetric(metrics.code_changes, 'code-changes')`` is what actually creates the ``/repo-groups/:repo_group_id/code-changes`` endpoint and links it to ``code_changes`` metric implementation function.
The rest is just annotation used to create documentation.

After you've completed these two steps, run ``make dev`` in the root of your directory and navigate to ``https:localhost:<port>api/unstable/repo-groups/:repo_group_id/code-changes`` where ``<port>`` is the port of backend is running on (default ``5000``) and ``repo_group_id`` is the ID of the repo group about which you wish to learn.

The rest of the process can be found in the frontend doc_.

.. _doc: frontend.html

.. 3.   example file 3: 'augurAPI.js' in the ``augur/frontend/app/`` directory needs to have the the metric from ``routes.py`` mapped to an API endpoint that the frontend will then access.


..    * Metrics from the facade.py that take a git url should go under the //GIT section in this file
..    * Most of your metrics are going to belong in the //GROWTH, MATURITY AND DECLINE section.

.. .. code-block:: javascript
..    :linenos:

..      // IN THIS SECTION of augurAPI.js DEVELOPER NOTE

..      if (repo.owner && repo.name) {
..       // DIVERSITY AND INCLUSION
..       // GROWTH, MATURITY, AND DECLINE

..       // FIND THE RIGHT SECTION, like "GROWTH, MATURITY AND DECLINE" and ADD YOUR code
..       Timeseries(repo, 'closedIssues', 'issues/closed')
..       Timeseries(repo, 'closedIssueResolutionDuration', 'issues/time_to_close')
..       Timeseries(repo, 'codeCommits', 'commits')
..       // Timeseries(repo, 'codeReviews', 'code_reviews')

..       // THIS IS THE NEW METRIC IN OUR EXAMPLE
..       Timeseries(repo, 'codeReviewIteration', 'code_review_iteration')
..      }


.. 4. Example file 4: `ExperimentalCard.vue` in the `augur/frontend/app/components/` directory. We will need to import and insert a chart component that we will be creating next or a chart component that already exists in the `augur/frontend/app/components/charts/ ` directory.

..       In the `<script>` section of `ExperimentalCard.vue`, we must import the chart file and add it to the `components` section under `module.exports` like this:

.. .. code-block::
..    :linenos:

..       import ExampleChart from `./charts/ExampleChart`

..       import DynamicLineChart from './charts/DynamicLineChart'
..       import BubbleChart from './charts/BubbleChart'
..       import StackedBarChart from './charts/StackedBarChart'
..       import DualAxisContributions from './charts/DualAxisContributions'

..       module.exports = {
..         data() {
..           return {
..             colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
..           }
..         },
..         components: {
..           ExampleChart,

..           DynamicLineChart,
..           BubbleChart,
..           StackedBarChart,
..           DualAxisContributions
..         }
..       }


.. **TODO** Can we keep the example from above in place?


.. 5. Example file 5: **TODO** <\ :raw-html-m2r:`<FILL IN FILE NAME and PATH>`\ > We insert the ``ExampleChart`` component with our endpoint name (\ ``closedIssues``\ ) defined as the ``source`` property (prop) of the component (Vue converts a string name like 'ExampleChart' to 'example-chart' to be used as an html tag):

.. .. code-block:: html
..    :linenos:


..       <example-chart source="closedIssues"
..                           title="Closed Issues / Week "
..                           cite-url=""
..                           cite-text="Closed Issues">
..       </example-chart>


.. 6. You will need to create a chart file. **TODO** << Where? What will it be called? What example are we using? >> Here is an example of a chart file that calls the endpoint that is passed as the ``source`` property. The template section holds the vega-lite tag that renders the chart. The Vega-lite ``spec`` is being bound to what is being returned by the ``spec()`` method inside the ``computed`` properties (\ ``:spec="spec"``\ ), and the ``data`` being used for the chart is bound to the ``values`` array being returned by the ``data()`` method (\ ``:data="values"``\ ):

.. **TODO** Where it goes in this file. Same file?

.. .. code-block:: html
..    :linenos:

..       <template>
..         <div ref="holder" style="position: relative; z-index: 5">
..           <div class="chart">
..             <h3 style="text-align: center">{{ title }}</h3>
..             <vega-lite :spec="spec" :data="values"></vega-lite>
..             <p> {{ chart }} </p>
..           </div>
..         </div>
..       </template>

.. **TODO** Where it goes in this file. Same file?

.. .. code-block:: javascript
..    :linenos:

..       import { mapState } from 'vuex'
..       import AugurStats from 'AugurStats'

..       export default {
..         props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
..         data() {
..           return {
..             values: [],
..           }
..         },
..         computed: {
..           repo() {
..             return this.$store.state.baseRepo
..           },
..           spec() {
..               // IF YOU WANT TO CALL YOUR ENDPOINT IN THE CHART FILE, THIS IS WHERE/HOW YOU SHOULD DO IT:
..             let repo = window.AugurAPI.Repo({ githubURL: this.repo })
..             repo[this.source]().then((data) => {
..                // you can print your data in a console.log() to make                   // sure the endpoint is returning what it needs to
..               // console.log("HERE", data)
..               this.values = data
..             })
..             //FINISH CALLING ENDPOINT

..             // THIS IS A SAMPLE 'spec', SPECS ARE WHAT CREATE THE VEGA-LITE FILE,
..             // YOU CAN PLAY WITH SAMPLE SPEC OF A LINE CHART AT:
..             // https://vega.github.io/editor/#/examples/vega-lite/line
..             // AND SEE THE DATA THAT THEY ARE USING AT:
..             // https://vega.github.io/vega-lite/data/stocks.csv
..             let config = {
..               "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
..               "width": 950,
..               "height": 300,
..               "mark": "line",
..               "encoding": {
..                 "x": {
..                   "field": "date", "type": "temporal",
..                 },
..                 "y": {
..                   "field": "value","type": "quantitative",
..                 },
..               }
..             }
..             return config
..           }
..         },
..         methods: {
..           //define any methods you may need here
..           //you can call them anywhere with: this.methodName()
..         }
..       }
