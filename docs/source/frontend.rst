==================================
Augur Frontend
==================================

Please note: anyone interested in contributing to the frontend should
read up on the ``Vue`` and ``Vuex`` documentations. This document
will briefly go over some ways the Augur frontend interacts with
these tools but to list every way Augur interacts with these modules
then we would essentially be duplicating their documentation.

If you want to contribute to the frontend, installing
``Vue Devtools`` is also a huge help.

==================================
The Basics
==================================

Adding visualizations
----------------------------

Chart components are stored in ``frontend/src/components/charts``.
``AugurAPI.ts`` is where current available endpoints are stored and
the names of how they should be called (see “Calling an endpoint”
below).
Examples: ``SparkChart.vue``, ``InsightChart.vue``

-  Adding an endpoint

``AugurAPI.ts`` is where current available endpoints are stored.

Inside the ``initialDBMetric`` methods of the ``Repo`` and
``RepoGroup`` classes (depending on what you want the endpoint
to be called on, usually a ``Repo``)
e.g.
``this.addRepoMetric('pullRequestAcceptanceRate', 'pull-request-acceptance-rate')``

The first argument is the attribute you will call on a ``Repo``
class instance.

Calling an endpoint
----------------------------

Endpoint calls are handled through Vuex “actions” (``frontend/src/store/modules/common/actions.ts``).
You can call the ``endpoint`` action and pass it an object that holds an array of ``Repo`` or ``RepoGroup`` classes and an array of the endpoint names you want to call on those repos, e.g.:

   ``this.endpoint({repoGroups: relevantApiGroups, endpoints: ['topInsights']}).then((tuples: any) => { .....``
   in the ``frontend/src/views/Dashboard.vue`` file

Or you can hit endpoints directly for a ``Repo`` by calling the endpoint’s attribute on that ``Repo`` class instance, e.g.:

  ``this.base[this.source]().then((data: any) => {....`` in
     the ``frontend/src/components/charts/PieChart.vue`` file

Adding a new page
----------------------------

The chart component should be stored in ``frontend/src/views``.
A new page will need its own route created in\ ``router.ts`` which holds all the routes and defines what components get loaded on each route.
``router-view`` tags act as slots where components can be inserted.

``router.ts`` example:

::

          [ 
             ...
             {
                 path: '/repos',
                 component: Default,
                 children: [
                   {
                     path: '',
                     name: 'repos',
                     components: {
                       sidebar: MainSidebar,
                       navbar: MainNavbar,
                       content: Repos,
                     },
                   },
                 ],
               },
               ...
           ]

-  Other Examples: ``SparkChart.vue``, ``InsightChart.vue``

CSS/Stylus and styling
----------------------------

All of our CSS/Stylus is stored within the ``frontend/src/styles/augur.styl`` file

----------------------------
Architecture
----------------------------

``Augur.ts``

-  imports all frontend packages
-  processes route’s data and updates the store accordingly on every
   route change
-  e.g. the user changes the route from a single to a double comparison,
   then ``Augur.ts`` will update the store’s state based on the route
   change
-  creates Vue application
-  attaches Vue router to Augur’s Vue application

``store`` folder and subfolders
---------------------------------


Responsible for storing our VueX store and its modules

-  store contains options for visualizations and miscellaneous things
   like the current tab or currently selected repo
-  the store’s state’s values can be accessed from any component in the
   application. For example: ``this.$store.state.base``
-  these options can only be changed through what vuex calls
   “mutations”, which are defined in the ``mutations.ts`` file in each
   modules’ folder and can be called from any component in the frontend.
   These mutations are the only way to change the store’s state
-  (OLD VERSION SPECIFIC) example of mutation call from
   MainControls.vue:

.. code:: typescript

         this.$store.commit('setVizOptions', {
           rawWeekly: e.target.checked
         })

-  The preceeding is just a taste of how to use vuex and what it has to
   offer. Anyone interested in contributing to the frontend should read
   up on the vuex docs at https://vuex.vuejs.org/

``AugurAPI.ts``
-----------------

-  anything related to endpoints on the frontend
-  contains methods for creating batch requests (NOT WORKING)
-  this is where new endpoints get added (so the frontend has access)
-  (OLD VERSION SPECIFIC)example from DownloadedReposCard.vue of calling
   an endpoint:

::

       window.AugurAPI.getDownloadedGitRepos().then((data) => {
           // data handler for what endpoint returns data

           this.repos = window._.groupBy(data, 'project_name')
           this.projects = Object.keys(this.repos)
         })

-  All endpoint calls are wrapped inside of vuex “actions” which are
   defined in the ``actions.ts`` file within each vuex modules’
   directory

``Default.vue`` and ``vue-router``
--------------------------------------

``Default.vue``:

-  base template for all pages on the frontend

``router.ts``:

-  add routes by defining paths and the component(s) you want to render
   at that path, see example under
-  be sure to import your component!!:

   -  ``import ComponentName from '../components/ComponentName.vue'``

``Rendering a component within another component's template (html section)``
--------------------------------------------------------------------------------

-  you need to import your inner component in your outer component’s

   .. raw:: html

      <script></script>

   section: ``import Spinner from '../components/Spinner.vue';``
-  (OLD EXAMPLE BUT RELEVANT) Vue translates a name like ‘AugurHeader’
   to something like ‘augur-header’ to be used as a tag. Example from
   MetricsStatusCard.vue:

::

   <template>
     <div class="is-table-container">
       <div class="fullwidth">
         <augur-header></augur-header>
       </div>
       ...
     </div>
   </template

Random “todos”
--------------

   -  Comparing more than one repo (used to work, logic to fix/recover
      this would need to be changed somewhere in DynamicLineChart.vue)
   -  Read the ability to filter by date (either reading the commented
      “more configuration options” part of the CompareControl.vue or
      moving the date options somewhere more convenient, possibly on the
      sidebar)
   -  Alphabetically compare control repositories
   -  See if very high committers by week statistics are caused by the
      frontend
   -  Finish PieChat

   ``The Vue documentation is your friend. You can always message the Slack with questions too.``
