<template>
	<div>
		<tr>
			<td>backend status</td>
			<td>frontend status</td>
		    <td>name</td>
		    <td>endpoint</td>
		    <td>source</td>
			<td>metric type</td>
		</tr>
		<tr>
			<td v-bind:style="{ color: backend_color }">{{ metric.backend_status }}</td>
			<td v-bind:style="{ color: frontend_color }">{{ metric.frontend_status }}</td>
			<td>{{ metric.name }}</td>
			<td>{{ metric.endpoint }}</td>
			<td>{{ metric.source }}</td>
			<td>{{ metric.metric_type }}</td>
		</tr>
	</div>
</template>

<script>
export default {

  name: "MetricStatusCard",

  props: [ "metric" ],

  data () {
    return {
    	backend_color: "#0c0",
    	frontend_color: "#0c0"
    }
  },
  methods: {
  	getBackendStatus() {
  		if (this.metric["backend_status"] == "unimplemented") {
  			this.backend_color = "#c00"
  		} 
  		else if (this.metric["backend_status"] == "undefined") {
  			this.backend_color = "#cc0"
  		} 
  		else if (this.metric["backend_status"] == "implemented") {
  			this.backend_color = "0c0"
  		}
  	},
  	getFrontendStatus() {
  		if (this.metric["frontend_status"] == "unimplemented") {
  			this.frontend_color = "#c00"
  		}   
  		else if (this.metric["frontend_status"] == "implemented") {
  			this.frontend_color = "#0c0"
  		}   
  	}
  },
  mounted() {
  	this.getBackendStatus()
  	this.getFrontendStatus()
  }
}
</script>

<style lang="css" scoped>
</style>