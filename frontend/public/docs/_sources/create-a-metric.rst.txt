Create Your First Metric
===============================

.. role:: raw-html-m2r(raw)
   :format: html

Building a new metric in Augur involves four main steps. Two steps are in the "back end" and two are in the "front end". 

1. Backend: 
	- Pull the result set you need out of the Augur Unified Schema. 
	- Define the API Route for the endpoint. 
2. Frontend
	- Map the route to the front end in `augurAPI.js`
	- Reference the endpoint from `augurAPI.js` as a datasource in a .VUE card. 
	  

.. image:: images/new-metric.png 
*The data served by Augur comes from a variety of sources, including .git repositories, issue trackers, mailing lists, Linux Foundation Badging programs, code coverage analysis tools and others.  All of the data is persisted by Augur's workers in a unified data model. Once the data is persisted, its ready to be served as API endpoints; which can be presented in Augur's front end or by any other presentation environment chosen.  There are four basic steps, two in the front end, and two in the backend.  In the backend, there's a <datasource>.py file in the `augur/datasources/<data-source>/` directory. Several are included, like `ghtorrent`, `facade`, `augurDB` and others. Look in the `datasources` directory for specific existing implementations. API Endpoints are served by the `routes.py` file in each `<data-source>` directory. Once the API "exists", the endpoint can be mapped in Augur's frontend through the `augurAPI.js` file in `augur/frontend/app/`. VUE cards present that data graphically in `<card>.vue` files.*

Follow the Steps 
--------------------------------------


1. augur/augur/datasources/\ :raw-html-m2r:`<directory for data source>`

   #. example: ghtorrent
   #. example file 1: ghtorrent.py

      * create a new function that has the sql query to the database, or API call to GitHub or whatever. But if you're in ``ghtorrent.py`` (or ``facade.py``\ ), its a sql query. Here's an example breakdown: 

        * ``@annotate(tag='code-review-iteration') makes the function visible in metrics-status``

          * ``def code_review_iteration..`` is the name of the function called in ``routes.py`` **in the same data source folder** (which is ``augur/augur/datasources/ghtorrent`` in our example

.. code-block:: python
   :linenos:

   @annotate(tag='code-review-iteration')
           def code_review_iteration(self, owner, repo=None):
           """
           Timeseries of the count of iterations (being closed and reopened) that a merge request (code review) goes through until it is finally merged

           :param owner: The name of the project owner or the id of the project in the projects table of the project in the projects table. Use repoid() to get this.
           :param repo: The name of the repo. Unneeded if repository id was passed as owner.
           :return: DataFrame with iterations/issue for each issue that week
           """
           repoid = self.repoid(owner, repo)

           codeReviewIterationSQL = s.sql.text("""
           SELECT
               DATE(issues.created_at) AS "created_at",
               DATE(pull_request_history.created_at) AS "merged_at",
               issues.issue_id AS "issue_id",
               pull_request_history.pull_request_id AS "pull_request_id",
               pull_request_history.action AS "action",
               COUNT(CASE WHEN action = "closed" THEN 1 ELSE NULL END) AS "iterations"
           FROM issues, pull_request_history
           WHERE find_in_set(pull_request_history.action, "closed,merged")>0
           AND pull_request_history.pull_request_id IN(
               SELECT pull_request_id
               FROM pull_request_history
               WHERE pull_request_history.action = "closed")   #go by reopened or closed??? (min: completed 1 iteration and has started another OR min: completed 1 iteration)
           AND pull_request_history.pull_request_id = issues.issue_id
           AND issues.pull_request = 1
           AND issues.repo_id = :repoid
           GROUP BY YEARWEEK(issues.created_at) #YEARWEEK to get (iterations (all PRs in repo) / week) instead of (iterations / PR)?
           """)

           df = pd.read_sql(codeReviewIterationSQL, self.db, params={"repoid": str(repoid)})
           return pd.DataFrame({'date': df['created_at'], 'iterations': df['iterations']})

	* Need the New API Documentation Here. 

`server.py`

.. code-block:: python 
	:linenos:

	    def addRepoGroupMetric(self, function, endpoint, **kwargs):
	        """Simplifies adding routes that accept repo_group_id"""
	        endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/{endpoint}'
	        self.app.route(endpoint)(self.routify(function, 'repo_group'))
	        self.updateMetricMetadata(function, endpoint, **kwargs)

	    def addRepoMetric(self, function, endpoint, **kwargs):
	        """Simplifies adding routes that accept repo_group_id and repo_id"""
	        endpoint = f'/{self.api_version}/repo-groups/<repo_group_id>/repos/<repo_id>/{endpoint}'
	        self.app.route(endpoint)(self.routify(function, 'repo'))
	        self.updateMetricMetadata(function, endpoint, **kwargs)



2. example file 2: ``routes.py`` in the same directory, ``augur/augur/datasources/ghtorrent/``

   * ``server.addTimeseries`` (most of the below is annotation. The very last line is what makes it actually work.);;;;

.. code-block:: python
   :linenos:

       """
       @api {get} /:owner/:repo/timeseries/code_review_iteration Code Review Iteration
       @apiName code-review-iteration
       @apiGroup Growth-Maturity-Decline
       @apiDescription <a href="com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md">CHAOSS Metric Definition</a>. Source: <a href="http://ghtorrent.org/">GHTorrent</a>

       @apiParam {String} owner Username of the owner of the GitHub repository
       @apiParam {String} repo Name of the GitHub repository

       @apiSuccessExample {json} Success-Response:
                           [
                               {
                                   "date": "2012-05-16T00:00:00.000Z",
                                   "iterations": 2
                               },
                               {
                                   "date": "2012-05-16T00:00:00.000Z",
                                   "iterations": 1
                               }
                           ]
       """
       server.addTimeseries(ghtorrent.code_review_iteration, 'code_review_iteration')


3.   example file 3: 'augurAPI.js' in the ``augur/frontend/app/`` directory needs to have the the metric from ``routes.py`` mapped to an API endpoint that the frontend will then access. 


   * Metrics from the facade.py that take a git url should go under the //GIT section in this file
   * Most of your metrics are going to belong in the //GROWTH, MATURITY AND DECLINE section. 

.. code-block:: javascript
   :linenos:

     // IN THIS SECTION of augurAPI.js DEVELOPER NOTE

     if (repo.owner && repo.name) {
      // DIVERSITY AND INCLUSION
      // GROWTH, MATURITY, AND DECLINE

      // FIND THE RIGHT SECTION, like "GROWTH, MATURITY AND DECLINE" and ADD YOUR code
      Timeseries(repo, 'closedIssues', 'issues/closed')
      Timeseries(repo, 'closedIssueResolutionDuration', 'issues/time_to_close')
      Timeseries(repo, 'codeCommits', 'commits')
      // Timeseries(repo, 'codeReviews', 'code_reviews')

      // THIS IS THE NEW METRIC IN OUR EXAMPLE
      Timeseries(repo, 'codeReviewIteration', 'code_review_iteration')
     }


4. Example file 4: `ExperimentalCard.vue` in the `augur/frontend/app/components/` directory. We will need to import and insert a chart component that we will be creating next or a chart component that already exists in the `augur/frontend/app/components/charts/ ` directory.

      In the `<script>` section of `ExperimentalCard.vue`, we must import the chart file and add it to the `components` section under `module.exports` like this: 

.. code-block::
   :linenos:

      import ExampleChart from `./charts/ExampleChart`

      import DynamicLineChart from './charts/DynamicLineChart'
      import BubbleChart from './charts/BubbleChart'
      import StackedBarChart from './charts/StackedBarChart'
      import DualAxisContributions from './charts/DualAxisContributions'

      module.exports = {
        data() {
          return {
            colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
          }
        },
        components: {
          ExampleChart,

          DynamicLineChart,
          BubbleChart,
          StackedBarChart,
          DualAxisContributions
        }
      }


**TODO** Can we keep the example from above in place? 


5. Example file 5: **TODO** <\ :raw-html-m2r:`<FILL IN FILE NAME and PATH>`\ > We insert the ``ExampleChart`` component with our endpoint name (\ ``closedIssues``\ ) defined as the ``source`` property (prop) of the component (Vue converts a string name like 'ExampleChart' to 'example-chart' to be used as an html tag):

.. code-block:: html
   :linenos:


      <example-chart source="closedIssues"
                          title="Closed Issues / Week "
                          cite-url=""
                          cite-text="Closed Issues">
      </example-chart>


6. You will need to create a chart file. **TODO** << Where? What will it be called? What example are we using? >> Here is an example of a chart file that calls the endpoint that is passed as the ``source`` property. The template section holds the vega-lite tag that renders the chart. The Vega-lite ``spec`` is being bound to what is being returned by the ``spec()`` method inside the ``computed`` properties (\ ``:spec="spec"``\ ), and the ``data`` being used for the chart is bound to the ``values`` array being returned by the ``data()`` method (\ ``:data="values"``\ ):

**TODO** Where it goes in this file. Same file? 

.. code-block:: html
   :linenos:

      <template>
        <div ref="holder" style="position: relative; z-index: 5">
          <div class="chart">
            <h3 style="text-align: center">{{ title }}</h3>
            <vega-lite :spec="spec" :data="values"></vega-lite>
            <p> {{ chart }} </p>
          </div>
        </div>
      </template>

**TODO** Where it goes in this file. Same file? 

.. code-block:: javascript
   :linenos:

      import { mapState } from 'vuex'
      import AugurStats from 'AugurStats'

      export default {
        props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
        data() {
          return {
            values: [],
          }
        },
        computed: {
          repo() {
            return this.$store.state.baseRepo
          },
          spec() {
              // IF YOU WANT TO CALL YOUR ENDPOINT IN THE CHART FILE, THIS IS WHERE/HOW YOU SHOULD DO IT:
            let repo = window.AugurAPI.Repo({ githubURL: this.repo })
            repo[this.source]().then((data) => {
               // you can print your data in a console.log() to make                   // sure the endpoint is returning what it needs to
              // console.log("HERE", data)
              this.values = data
            })
            //FINISH CALLING ENDPOINT

            // THIS IS A SAMPLE 'spec', SPECS ARE WHAT CREATE THE VEGA-LITE FILE, 
            // YOU CAN PLAY WITH SAMPLE SPEC OF A LINE CHART AT: 
            // https://vega.github.io/editor/#/examples/vega-lite/line
            // AND SEE THE DATA THAT THEY ARE USING AT:
            // https://vega.github.io/vega-lite/data/stocks.csv
            let config = {
              "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
              "width": 950,
              "height": 300,
              "mark": "line",
              "encoding": {
                "x": {
                  "field": "date", "type": "temporal",
                },
                "y": {
                  "field": "value","type": "quantitative",
                },
              }
            }
            return config
          }
        },
        methods: {
          //define any methods you may need here
          //you can call them anywhere with: this.methodName()
        }
      }
