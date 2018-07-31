<template>
	  <ul>
	      <li>
		    <b>Name: {{ metric.name }}</b>
		  </li>
			  <ul>
			      <li>
				    Tag: {{ metric.tag }}
				  </li>
			      <li v-if="metric.url != '/'">
				    URL: {{ metric.url }}
				  </li>
			      <li>
		 			Group: {{ metric.group }}
				  </li>
			      <li v-if="metric.endpoint != 'n/a'">
		 			Endpoint: {{ metric.endpoint }}
				  </li>
			      <li v-if="metric.source != 'n/a'">
		 			Source: {{ metric.source }}
				  </li>
			      <li>
		 			Backend Status: {{ metric.backend_status }}
				  </li>
			      <li>
		 			Frontend Status: {{ metric.frontend_status }}
				  </li>
			      <li v-if="metric.metric_type != 'n/a'">
		 			Metric Type: {{ metric.metric_type }}
				  </li>
			</ul>
	</ul>
</template>

<script>

export default {

  name: 'MetricsStatusCard',
  props: [ 'metric' ],
  data () {
    return {
    }
  },
}


</script>

<style lang="css" scoped>
</style>