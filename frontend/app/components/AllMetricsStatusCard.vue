<template>
  <div class="is-table-container">

    <h3 style="padding-top: 30px; width: 100%">Metrics Status</h3>

    <div class="row">
      <div class="col col-4">
        <label>Group:</label>
        <select id="metric_group" @change="getMetricsStatus()" v-model='selected_group'>
         <option v-for="group in metadata['groups']" v-bind:value="group">
          {{ group }} 
         </option> 
        </select> 
      </div>

      <div class="col col-4">
        <label>Source:</label>
        <select id="metric_source" @change="getMetricsStatus()" v-model='selected_source'>
         <option v-for="source in metadata['sources']" v-bind:value="source">
          {{ source }} 
         </option> 
        </select> 
      </div>

      <div class="col col-4">
        <label>Metric Type:</label>
        <select id="metric_type" @change="getMetricsStatus()" v-model='selected_metric_type'>
         <option v-for="metric_type in metadata['metric_types']" v-bind:value="metric_type">
          {{ metric_type }} 
         </option> 
        </select> 
      </div>
    </div>

    <div class="row">
      <div class="col col-4">
        <label>Backend Status:</label>
        <select id="metric_backend_status" @change="getMetricsStatus()" v-model='selected_backend_status'>
         <option value="all">all</option> 
         <option value="undefined">undefined</option> 
         <option value="unimplemented">unimplemented</option> 
         <option value="implemented">implemented</option> 
        </select> 
      </div>

      <div class="col col-4">
        <label>Frontend Status:</label>
        <select id="metric_frontend_status" @change="getMetricsStatus()" v-model='selected_frontend_status'>
         <option value="all">all</option> 
         <option value="unimplemented">unimplemented</option> 
         <option value="implemented">implemented</option> 
        </select> 
      </div>

      <div class="col col-4">
        <label>Defined:</label>
        <select id="metric_is_defined" @change="getMetricsStatus()" v-model='selected_is_defined'>
         <option value="all">all</option> 
         <option value="true">true</option> 
         <option value="false">false</option> 
        </select> 
      </div>
    </div>

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
      <tr v-for="metric in metricsStatus">
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
    
  </div>
</template>

<script>

export default {

  name: 'AllMetricsStatusCard',

  data () {
    return {
      metricsStatus: [],
      metadata: {
        metricStatusMetadata: [],
        groups: [],
        sources: [],
        metric_types: []
      },
      filters: {
        selected_group: 'all',
        selected_source: 'all',
        selected_metric_type: 'all',
        selected_backend_status: 'all',
        selected_frontend_status: 'all',
        seletec_is_defined: 'all'
      }
    }
  },
  methods: {
      getMetricsStatus() {
        var query_string = "group=" + this.selected_group + 
                           "&source=" + this.selected_source + 
                           "&metric_type=" + this.selected_metric_type + 
                           "&backend_status=" + this.selected_backend_status +
                           "&frontend_status=" + this.selected_frontend_status +
                           "&is_defined=" + this.selected_is_defined

          window.AugurAPI.getMetricsStatus(query_string).then((data) => {
            this.metricsStatus = data
        })
      },
      getMetricsStatusMetadata() {
        window.AugurAPI.getMetricsStatusMetadata().then((data) => {
          this.metadata['metricStatusMetadata'] = data

          this.metadata['groups'] = Object.keys(data.groups[0])

          this.metadata['sources'] = data.sources

          this.metadata['metric_types'] = data.metric_types


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
    this.selected_group = 'all'
    this.selected_source = 'all'
    this.selected_metric_type = 'all'
    this.selected_backend_status = 'all'
    this.selected_frontend_status = 'all'
    this.selected_is_defined = 'all'
    this.getMetricsStatus()
    this.getMetricsStatusMetadata()
  }
}

</script>

<style lang="css" scoped>
</style>