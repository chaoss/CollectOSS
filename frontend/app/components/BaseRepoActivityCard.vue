<template>
  <section>
    <h1>Activity</h1>
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
        <line-chart source="issues"
                    title="Issues / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issueComments" 
                    title="Issue Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="commitComments" 
                    title="Commit Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"> 
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
        <line-chart source="pulls" 
                    title="Pulls Requests / Week" 
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

      <div class="col col-12">
        <bubble-chart source="contributions"
                      title="Contributior Overview"
                      size="total"
                      color-red="issues"
                      color-green="commit_comments"
                      color-blue="issue_comments"
                      color-lightness="commits"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                      cite-text="Community Activty">
        </bubble-chart>
      </div>
 
      <div class="col col-12">
        <StackedBarChart source="issueActivity" 
                    title="Stacked Bar Chart" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </StackedBarChart>
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
