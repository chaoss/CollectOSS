<template>
  <section>
    <h1>Experimental</h1>
    <div style="display: inline-block;">
      <h2 style="display: inline-block; color: black !important">{{ $store.state.baseRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
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
                    cite-text="Commit Comments">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="totalCommitters"
                    title="Committers"
                    cite-url=""
                    cite-text="Total Commiters"
                    disable-rolling-average=1>
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="contributionAcceptance"
                    title="Contribution Acceptance Rate"
                    cite-url=""
                    cite-text="Contribution Acceptance">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="communityEngagement:issues_open"
                    title="Community Engagement: Open Issues"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Open Issues"
                    disable-rolling-average=1>
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="communityEngagement:issues_closed_total"
                    title="Community Engagement: Closed Issues"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Closed Issues"
                    disable-rolling-average=1>
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="fakes"
                    title="Fakes"
                    cite-url=""
                    cite-text="Fakes"
                    disable-rolling-average=1>
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="newWatchers"
                    title="New Watchers / Week"
                    cite-url=""
                    cite-text="New Watchers">
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

module.exports = {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart,
    DualAxisContributions
  }
}

</script>
