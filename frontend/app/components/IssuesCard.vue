<template>
  <section>
    <div style="display: inline-block;">
      <h2 v-if="loaded" style="display: inline-block; color: black !important">Overview of Issue Counts for Repo Group: All repositories</h2>
      <p></p>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>

    <spinner v-if="!loaded"></spinner>
    

    <div class="row" style="transform: translateY(-50px) !important" v-if="loaded">
      
      <div class="col col-12" style="padding-right: 35px">
        <dual-line-chart source=""
        :title="'Issue Count History for ' + repo + ' - Grouped by Week'"
        fieldone="open_count"
        fieldtwo="closed_count"
        :data="values['repo_issues']"></dual-line-chart>
      </div>

      <div class="col col-12" style="padding-right: 35px">
        <dual-line-chart source=""
        :title="'Issue Count History for this Repo Group:  ' + group + ' - Grouped by Week'"
        fieldone="open_count"
        fieldtwo="closed_count"
        :data="values['group_issues']"></dual-line-chart>
      </div>

    </div>
  </section>
</template>

<script>
import Spinner from './Spinner'
import AugurHeader from './AugurHeader'
import TickChart from './charts/TickChart'
import LinesOfCodeChart from './charts/LinesOfCodeChart'
import NormalizedStackedBarChart from './charts/NormalizedStackedBarChart'
import OneDimensionalStackedBarChart from './charts/OneDimensionalStackedBarChart'
import HorizontalBarChart from './charts/HorizontalBarChart'
import GroupedBarChart from './charts/GroupedBarChart'
import StackedBarChart from './charts/StackedBarChart'
import DualLineChart from './charts/DualLineChart'
module.exports = {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      values: {'group_issues': [], 'repo_issues': []},
      loaded: false,
      project: null,
      group: null
    }
  },
  components: {
    AugurHeader,
    Spinner,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    StackedBarChart,
    DualLineChart
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepo () {
      return this.$store.state.gitRepo
    },
    comparedRepos () {
      return this.$store.state.comparedRepos
    },
    // loaded() {
    //   return this.loaded1 && this.loaded2
    // }
  },
  mounted() {
    let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
    let group = window.AugurAPI.Repo({ repo_group_id: repo.repo_group_id })

    group.openIssuesCount().then((data) => {
      this.group = data[0]['rg_name']
      this.values['group_issues'] = this.values['group_issues'].concat(data)
      console.log("group DATA: ", this.values['group_issues'])
    })
    group.closedIssuesCount().then((data) => {
      this.values['group_issues'] = this.values['group_issues'].concat(data)
      console.log("group DATA: ", this.values['group_issues'])
    })

    repo.openIssuesCount().then((data) => {
      this.values['repo_issues'] = this.values['repo_issues'].concat(data)
      console.log("repo DATA: ", this.values['repo_issues'])
    })
    repo.closedIssuesCount().then((data) => {
      this.values['repo_issues'] = this.values['repo_issues'].concat(data)
      console.log("repo DATA: ", this.values['repo_issues'])
    })

    this.loaded = true
  }
}
</script>