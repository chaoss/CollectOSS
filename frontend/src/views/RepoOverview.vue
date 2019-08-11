<template>
  <d-container fluid class="main-content-container px-4">
    <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
      <d-breadcrumb-item :active="false" :text="base.rg_name" href="#" />
      <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
    </d-breadcrumb>
    <!-- Page Header -->
    <!-- <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div> -->
    <!-- Compare Control -->
    <compare-control></compare-control>

    <!-- Overview Section -->
    <div class="page-header row no-gutters py-4" >
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title" style="font-size: 1rem">Overview</h3>
      </div>
    </div>

    <!-- <spinner :v-show="!loaded_overview"></spinner> -->
    
    <!-- <div class="row" :v-show="loaded_overview"> -->
    <!-- <div class="row"> -->

        <!-- <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="annualCommitCountRankedByRepoInRepoGroup"
            title="Top Repos in 2018 by Commits with Baseline Averages - Sorted"
            field="commit"
            :data="values['annualCommitCountRankedByRepoInRepoGroup']">
          </grouped-bar-chart>
        </div> -->
     <!--    <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="annualLinesOfCodeCountRankedByRepoInRepoGroup"
            title="Top Repos in 2018 by Net LoC with Baseline Averages - Sorted"
            field="loc"> -->
            <!-- :data="values['annualLinesOfCodeCountRankedByRepoInRepoGroup']"> -->
          <!-- </grouped-bar-chart>
        </div> -->

    <!-- </div> -->

    <!-- Evolution section -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Evolution</h3>
      </div>
    </div>

    <spinner :v-show="!loaded_evolution"></spinner>
    
    <!-- <div class="row" :v-show="loaded_evolution"> -->
    <div class="row" v-if="true">

      <div class="col col-6">
        <dynamic-line-chart source="issuesClosed"
                      title="Number of issuesClosed"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md"
                      cite-text="issuesClosed"
                      :data="values['issuesClosed']">
        </dynamic-line-chart>
      </div>

      <!-- <div class="col col-6">
        <dynamic-line-chart source="closedIssues"
                    title="Closed Issues / Week"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed"> -->
                    <!-- :data="values['closedIssues']"> -->
        <!-- </dynamic-line-chart>
      </div>
 -->
    </div>

    <!-- Issues Section -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Issues</h3>
      </div>
    </div>

    <!-- <spinner :v-show="!loaded_issues"></spinner> -->
    
    <!-- <div class="row" :v-show="loaded_issues"> -->
    <div class="row" v-if="false">

      <div class="col col-12" style="padding-right: 35px">
        <dual-line-chart source=""
          :title="'Issue Count History for ' + base.name + ' - Grouped by Week'"
          fieldone="open_count"
          fieldtwo="closed_count">
          <!-- :data="values['repo_issues']"> -->
        </dual-line-chart>
      </div>

      <div class="col col-12" style="padding-right: 35px">
        <dual-line-chart source=""
          :title="'Issue Count History for this Repo Group:  ' + group + ' - Grouped by Week'"
          fieldone="open_count"
          fieldtwo="closed_count">
        </dual-line-chart>
        <!-- :data="values['group_issues']"></dual-line-chart> -->
      </div>

    </div>

    <!-- Experimental section -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Experimental</h3>
      </div>
    </div>

    <!-- <spinner :v-show="!loaded_experimental"></spinner> -->
    
    <!-- <div class="row" :v-show="loaded_experimental"> -->
    <div class="row" v-if="false">

      <div class="col col-6">
        <dynamic-line-chart source="commitComments"
                    title="Commit Comments / Week "
                    cite-url=""
                    cite-text="Commit Comments">
                    <!-- :data="values['commitComments']"> -->
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="totalCommitters"
                    title="Committers"
                    cite-url=""
                    cite-text="Total Commiters"
                    disable-rolling-average=1>
                    <!-- :data="values['totalCommitters']"> -->
        </dynamic-line-chart>
      </div>

    </div>

    <!-- Activity section -->
    <!-- <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Activity</h3>
      </div>
    </div> -->

    <!-- <spinner :v-show="!loaded_activity"></spinner> -->
    
    <!-- <div class="row" :v-show="loaded_activity"> -->
    <!-- <div class="row">

      <div class="col col-6">
        <dynamic-line-chart source="issueComments" 
                    title="Issue Comments / Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/issue-comments.md"
                    cite-text="Issue Comments"> 
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="pullRequestsMadeClosed" 
                    title="Pull Requests Made/ Closed per Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requests Made/Closed"> 
        </dynamic-line-chart>
      </div>

      <div class="col col-12">
        <dynamic-line-chart source="watchers" 
                    title="Watchers / Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/watchers.md"
                    cite-text="Watchers"> 
        </dynamic-line-chart>
      </div>
       
    </div> -->
    



    
  </d-container>
</template>

<script lang="ts">
import  { Component, Vue } from 'vue-property-decorator';
import {mapActions, mapGetters} from "vuex";
import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';
import TickChart from '../components/charts/TickChart.vue'
import LinesOfCodeChart from '../components/charts/LinesOfCodeChart.vue'
import NormalizedStackedBarChart from '../components/charts/NormalizedStackedBarChart.vue'
import OneDimensionalStackedBarChart from '../components/charts/OneDimensionalStackedBarChart.vue'
import HorizontalBarChart from '../components/charts/HorizontalBarChart.vue'
import GroupedBarChart from '../components/charts/GroupedBarChart.vue'
import StackedBarChart from '../components/charts/StackedBarChart.vue'
import DynamicLineChart from '../components/charts/DynamicLineChart.vue'
import DualLineChart from '../components/charts/DualLineChart.vue'
import Spinner from '../components/Spinner.vue'
import CompareControl from '../components/common/CompareControl.vue'

@Component({
  components: {
    SparkChart,
    InsightChart,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    DynamicLineChart,
    StackedBarChart,
    DualLineChart,
    Spinner,
    CompareControl,
  },
  methods: {
    ...mapActions('common',[
      'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                  // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
    ])
  },
  computed: {
    ...mapGetters('common',[
    ]),
    ...mapGetters('compare',[
      'base'
    ]),
  },
})

export default class RepoOverview extends Vue {
  colors = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
  testEndpoints = ['closedIssues', 'openIssues', 'codeCommits']
  testTimeframes = ['past 1 month', 'past 3 months', 'past 2 weeks']
  repos = {}
  projects = []
  themes = ['dark', 'info', 'royal-blue', 'warning']
  project = null
  loaded_overview = false
  loaded_evolution = false
  loaded_issues = false
  loaded_experimental = false
  loaded_activity = false
  values = {'issuesClosed':{}}

  // deflare vuex action, getter, mutations
  groupsInfo!: any;
  getRepoGroups!: any;
  repo_groups!: any[];
  sorted_repo_groups!: any[];
  base!: any;
  // actions
  endpoint!: any;

  created() {
    this.endpoint({endpoints:this.testEndpoints,repos:[this.base]}).then((tuples:any) => {

    })
  }
}
</script>

