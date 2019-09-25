<template>
  <d-container fluid class="main-content-container px-4">
    <div class="row">
      <div class="col col-5">
        <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
          <d-breadcrumb-item :active="false" :text="base.rg_name" href="#" @click="onRepoGroup({rg_name: base.rg_name, repo_group_id: base.repo_group_id})"/>
          <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
        </d-breadcrumb>
      </div>
      <div class="col col-3" v-for="repo in compRepoNames">
        <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
          <d-breadcrumb-item :active="false" :text="repo.split('/')[0]" href="#"/>
          <d-breadcrumb-item :active="true" :text="repo.split('/')[1]" href="#" />
        </d-breadcrumb>
      </div>
      <!-- <div class="col col-6"></div> -->
    </div>

    <d-button-group>
      <d-button outline pill theme="secondary" @click="onTab" value="repo_overview">Overview</d-button>
      <d-button outline pill theme="secondary" @click="onTab" value="repo_risk">Risk Metrics</d-button>
      <d-button outline pill active>Comparison Overview</d-button>
      <!-- <d-button outline pill theme="secondary" @click="onTab" value="repo_risk">Risk</d-button> -->
    </d-button-group>
    <p></p>

    <!-- Page Header -->
    <!-- <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div> -->
    <!-- Compare Control -->
    <compare-control></compare-control>

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
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="codeChanges"
                      title="Code Changes (Commits) / Week"
                      cite-url=""
                      cite-text="Code Changes"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <dynamic-line-chart v-if="loaded"
                      source="codeChangesLines"
                      title="Lines of Code Changed / Week"
                      cite-url=""
                      cite-text="Code Changes Lines"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="openIssuesCount"
                      title="Open Issues / Week"
                      cite-url=""
                      cite-text="Open Issues"
                      :repos="repos">
                      <!-- :data="values['openIssuesCount']"> -->
          </dynamic-line-chart>
        </d-card>
      </div>


      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="closedIssuesCount"
                      title="Closed Issues / Week"
                      cite-url=""
                      cite-text="Closed Issues"
                      :repos="repos">
                      <!-- :data="values['closedIssuesCount']"> -->
          </dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="issuesNew"
                      title="New Issues / Week"
                      cite-url=""
                      cite-text="New Issues"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div> 

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="reviews"
                      title="Reviews (Pull Requests) / Week"
                      cite-url=""
                      cite-text="Reviews"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div> 

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="reviewsAccepted"
                      title="Reviews (Pull Requests) Accepted / Week"
                      cite-url=""
                      cite-text="Reviews Accepted"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div> 

      <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="reviewsDeclined"
                      title="Reviews (Pull Requests) Declined / Week"
                      cite-url=""
                      cite-text="Reviews Declined"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div> 

      <!-- need to update metric to make it averages -->
      <!-- <div class="col col-6" style="padding-top:3rem">
        <d-card>
          <spinner v-if="!loaded"></spinner>

          <dynamic-line-chart v-if="loaded"
                      source="reviewDuration"
                      title="Reviews (Pull Requests) Average Duration / Week"
                      cite-url=""
                      cite-text="Reviews Duration"
                      :repos="repos">
          </dynamic-line-chart>
        </d-card>
      </div>  -->

      

      <!-- <div class="col col-12">
        <d-card>
          <stacked-bar-chart source="issueActivity"
                      title="Issue Activity"
                      cite-url=""
                      cite-text="Issue Activity">
          </stacked-bar-chart>
        </d-card>
      </div>

      <div class="col col-12">
        <d-card>
          <bubble-chart source="contributors"
                        title="Contributor Overview"
                        size="total"
                        cite-url=""
                        cite-text="Contributors">
          </bubble-chart>
        </d-card>
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
      'comparedAPIRepos',
      'comparedRepos'
    ]),
  },
})

export default class SingleComparison extends Vue {
  colors = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
  endpoints = ['openIssuesCount', 'closedIssuesCount', 'pullRequestAcceptanceRate']
  testTimeframes = ['past 1 month', 'past 3 months', 'past 2 weeks']
  repos:any = []
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
  sortedRepoGroups!: any[];
  base!: any;
  comparedRepos!: any;
  comparedAPIRepos!: any;
  apiRepos!: any;

  // actions
  endpoint!: any;
  setBaseGroup!: any;

  get compRepoNames () {
    return 'names' in this.comparedRepos ? this.comparedRepos.names : this.comparedRepos
  }

  created() {
    console.log("here",this.comparedRepos, this.base)
    let promises = []
    promises.push(this.repos.push(this.base))
    promises.push(this.comparedAPIRepos.forEach((repo: any) => {
      this.repos.push(repo)
    }))
    Promise.all(promises).then(() => {
      console.log("singly comparison", "true", this.repos)
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

  onTab(e: any) {
    console.log("onTab", e.target.value)
    this.$router.push({
      name: e.target.value, params: {repo: this.base.repo_name, group: this.base.rg_name}
    })
  }

}
</script>

