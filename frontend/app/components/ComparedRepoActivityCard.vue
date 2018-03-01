<template>
  <section>
    <div id="base-template" v-bind:class="{ hidden: !this.repo }"/>

      <h1>Activity Comparison</h1>
      <h2>{{ comparedTo }} compared to {{ $store.state.baseRepo }}</h2>

      <div class="row">

        <div class="col col-6">
        <line-chart source="commits"
                    title="Commits / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="forks"
                    title="Forks / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issues"
                    title="Issues / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issueComments" 
                    title="Issue Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="commitComments" 
                    title="Commit Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullReqComments" 
                    title="Pull Request Comments / Week " 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullsAcceptanceRate" 
                    title="Pull Acceptance Rate" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pulls" 
                    title="Pulls Requests / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="issuesClosed" 
                    title="Issues Closed / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    v-bind:compared-to="comparedTo"> 
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="totalCommitters" 
                    title="Total Committers" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors"
                    disableRollingAverage=1
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

module.exports = {
  props: ['comparedTo'],
  components: {
    LineChart
  },
  computed: {
    repo () {
      return this.$store.state.repo
    }
  }
}

</script>