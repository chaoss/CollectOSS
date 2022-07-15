<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <h1>Experimental</h1>
    <div class="baseRepo">
      <h2 class="baseRepoh2">{{ $store.state.baseRepo }}</h2>
      <h2 class="repolisting baseRepo" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="baseRepo" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>

      <div class="row">

      <!-- <div class="col col-12">
        <dual-axis-contributions></dual-axis-contributions>
      </div> -->

      <div class="col col-6">
        <dynamic-line-chart source="commitComments"
                    title="Commit Comments / Week "
                    cite-url=""
                    cite-text="Commit Comments"
                    :data="values['commitComments']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="totalCommitters"
                    title="Committers"
                    cite-url=""
                    cite-text="Total Commiters"
                    disable-rolling-average=1
                    :data="values['totalCommitters']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="contributionAcceptance"
                    title="Contribution Acceptance Rate"
                    cite-url=""
                    cite-text="Contribution Acceptance"
                    :data="values['contributionAcceptance']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="communityEngagement:issues_open"
                    title="Community Engagement: Open Issues"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Open Issues"
                    disable-rolling-average=1
                    :data="values['communityEngagement:issues_open']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="communityEngagement:issues_closed_total"
                    title="Community Engagement: Closed Issues"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Closed Issues"
                    disable-rolling-average=1
                    :data="values['communityEngagement:issues_closed_total']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="fakes"
                    title="Fakes"
                    cite-url=""
                    cite-text="Fakes"
                    disable-rolling-average=1
                    :data="values['fakes']">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="newWatchers"
                    title="New Watchers / Week"
                    cite-url=""
                    cite-text="New Watchers"
                    :data="values['newWatchers']">
        </dynamic-line-chart>
      </div>

      <div class="col col-12">
        <stacked-bar-chart source="issueActivity"
                    title="Issue Activity"
                    cite-url=""
                    cite-text="Issue Activity">
        </stacked-bar-chart>
      </div>

      <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributor Overview"
                      size="total"
                      cite-url=""
                      cite-text="Contributors">
        </bubble-chart>
      </div>

    </div>

  </section>
</template>

<script>

import DynamicLineChart from './charts/DynamicLineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'
import DualAxisContributions from './charts/DualAxisContributions'

export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      loaded: false,
      values: {}
    }
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepos () {
      return this.$store.state.gitRepo
    },
    comparedRepos () {
      return this.$store.state.comparedRepos
    },
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart,
    DualAxisContributions
  },
  created() {
    let repos = []
    if (this.repo) {
      if (window.AugurRepos[this.repo])
        repos.push(window.AugurRepos[this.repo])
      else if (this.domain){
        let temp = window.AugurAPI.Repo({"gitURL": this.gitRepo})
        if (window.AugurRepos[temp])
          temp = window.AugurRepos[temp]
        else
          window.AugurRepos[temp] = temp
        repos.push(temp)
      }
      // repos.push(this.repo)
    } // end if (this.$store.repo)
    this.comparedRepos.forEach(function(repo) {
      repos.push(window.AugurRepos[repo])
    });
    let endpoints1 = [
"commitComments",
"totalCommitters",
"contributionAcceptance",
"communityEngagement:issues_open",
"communityEngagement:issues_closed_total",
"fakes",
"newWatchers",
"issueActivity",
"contributors"
    ]
    window.AugurAPI.batchMapped(repos, endpoints1).then((data) => {
      endpoints1.forEach((endpoint) => {
        this.values[endpoint] = {}
        this.values[endpoint][this.repo] = {}
        this.values[endpoint][this.repo][endpoint] = data[this.repo][endpoint]
      })
      // this.values=data
      this.loaded=true
      // return data
    }, (error) => {
      //this.renderError()
      console.log("failed", error)
    }) // end batch request
  }
}

</script>
