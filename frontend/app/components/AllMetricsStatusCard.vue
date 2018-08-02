<template>
	<div>
		<h2>Diversity and Inclusion</h2>
		<template v-for="metric in metricsStatus">
			<table class="metrics-status-card">
				<metric-status-card :metric="metric"></metric-status-card>
			</table>
		</template>
	</div>
</template>

<script>

import MetricStatusCard from './MetricStatusCard.vue'

export default {

  components: {
    MetricStatusCard,
  },

  name: 'AllMetricsStatusCard',

  data () {
    return {
      metricsStatus: []
    }
  },
  methods: {
    getMetricsStatus() {
      this.metricsStatus = []
      window.AugurAPI.getMetricsStatus().then((data) => {
        this.metricsStatus = data
	  })
    },
  },
  mounted() {
    this.getMetricsStatus()
  }
}


</script>

<style lang="css" scoped>
</style>