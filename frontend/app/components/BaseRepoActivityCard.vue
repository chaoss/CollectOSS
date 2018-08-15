<template>
  <section>
    <h1>Activity</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">

      <div class="col col-6">
        <line-chart source="issueComments" 
                    title="Issue Comments / Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/tree/master/activity-metrics/issue-comments.md"
                    cite-text="Issue Comments"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullRequestsMadeClosed" 
                    title="Pull Requests Made/ Closed per Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/tree/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requests Made/Closed"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="watchers" 
                    title="Watchers / Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/tree/master/activity-metrics/watchers.md"
                    cite-text="Watchers"> 
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
