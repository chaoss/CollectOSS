<template>
  <section>
    <h1>Activity</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">
      <div class="col col-12">
        <line-chart source="commits"
                    title="Commits / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>
    </div>

    <div class="row">
      <div class="col col-12">
        <line-chart source="forks"
                    title="Forks / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>
    </div>

    <div class="row">
      <div class="col col-12">
        <line-chart source="issues"
                    title="Issues / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>
    </div>

    <div class="row">
      <div class="col col-6">
        <line-chart source="pulls" 
                    title="Pulls Requests / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Contributors">
        </line-chart>
      </div>
      <div class="col col-6">
        <line-chart source="uniqueCommitters" 
                    title="Unique Committers" 
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

module.exports = {
  components: {
    LineChart
  },
  computed: {
    repo () {
      return this.$store.state.repo
    }
  }
};

</script>