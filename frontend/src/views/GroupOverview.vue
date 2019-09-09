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



    <spinner style="padding-top: 2rem" v-if="!loadedRepos"></spinner>

    <div style="padding-top: 2rem" v-if="loadedRepos"  class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Repos</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table style="table-layout:fixed;" class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th width="20%" scope="col" class="border-0" v-on:click="sortTable('url')"> 
                    <div class="row">
                      <div class="col col-9">URL</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')"> 
                    <div class="row">
                      <div class="col col-9">Repo Group Name</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'rg_name' == sortColumn"></div>
                    </div>
                  </th>
                  <th width="30%" scope="col" class="border-0" v-on:click="sortTable('description')">
                    <div class="row">
                      <div class="col col-9">Repo Description</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'description' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('repo_count')">
                    <div class="row">
                      <div class="col col-9">Group's Repo Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_count' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('commits_all_time')">
                    <div class="row">
                      <div class="col col-9">Total Commit Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'commits_all_time' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('issues_all_time')">
                    <div class="row">
                      <div class="col col-0">Total Issue Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'issues_all_time' == sortColumn"></div>
                    </div>
                  </th>
                  <!-- <th scope="col" class="border-0" v-on:click="sortTable('repo_status')">
                    <div class="row">
                      <div class="col col-9">Status</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_status' == sortColumn"></div>
                    </div>
                  </th> -->
                  <th scope="col" class="border-0">Options</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(repo,index) in sortedReposInGroup(base,sortColumn,ascending)" v-bind:item="repo">
                  <td>
                    <a href="#" @click="onGitRepo(repo)">{{ repo.url }}</a>
                  </td>
                  <td>{{ repo.rg_name }}</td>
                  <td>{{ repo.description }}</td>
                  <td>{{ repo.repo_count }}</td>
                  <td>{{ repo.commits_all_time }}</td>
                  <td>{{ repo.issues_all_time }}</td>
                  <!-- <td>{{ repo.repo_status }}</td> -->
                  <td>
                    <div class="row">
                      <button :id="'favorite'+index" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0;border: none; background: none;">
                        <i class="material-icons" style="color:#007bff;">star_rate</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#favorite'+index"
                                 container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <button :id="'add_compare'+index" class="nav-link col col-2" style="padding: 0;border: none; background: none;" @click="addComparedRepo(repo)">
                        <i class="material-icons" style="color:#007bff;">library_add</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#add_compare'+index"
                                 :triggers="['hover']"
                                 container=".shards-demo--example--tooltip-01">
                        Add this repo group to your current compared repos
                      </d-tooltip>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    <!-- <div class="row">
      
      <div class="row col col-7" style="" >
        <spinner v-if="!loadedBars" style="padding-top: 2rem"></spinner>
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
      'loadRepos',
    ])
  },
  computed: {
    ...mapGetters('common',[
      'sortedReposInGroup'
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
  values: any = {'repos':[], 'changesByAuthor': []}
  loadedBars = false
  loadedRepos = false
  ascending:boolean = false;
  sortColumn: string ='commits_all_time';

  // deflare vuex action, getter, mutations
  groupsInfo!: any;
  getRepoGroups!: any;
  repo_groups!: any[];
  sortedReposInGroup!: any[];
  base!: any;
  // actions
  endpoint!: any;
  loadRepos!: any;

  created() {
    // this.endpoint({endpoints:this.barEndpoints,repoGroups:[this.base]}).then((tuples:any) => {
    //   console.log(tuples)
    //   Object.keys(tuples[this.base.rg_name]['groupEndpoints']).forEach((endpoint) => {
    //     this.values[endpoint] = tuples[this.base.rg_name]['groupEndpoints'][endpoint]
    //   })
    //   console.log(this.values)
    //   this.loadedBars = true
    //   console.log("done")
    // })
    this.loadRepos().then((repos:any) => {
      this.loadedRepos = true
    })

  }

  sortTable(col: string) {
      if (this.sortColumn === col) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = col;
      }
  }

  onGitRepo (e: any) {
    this.$router.push({
      name: 'repo_overview',
      params: {group:e.rg_name, repo:e.repo_name, repo_group_id: e.repo_group_id, repo_id: e.repo_id, url:e.url}
    })
  }

}
</script>

