<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <h1>Activity</h1>
    <div class="baseRepo">
      <h2 class="baseRepoh2">{{ $store.state.baseRepo }}</h2>
      <h2 class="baseRepo repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="baseRepo" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>
    <div class="row">

      <div class="col col-6">
        <dynamic-line-chart source="issueComments" 
                    title="Issue Comments / Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/issue-comments.md"
                    cite-text="Issue Comments"> 
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="pullRequestsMadeClosed" 
                    title="Pull Requests Made/ Closed per Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requests Made/Closed"> 
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="watchers" 
                    title="Watchers / Week " 
                    cite-url="https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/watchers.md"
                    cite-text="Watchers"> 
        </dynamic-line-chart>
      </div>
       
    </div>
    
    <small>Data provided by <a href="http://ghtorrent.org/msr14.html">GHTorrent</a> <span class="ghtorrent-version"></span> and the <a href="https://developer.github.com/">GitHub API</a></small>
  </section>
</template>

<script>

import DynamicLineChart from './charts/DynamicLineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart
  }
};

</script>
