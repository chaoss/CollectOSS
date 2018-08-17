<template>
  <section>
    <div id="base-template" v-bind:class="{ hidden: !this.repo }"/>

      <h1>Activity Comparison</h1>
      <h2>{{ comparedTo }} compared to {{ $store.state.baseRepo }}</h2>

      <div class="row">

      <div class="col col-6">
        <line-chart source="issueComments"
                    title="Issue Comments / Week "
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

       <div class="col col-6">
        <line-chart source="pullRequestsMadeClosed" 
                    title="Pull Requests Made/ Closed per Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/tree/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requests Made/Closed"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="watchers" 
                    title="Watchers / Week " 
                    cite-url="https://github.com/OSSHealth/wg-gmd/tree/master/activity-metrics/watchers.md"
                    cite-text="Watchers"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      </div>

      <small>Data provided by <a href="http://ghtorrent.org/msr14.html">GHTorrent</a> <span class="ghtorrent-version"></span> and the <a href="https://developer.github.com/">GitHub API</a></small>
    </div>
  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'

module.exports = {
  props: ['comparedTo'],
  components: {
    LineChart,
    BubbleChart
  },
  computed: {
    repo () {
      return this.$store.state.repo
    }
  }
}

</script>
