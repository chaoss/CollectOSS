<template>
  <section>
    <h1>Growth, Maturity, and Decline</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">

      <div class="col col-6">
        <line-chart source="closedIssues"
                    title="Closed Issues / Week" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="codeCommits"
                    title="Code Commits / Week" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/commits.md"
                    cite-text="Commits">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="firstResponseToIssueDuration"
                    title="Issue Response Time" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/issue-response-time.md"
                    cite-text="Issue Response Time">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="forks"
                    title="Forks / Week" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/forks.md"
                    cite-text="Forks">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="openIssues"
                    title="Open Issues / Week" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Issues Open">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullRequestsOpen"
                    title="Pull Requests Open / Week" 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-requests-open.md"
                    cite-text="Open Pull Requests">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullRequestComments" 
                    title="Pull Request Comments / Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments"> 
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
