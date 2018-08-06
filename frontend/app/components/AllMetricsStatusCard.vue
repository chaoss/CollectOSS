<template>
  <div class="is-table-container">
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
      <tr v-for="metric in rawMetricsStatus">
        <td v-bind:style="{ color: getBackendStatus(metric) }">{{ metric.backend_status }}</td>
        <td v-bind:style="{ color: getFrontendStatus(metric) }">{{ metric.frontend_status }}</td>
        <td>{{ metric.name }}</td>
        <td>{{ metric.group }}</td>
        <td>{{ metric.endpoint }}</td>
        <td>{{ metric.source }}</td>
        <td>{{ metric.metric_type }}</td>
      </tr>
    </table>
  </div>
</template>

<script>

export default {

  name: 'AllMetricsStatusCard',

  props: ['grouping'],

  data () {
    return {
      rawMetricsStatus: [],
    }
  },
  methods: {
      getMetricsStatus() {
        this.rawMetricsStatus = []
        window.AugurAPI.getMetricsStatus().then((data) => {
          this.rawMetricsStatus = data
      })
    },
      getBackendStatus(metric) {
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
      getFrontendStatus(metric) {
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
  }
}

</script>

<style lang="css" scoped>
</style>