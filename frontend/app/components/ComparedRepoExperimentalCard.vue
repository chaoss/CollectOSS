<template>
  <section>
    <h1>Experimental Comparison</h1>
    <h2>{{ comparedTo }} compared to {{ $store.state.baseRepo }}</h2>
      <div class="row">

      <div class="col col-6">
        <line-chart source="commitComments"
                    title="Commit Comments / Week "
                    cite-url=""
                    v-bind:compared-to="comparedTo"
                    cite-text="Commit Comments">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="totalCommitters"
                    title="Committers"
                    cite-url=""
                    v-bind:compared-to="comparedTo"
                    cite-text="Total Commiters">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="contributionAcceptance"
                    title="Contribution Acceptance Rate"
                    cite-url=""
                    cite-text="Contribution Acceptance"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="communityEngagement:issues_open"
                    title="Community Engagement: Open Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    v-bind:compared-to="comparedTo"
                    cite-text="Open Issues"
                    disable-rolling-average=1>
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="communityEngagement:issues_closed_total"
                    title="Community Engagement: Closed Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    v-bind:compared-to="comparedTo"
                    cite-text="Closed Issues"
                    disable-rolling-average=1>
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="fakes"
                    title="Fakes"
                    cite-url=""
                    v-bind:compared-to="comparedTo"
                    cite-text="Fakes"
                    disable-rolling-average=1>
        </line-chart>
      </div>

      <div class="col col-12">
        <stacked-bar-chart source="issueActivity"
                    title="Issue Activity"
                    cite-url=""
                    v-bind:compared-to="comparedTo"
                    cite-text="Issue Activity">
        </stacked-bar-chart>
      </div>

      <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributor Overview"
                      size="total"
                      cite-url=""
                      v-bind:compared-to="comparedTo"
                      cite-text="Contributors">
        </bubble-chart>
      </div>

    </div>

  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

module.exports = {
  props: ['comparedTo'],
  components: {
    LineChart,
    BubbleChart,
    StackedBarChart
  }
}

</script>
