<template>
  <d-container fluid class="main-content-container px-4">
    <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
      <d-breadcrumb-item :active="true" :text="base.rg_name" href="#" />
    </d-breadcrumb>
    <!-- Page Header -->
    <!-- <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div> -->
    <!-- Compare Control -->
    <compare-control></compare-control>

    <div class="row">
      <d-button><d-link :to="{name: 'risk', params: {repo: base.repo_name, group:base.rg_name}}"><span>Risk</span></d-link></d-button>
    </div>

    <!-- Overview Section -->
    <!-- <div class="page-header row no-gutters py-4" >
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0"> -->
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <!-- <h3 class="page-title" style="font-size: 1rem">Overview</h3>
      </div>
    </div> -->

    <div class="row">
      
      <div class="row col col-7" style="" >
        <spinner v-if="!loadedBars" style="padding-top: 2rem"></spinner>
<!-- look to add commit chart? -->
        <!--<div class="col col-12">
          <commit-chart source="changesByAuthor" :data="values['changesByAuthor']"></commit-chart>
        </div> -->
        <div class="row col col-12" v-if="loadedBars">
          <div class="col col-6" style="padding-right: 35px; transform: translateY(-0px) !important">
            <normalized-stacked-bar-chart 
            title="Lines of code added by the top 10 authors as Percentages - By Time Period"
            source="changesByAuthor1" :data="values['changesByAuthor']">
            </normalized-stacked-bar-chart>
          </div>
          <div class="col col-6" style="padding-left: 0px; transform: translateY(-0px) !important">
            <div style="padding-top: 0px"></div>
            <horizontal-bar-chart measure="lines" title="Average Lines of Code Per Commit"
            source="changesByAuthor2" :data="values['changesByAuthor']"></horizontal-bar-chart>
          </div>

          <div class="col col-6">
            <one-dimensional-stacked-bar-chart type="lines" title="Lines of Code Added by the top 10 Authors as Percentages - All Time" :data="values['changesByAuthor']"></one-dimensional-stacked-bar-chart>
          </div>
          <div class="col col-6">
            <one-dimensional-stacked-bar-chart type="commit" title="Commits by the top 10 Authors as Percentages - All Time"
            :data="values['changesByAuthor']"></one-dimensional-stacked-bar-chart>
          </div>
        </div>
      </div>
      <div class="row col col-5">
        <spinner v-if="!loadedBars" style="padding-top: 2rem"></spinner>
        <lines-of-code-chart v-if="loadedBars" :data="values['changesByAuthor']" style="font-size: 0.6rem"></lines-of-code-chart>
      </div>

    </div>

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
import router from "@/router";
import BubbleChart from '../components/charts/BubbleChart.vue'

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
    BubbleChart,
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
  barEndpoints = ['changesByAuthor']
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
  values: any = {'issuesClosed':[], 'changesByAuthor': []}
  loadedBars = false

  // deflare vuex action, getter, mutations
  groupsInfo!: any;
  getRepoGroups!: any;
  repo_groups!: any[];
  sorted_repo_groups!: any[];
  base!: any;
  // actions
  endpoint!: any;

  created() {
    console.log(this.base)
    console.log(process.env.VUE_APP_PORT)
    this.endpoint({endpoints:this.barEndpoints,repos:[this.base]}).then((tuples:any) => {
      console.log(tuples)
      Object.keys(tuples[this.base.rg_name][this.base.url]).forEach((endpoint) => {
        this.values[endpoint] = tuples[this.base.rg_name][this.base.url][endpoint]
      })
      console.log(this.values)
      this.loadedBars = true
    })
  }

}
</script>

