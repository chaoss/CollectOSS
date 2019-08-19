<template>
  <d-container fluid class="main-content-container px-4">
    <div class="row">
      <div class="col col-3">
        <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
          <d-breadcrumb-item :active="false" :text="base.rg_name" href="#" @click="onRepoGroup({rg_name: base.rg_name, repo_group_id: base.repo_group_id})"/>
          <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
        </d-breadcrumb>
      </div>
      <div class="col col-3" v-for="repo in comparedRepos">
        <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
          <d-breadcrumb-item :active="false" :text="repo.split('/')[0]" href="#"/>
          <d-breadcrumb-item :active="true" :text="repo.split('/')[1]" href="#" />
        </d-breadcrumb>
      </div>
      <!-- <div class="col col-6"></div> -->
    </div>

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

      <!-- <div class="col col-12">
        <dual-axis-contributions></dual-axis-contributions>
      </div> -->
      <div class="col col-6" style="padding-top:3rem">
        <spinner v-if="!loaded"></spinner>

        <dynamic-line-chart v-if="loaded"
                    source="openIssuesCount"
                    title="Open Issues / Week"
                    cite-url=""
                    cite-text="Open Issues"
                    :data="values['openIssuesCount']">
        </dynamic-line-chart>
      </div>


      <div class="col col-6" style="padding-top:3rem">
        <spinner v-if="!loaded"></spinner>

        <dynamic-line-chart v-if="loaded"
                    source="closedIssuesCount"
                    title="Closed Issues / Week"
                    cite-url=""
                    cite-text="Closed Issues"
                    :data="values['closedIssuesCount']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6" style="padding-top:3rem">
        <dynamic-line-chart v-if="loaded"
                    source="pullRequestAcceptanceRate"
                    title="Pull Request Acceptance Rate"
                    cite-url=""
                    cite-text="Pull Request Acceptance Rate"
                    :data="values['pullRequestAcceptanceRate']">
        </dynamic-line-chart>
      </div>
<!-- 
      <div class="col col-12">
        <stacked-bar-chart source="issueActivity"
                    title="Issue Activity"
                    cite-url=""
                    cite-text="Issue Activity">
        </stacked-bar-chart>
      </div> -->

     <!--  <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributor Overview"
                      size="total"
                      cite-url=""
                      cite-text="Contributors">
        </bubble-chart>
      </div> -->

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
    ]),
    ...mapActions('compare',[
      'addComparedRepo',
      'setBaseGroup'
    ])
  },
  computed: {
    ...mapGetters('common',[
      'apiRepos'
    ]),
    ...mapGetters('compare',[
      'base',
      'comparedRepos'
    ]),
  },
})

export default class SingleComparison extends Vue {
  colors = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
  endpoints = ['openIssuesCount', 'closedIssuesCount', 'pullRequestAcceptanceRate']
  testTimeframes = ['past 1 month', 'past 3 months', 'past 2 weeks']
  repos = {}
  projects = []
  themes = ['dark', 'info', 'royal-blue', 'warning']
  project = null
  loaded: boolean = false
  values: any = {'issuesClosed':{}, 'changesByAuthor': {}, 'pullRequestAcceptanceRate': {}}
  loadedBars = false

  // deflare vuex action, getter, mutations
  groupsInfo!: any;
  getRepoGroups!: any;
  repo_groups!: any[];
  sorted_repo_groups!: any[];
  base!: any;
  // actions
  endpoint!: any;
  setBaseGroup!: any;
  comparedRepos!: any;
  apiRepos!: any;

  created() {
    let apiRepos: any[] = [this.base]
    this.comparedRepos.forEach((repo: any) => {
      apiRepos.push(this.apiRepos[repo])
    })
    this.endpoint({endpoints:this.endpoints,repos: apiRepos}).then((tuples:any) => {
      console.log(tuples)
      Object.keys(tuples[this.base.rg_name][this.base.url]).forEach((endpoint) => {
        this.values[endpoint] = {}
        apiRepos.forEach((repo) => {
          this.values[endpoint][repo.repo_name] = {}
          this.values[endpoint][repo.repo_name][endpoint] = tuples[this.base.rg_name][this.base.url][endpoint]
        })
      })
      this.loaded = true
    })
  }

  onRepoGroup(repo_group: any) {
    this.setBaseGroup(repo_group).then((repo: any) => {
      this.$router.push({
        name: 'group_overview',
        params: {group: repo_group.rg_name}
      })
    })
  }

}
</script>

