<template>
  <section>
    <h1>Growth, Maturity, and Decline</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">



      <div class="col col-6">
        <line-chart source="commits"
                    title="Commits / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="forks"
                    title="Forks / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="communityEngagement:issues_open"
                    title="Open Issues" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty"
                    disable-rolling-average=1>
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="communityEngagement:issues_open+issues_closed_total"
                    title="Closed Issues" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty"
                    disable-rolling-average=1>
        </line-chart>
      </div>

            <div class="col col-6">
        <line-chart source="communityEngagement:issues_opened"
                    title="Issues Open / Week"
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>


      <div class="col col-6">
        <line-chart source="pullReqComments" 
                    title="Pull Request Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullsAcceptanceRate" 
                    title="Pull Acceptance Rate" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issuesClosed" 
                    title="Issues Closed / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="totalCommitters" 
                    title="Total Committers" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="linesChanged" 
                    title="Lines Changed" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </line-chart>
      </div>
    </div>
    
    <small>Data provided by <a href="http://ghtorrent.org/msr14.html">GHTorrent</a> <span class="ghtorrent-version"></span> and the <a href="https://developer.github.com/">GitHub API</a></small>
  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

module.exports = {
  components: {
    LineChart,
    BubbleChart,
    StackedBarChart
  }
};

</script>
