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
      <div class="row" style="transform: translateY(-50px) !important" v-if="loaded">

        <div class="col col-12" style="padding-right: 35px">
          <dual-line-chart source=""
          title="Issue Counts for All Repositories - Grouped by Week"
          fieldone="open_count"
          fieldtwo="closed_count"
          :data="values['issues']"></dual-line-chart>
        </div>
    </div>
  </section>
</template>

<script>
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
      values: {'issues': []},
      loaded: false,
      project: null
    }
  },
  components: {
    AugurHeader,
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
created() {
//     let repos = []
//     console.log("HI")
//     if (this.repo) {
//       if (window.AugurRepos[this.repo])
//         repos.push(window.AugurRepos[this.repo])
//       // repos.push(this.repo)
//     } // end if (this.$store.repo)
//     this.comparedRepos.forEach(function(repo) {
//       repos.push(window.AugurRepos[repo])
//     });
//     let endpoints1 = [
// 'rgOpenIssuesCount',

// // "facadeProject"
//     ]
//     endpoints1.forEach((source) => {
//       let repo = window.AugurAPI.Repo({ repo_group_id: 25153 })
//       repo[source]().then((data) => {
//         console.log("batch data", data)
//         this.values[source] = data
//         this.loaded=true
//         // this.project = this.values["facadeProject"][0].name
//         // console.log(this.project, "here", this.values["facadeProject"])     
//       }, () => {
//             //this.renderError()
//       }) // end batch request
//     })
    window.AugurAPI.getOpenIssues().then((data) => {
      console.log("DATA: ", data)
      this.values['issues'] = this.values['issues'].concat(data)
      console.log("DATA: ", this.values['issues'])
    })
    window.AugurAPI.getClosedIssues().then((data) => {
      console.log("DATA: ", data)
      this.values['issues'] = this.values['issues'].concat(data)
      console.log("DATA: ", this.values['issues'])
      this.loaded = true
    })
  }
}
</script>