<template>
  <div class="is-table-container">
    <template v-for="group in metricGroups">
      <h3 style="padding-top: 30px; width: 100%">{{ metricGroupNames[group] }}</h3>
      <table class="is-responsive">
        <tr>
          <td>backend status</td>
          <td>frontend status</td>
          <td>name</td>
          <td>group</td>
          <td>endpoint</td>
          <td>source</td>
          <td>metric type</td>
        </tr>
        <tr v-for="metric in metricsStatus" v-if="metric.group == group">
          <td v-bind:style="{ color: getBackendStatusColor(metric) }">{{ metric.backend_status }}</td>
          <td v-bind:style="{ color: getFrontendStatusColor(metric) }">{{ metric.frontend_status }}</td>

          <template v-if="metric.url != '/'" >
          <td><a :href="metric.url">{{ metric.name }}</a></td>
          </template>

          <template v-else >
          <td>{{ metric.name }}</td>
          </template>

          <td>{{ metric.group }}</td>
          <td>{{ metric.endpoint }}</td>
          <td>{{ metric.source }}</td>
          <td>{{ metric.metric_type }}</td>
        </tr>
      </table>
    </template>
  </div>
</template>

<script>

export default {

  name: 'AllMetricsStatusCard',

  data () {
    return {
      metricsStatus: [],
      metricsStatusMetadata: [],
      metricGroups: [],
      metricGroupNames: []
    }
  },
  methods: {
      getMetricsStatus() {
          window.AugurAPI.getMetricsStatus().then((data) => {
            this.metricsStatus = data
        })
      },
      getMetricsStatusMetadata() {
        window.AugurAPI.getMetricsStatusMetadata().then((data) => {
          this.metricsStatusMetadata = data
          this.metricGroups = Object.keys(this.metricsStatusMetadata.groups[0])
          this.metricGroupNames = this.metricsStatusMetadata.groups[0]

        })
      },
      getBackendStatusColor(metric) {
        if (metric["backend_status"] == "unimplemented") {
          return "#c00"
        } 
        else if (metric["backend_status"] == "undefined") {
          return "#cc0"
        } 
        else if (metric["backend_status"] == "implemented") {
          return "#0c0"
        }
      },
      getFrontendStatusColor(metric) {
        if (metric["frontend_status"] == "unimplemented") {
          return "#c00"
        }   
        else if (metric["frontend_status"] == "implemented") {
          return "#0c0"
        }   
      },
    },
  mounted() {
    this.getMetricsStatus()
    this.getMetricsStatusMetadata()
  }
}

</script>

<style lang="css" scoped>
</style>