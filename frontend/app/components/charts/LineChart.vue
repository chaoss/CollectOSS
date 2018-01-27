<template>
  <div>
    <cite class="metric">Metric: <a v-bind:href="citeUrl" target="_blank">{{ citeText }}</a><button class="button small outline download" v-on:click="downloadSVG">&#11015; SVG</button><button class="button small outline download" v-on:click="downloadPNG">&#11015; PNG</button></cite>
    <div ref="chart" class="linechart">
      <div ref="chartholder"></div>
      <div ref="legend" class="legend"></div>
      <span ref="chartStatus" v-html="chart"></span>
    </div>
  </div>
</template>


<script>
import * as d3 from 'd3'
import GHDataStats from 'GHDataStats'
import { mapState } from 'vuex'
import MG from '../../include/metricsgraphics';
import SvgSaver from '../../include/svgsaver';

console.log(d3)

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'percentage', 
          'comparedTo', 'disableRollingAverage', 'alwaysByDate'],
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
      config.earliest   = this.earliest                 || new Date('01-01-2005')
      config.latest     = this.latest                   || new Date()
      config.title      = this.title                    || "Activity"
      config.full_width = true
      config.height     = 200
      config.x_accessor = 'date'
      config.format     = this.percentage ? 'percentage' : undefined;
      config.compare    = this.compare
      config.byDate     = true
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
            return GHDataRepos[this.comparedTo][this.source]()
          }
          return new Promise((resolve, reject) => { resolve() });
        }).then((compareData) => {
          let keys = Object.keys(config.data[0]).splice(1)
          if (config.data && compareData && compareData.length) {
            // If there is comparedData, do the necesarry computations for
            // the comparision
            if (config.compare == 'each') {
              compareData = GHDataStats.convertDates(compareData, this.earliest, this.latest)
              let key = Object.keys(compareData[0])[1]
              let compare = GHDataStats.rollingAverage(GHDataStats.zscores(compareData, key), 'value', this.period)
              let base = GHDataStats.rollingAverage(GHDataStats.zscores(config.data, key), 'value', this.period)
              config.data = [base, compare]
              config.legend = [window.GHDataRepos[this.repo].toString(), window.GHDataRepos[this.comparedTo].toString()]
              config.colors = config.colors || ['#FF3647', '#999']
            } else {
              config.format = 'percentage'
              config.baselines = [{value: 1, label: config.baseline}]
              config.data = GHDataStats.makeRelative(config.data, compareData, {
                earliest: config.earliest,
                latest: config.latest,
                byDate: config.byDate,
                period: this.period
              })
              config.x_accessor = (config.byDate) ? 'date' : 'x';
            }
          } else {
            // Otherwise, render a normal timeseries chart
            if (!this.disableRollingAverage) {
              config.legend = config.legend || [config.title.toLowerCase(), this.period + ' day average']
              let rolling = GHDataStats.rollingAverage(config.data, keys[0], this.period)
              config.data = GHDataStats.convertKey(GHDataStats.combine(config.data, rolling), keys[0])
              config.colors = config.colors ||['#CCC', '#FF3647']
              config.y_accessor = 'value'
            }
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
          config.target = document.createElement('div');
          this.$refs.chartholder.innerHTML = '';
          this.$refs.chartholder.appendChild(config.target)
          console.log('finalized config that will be sent', config)
          MG.data_graphic(config)
        }) // end then()
        return '<div class="loader">' + this.title + '...</div>' 
      } // end if (this.$store.repo)   
    } // end chart()
  }, // end computed
  methods: {
    downloadSVG (e) {
      var svgsaver = new SvgSaver();                      // creates a new instance
      var svg = $(this.$refs.chartholder).find("svg")[0];    // find the SVG element
      svgsaver.asSvg(svg);                                // save as SVG
    },
    downloadPNG (e) {
      var svgsaver = new SvgSaver();                      // creates a new instance
      var svg = $(this.$refs.chartholder).find("svg")[0];    // find the SVG element
      svgsaver.asPng(svg);                                // save as SVG
    }
  }//end methods
} // end export default {}


</script>