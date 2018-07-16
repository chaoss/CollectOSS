<template>
  <section>
    <h1>Experimental</h1>
    <h2>{{ $store.state.baseRepo }}   {{ $store.state.comparedRepo }}</h2>
      <div class="row">

      <div class="col col-6">
        <area-line-chart source="commitComments"
                    title="Commit Comments / Week "
                    cite-url=""
                    cite-text="Commit Comments">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="totalCommitters"
                    title="Committers"
                    cite-url=""
                    cite-text="Total Commiters">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="pullsAcceptanceRate"
                    title="Pull Acceptance Rate"
                    cite-url=""
                    cite-text="Total Commiters">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="communityEngagement:issues_open"
                    title="Community Engagement: Open Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Open Issues"
                    disable-rolling-average=1>
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="communityEngagement:issues_closed_total"
                    title="Community Engagement: Closed Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Closed Issues"
                    disable-rolling-average=1>
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="fakes"
                    title="Fakes"
                    cite-url=""
                    cite-text="Fakes"
                    disable-rolling-average=1>
        </area-line-chart>
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

import AreaLineChart from './charts/AreaLineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

module.exports = {
  components: {
    AreaLineChart,
    BubbleChart,
    StackedBarChart
  }
}

</script>
