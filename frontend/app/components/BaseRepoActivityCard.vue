<template>
  <section>
    <h1>Activity</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">

      <div class="col col-6">
        <line-chart source="commits"
                    title="Commits / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-commits.md"
                    cite-text="Commits">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="forks"
                    title="Forks / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md"
                    cite-text="Forks">
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
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/people-opening-issues.md"
                    cite-text="Issue Comments"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="commitComments"
                    title="Commit Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-reviews.md"
                    cite-text="Code Reviews (naive implementation)"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullReqComments" 
                    title="Pull Request Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullsAcceptanceRate" 
                    title="Pull Request Acceptance Rate" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requets Made / Closed"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issuesClosed" 
                    title="Issues Closed / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-resolution-efficiency.md"
                    cite-text="Issue Resolution Efficiency"> 
        </line-chart>
      </div>

      <div class="col col-12">
        <line-chart source="totalCommitters" 
                    title="Total Committers" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contributors.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </line-chart>
      </div>

      <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributior Overview"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contributors.md"
                      cite-text="Contributors">
        </bubble-chart>
      </div>
 
      <div class="col col-12">
        <stacked-bar-chart source="issueActivity"
                    title="Issue Activity"
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </stacked-bar-chart>
      </div>

     <div class="col col-12">
        <line-chart source="commits100"
                    title="Commits > 100 / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
    </div>
    
    <div class="col col-12">
        <line-chart source="fakes"
                    title="Fake Contributors" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
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
