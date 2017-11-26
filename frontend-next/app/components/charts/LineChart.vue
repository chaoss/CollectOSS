<template>
  <div>
    <div ref="chart" class="linechart">
      <div ref="legend" class="legend"></div>
      <span ref="chartStatus" v-html="chart"></span>
    </div>
    <cite class="metric">Metric: <a v-bind:href="citeURL" target="_blank">{{ citeText }}</a></cite></div>
  </div>
</template>


<script>
import * as d3 from 'd3'
import GHDataStats from 'GHDataStats'
import { mapState } from 'vuex'
import MG from '../../include/metricsgraphics';

console.log(d3)

export default {
  props: ['source', 'citeURL', 'citeText', 'title', 'percentage', 'comparedTo', 'disableRollingAverage'],
  computed: {
    repo() {
      return this.$store.state.baseRepo
    },
    period() {
      return this.$store.state.trailingAverage
    },
    earliest() {
      return this.$store.state.startDate
    },
    latest() {
      return this.$store.state.endDate
    },
    compare() {
      return this.$store.state.compare
    },
    chart () {
      let config = {};
  /*+-------------------+--------------------------------+-----------------------+
    | Parameter         | Source                         | Default               |
    +-------------------+--------------------------------+-----------------------+*/
      config.period     = this.period                   || 180
      config.earliest   = this.earliest                 || new Date('01-01-2005')
      config.latest     = this.latest                   || new Date()
      config.title      = this.title                    || "Activity"
      config.full_width = true
      config.height     = 200
      config.x_accessor = 'date'
      config.target     = this.$refs.chart
      config.format     = this.percentage ? 'percentage' : undefined;
  /*+-------------------+--------------------------------+------------------------+*/

      if (this.repo) {
        if (this.$refs.chart) {
          this.$refs.chart.className = 'linechart loader'
        }
        window.GHDataRepos[this.repo][this.source]().then((baseData) => {
          this.$refs.chartStatus.innerHTML = ''
          if (baseData && baseData.length) {
            config.data = GHDataStats.convertDates(baseData, this.earliest, this.latest)
          } else {
            config.data = []
          }
          if (this.comparedTo) {
            if (this.compare === "percentage") {
              config.baselines = [{value: 1, label: config.baseline}]
              return GHDataRepos[this.repo][this.source].relativeTo(GHDataRepos[this.comparedTo])
            } else {
              console.log(this.comparedTo)
              return GHDataRepos[this.comparedTo][this.source]()
            } 
          }
          return new Promise((resolve, reject) => { resolve() });
        }).then((compareData) => {
          console.log(compareData)
          if (compareData && compareData.length) {
            // If there is comparedData, render a comparison chart
            config.data = GHDataStats.makeRelative(config.data, compareData, config)
          } else {
            // Otherwise, render a normal timeseries chart
            let keys = Object.keys(config.data[0]).splice(1)
            if (!this.disableRollingAverage) {
              config.legend = config.legend || [config.title.toLowerCase(), config.period + ' day average']
              let rolling = GHDataStats.rollingAverage(config.data, keys[0], config.period)
              config.data = GHDataStats.convertKey(GHDataStats.combine(config.data, rolling), keys[0])
              config.colors = config.colors ||['#CCC', '#FF3647']
              config.y_accessor = 'value';
            }
            if (Array.isArray(config.data[0])) {
              config.legend = config.legend || ['compared', 'base']
              config.colors = config.colors || ['#FF3647', '#999']
              config.y_accessor = config.y_accessor || 'value'
            } else {
              config.y_accessor = keys
              config.legend = config.y_accessor
            }

            if (keys.length > 1) {
              config.legend_target = this.$refs.legend
              $(this.$refs.chart).hover(() => {
                this.$refs.legend.style.display = 'none'
              }, () => {
                this.$refs.legend.style.display = 'block'
              })
            }
            this.$refs.chart.className = 'linechart intro'
            MG.data_graphic(config)
          }
        }) // end then()
        return '<div class="loader">' + this.title + '...</div>' 
      } // end if (this.$store.repo)   
    } // end chart()
  } // end computed
} // end export default {}

</script>