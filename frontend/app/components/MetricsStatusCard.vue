 <template>

  <div class="is-table-container">
    <augur-header></augur-header>
    <section>
    <h3>CHAOSS Metrics Implementation Status</h3>

    <div class="row gutters">
      <div class="col col-4">
        <label>Group:
        <select id="metric_group" @change="getMetricsStatus()" v-model='selected_group'>
         <option v-for="group in metadata['groups']" v-bind:value="group">
          {{ group }}
         </option>
        </select>
        </label>
      </div>

      <div class="col col-4">
        <label>Source:
        <select id="metric_source" @change="getMetricsStatus()" v-model='selected_source'>
         <option v-for="data_source in metadata['data_sources']" v-bind:value="data_source">
          {{ data_source }}
         </option>
        </select>
        </label>
      </div>

      <div class="col col-4">
        <label>Metric Type:
        <select id="metric_type" @change="getMetricsStatus()" v-model='selected_metric_type'>
         <option v-for="metric_type in metadata['metric_types']" v-bind:value="metric_type">
          {{ metric_type }}
         </option>
        </select>
        </label>
      </div>

      <div class="col col-12"><br></div>

      <div class="col col-4">
        <label>Backend Status:
        <select id="metric_backend_status" @change="getMetricsStatus()" v-model='selected_backend_status'>
         <option value="all">all</option>
         <option value="unimplemented">unimplemented</option>
         <option value="implemented">implemented</option>
        </select>
        </label>
      </div>

      <div class="col col-4">
        <label>Frontend Status:
        <select id="metric_frontend_status" @change="getMetricsStatus()" v-model='selected_frontend_status'>
         <option value="all">all</option>
         <option value="unimplemented">unimplemented</option>
         <option value="implemented">implemented</option>
        </select>
        </label>
      </div>

      <div class="col col-4">
        <label>Defined:
        <select id="metric_is_defined" @change="getMetricsStatus()" v-model='selected_is_defined'>
         <option value="all">all</option>
         <option value="true">true</option>
         <option value="false">false</option>
        </select>
        </label>
      </div>
    </div>
    <p></p>
    <table class="is-responsive" >
      <thead style="display:block;">
        <tr style="font-weight: 600; text-align: center">
          <td style="width: 119px !important">Backend Status</td>
          <td style="width: 135px !important">Frontend Status</td>
          <td style="width: 170px !important">Name</td>
          <td style="width: 121px !important">Group</td>
          <td style="width: 569px !important">Endpoint</td>
          <td style="width: 120px !important">Source</td>
          <td style="width: 85px !important">Metric Type</td>
        </tr>
      </thead>

      <tbody style="display:block; height: 400px; overflow-y: scroll; text-align: center; background: #eaeaea">
        <tr v-for="metric in metricsStatus">
          <div style="overflow: hidden">
            <td v-bind:style="{ color: getBackendStatusColor(metric) }" style="width: 119px !important">{{ metric.backend_status }}</td>
            <td v-bind:style="{ color: getFrontendStatusColor(metric) }" style="width: 135px !important">{{ metric.frontend_status }}</td>

            <template v-if="metric.url != '/'" >
              <td style="width: 170px !important"><a :href="metric.documentation_url">{{ metric.display_name }}</a></td>
            </template>
            <template v-else >
            <td style="width: 170px !important">{{ metric.display_name }}</td>
            </template>

            <td style="width: 121px !important">{{ metric.group }}</td>
            <td style="width: 569px !important">{{ metric.endpoint }}</td>
            <td style="width: 120px !important">{{ metric.data_source }}</td>
            <td style="width: 85px !important">{{ metric.metric_type }}</td>
          </div>
        </tr>
      </tbody>

    </table>
  </section>
  </div>
  
</template>

<script>

import AugurHeader from './AugurHeader'
export default {

  name: 'MetricsStatus',
  components: {
    AugurHeader
  },
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
                           "&data_source=" + this.selected_source +
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

          this.metadata['groups'] = Object.keys(data[0].groups)

          this.metadata['data_sources'] = data[0].data_sources

          this.metadata['metric_types'] = data[0].metric_types
        })
      },
      getImplementationStatusColor(metric, location) {
        if (metric[location] == "unimplemented") {
          return "#c00"
        }
        else if (metric[location] == "implemented") {
          return "#0c0"
        }
      },
      getBackendStatusColor(metric) {
        if (metric["backend_status"] == "unimplemented") {
          return "#c00"
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
