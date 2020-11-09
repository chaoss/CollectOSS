<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <div class="growthMaturity">
      <h2 v-if="this.loaded" class="growthMaturityHeader">{{$store.state.baseRepo}}</h2>
      <p></p>
      <h2 class="growthMaturity repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="growthMaturity" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>

    

    <div class="row gitCardDiv7" v-if="loaded1">
        <issue-chart source="issuesOverview" 
                    title = "issue Overview"
                    :data="values['getIssues']">
        </issue-chart>
    </div>
    <div v-if="loaded2" class="row">
      <div class="col col-6">
        <dynamic-line-chart source="issuesOpenAge"
                      title="Issues Open Age"
                      cite-url="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md"
                      cite-text="Issues Open Age"
                      :data="values['issuesOpenAge']">
        </dynamic-line-chart>
      </div>
      <div class="col col-6">
        <dynamic-line-chart source="issueActive"
                      title="Active Issues"
                      cite-url="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md"
                      cite-text="Acitve Issue"
                      :data="values['issueActive']">
        </dynamic-line-chart>
      </div>
    </div>

    <div v-if="loaded3" class="row">
        <div class="col col-12 issuesCard" >
        <dual-line-chart source=""
        :title="'Issue Count History for this Repo :  ' + this.repo + ' - Grouped by Week'"
        fieldone="open_count"
        fieldtwo="closed_count"
        :data="values['repo_issues']"></dual-line-chart>
      </div>
    </div>

    <spinner v-if="!this.loaded"></spinner>

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
import IssueChart from './charts/IssueChart'
import DynamicLineChart from './charts/DynamicLineChart'
import DualLineChart from './charts/DualLineChart'

export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      values: {'repo_issues':[]},
      loaded1: false,
      loaded2: false,
      loaded3: false,
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
    IssueChart,
    DynamicLineChart,
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
    loaded() {
      return this.loaded1 && this.loaded2 && this.loaded3
    }
  },
  mounted() {
    // repo.issueActive().then((data) => {
    //   this.values['issueActive'] = data
    //   console.log("repo DATA: ", this.values['issueActive'])
    // })
    let repos = []
    if (this.repo) {
      if (window.AugurRepos[this.repo])
        repos.push(window.AugurRepos[this.repo])
      // repos.push(this.repo)
    } // end if (this.$store.repo)
    this.comparedRepos.forEach(function(repo) {
      repos.push(window.AugurRepos[repo])
    }); 

    let endpoints1 = [
      "getIssues"
    ]
    
    window.AugurAPI.batchMapped(repos, endpoints1).then((data) => {
      console.log("here",data)
      endpoints1.forEach((endpoint) => {
        this.values[endpoint] = {}
        this.values[endpoint][this.repo] = {}
        this.values[endpoint][this.repo][endpoint] = data[this.repo][endpoint]
      })
      // this.values=data
      this.loaded1=true
      // return data
    }, (error) => {
      this.loaded1=false
      console.log("failed", error)
    }) // end batch

    let endpoints2 = [
      "issuesOpenAge",
      "issueActive"
    ]
    window.AugurAPI.batchMapped(repos, endpoints2).then((data) => {
      console.log("here",data)
      endpoints2.forEach((endpoint) => {
        this.values[endpoint] = {}
        this.values[endpoint][this.repo] = {}
        this.values[endpoint][this.repo][endpoint] = data[this.repo][endpoint]
      })
      // this.values=data
      this.loaded2=true
      // return data
    }, (error) => {
      this.loaded2=false
      console.log("failed", error)
    }) // end batch
  
    let endpoints3 = [
      "openIssuesCount",
      "closedIssuesCount"
    ]
     window.AugurAPI.batchMapped(repos, endpoints3).then((data) => {
      console.log("here",data)
      endpoints3.forEach((endpoint) => {
       this.values['repo_issues'] =  this.values['repo_issues'].concat(data[this.repo][endpoint])
      })
      // this.values=data
      this.loaded3=true
      // return data
    }, (error) => {
      this.loaded3=false
      console.log("failed", error)
    }) // end batch
  
  }
}
</script>