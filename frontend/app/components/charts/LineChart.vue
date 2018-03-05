<template>
  <div ref="holder">
    <div ref="chart" class="linechart">
      <div ref="legend" class="legend hideme invis"></div>
      <div ref="chartholder"></div>
      <span ref="chartStatus" class="showme" v-html="chart"></span>
    </div>
    <div class="row below-chart hideme invis">
      <div class="col col-6"><cite class="metric">Metric: <a v-bind:href="citeUrl" target="_blank">{{ citeText }}</a></cite></div>
      <div class="col col-6"><button class="button download graph-download" v-on:click="downloadSVG">&#11015; SVG</button><button class="button graph-download download" v-on:click="downloadPNG">&#11015; PNG</button><a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
    </div>
  </div>
</template>


<script>
import GHDataStats from 'GHDataStats'
import { mapState } from 'vuex'
import EmptyChart from './EmptyChart'

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
      config.time_series = true
  /*+-------------------+--------------------------------+------------------------+*/

      this.__download_data = {}
      this.__download_file = config.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()

      var renderChart = () => {
        $(this.$refs.holder).find('.showme').removeClass('invis')
        this.$refs.chartholder.innerHTML = '';
        this.$refs.chartholder.appendChild(config.target)
        this.$refs.chart.className = 'linechart'
        MG.data_graphic(config)
      }

      if (this.repo) {
        if (this.$refs.chart) {
          this.$refs.chart.className = 'linechart loader'
          $(this.$refs.holder).find('.hideme').addClass('invis')
          $(this.$refs.holder).find('.showme').removeClass('invis')
        }
        // Create element to hold the chart
        config.target = document.createElement('div');
        window.GHDataRepos[this.repo][this.source]().
        then((baseData) => {
          this.__download_data.base = baseData;
          this.$refs.chartStatus.innerHTML = ''
          if (baseData && baseData.length) {
            config.data = GHDataStats.convertDates(baseData, this.earliest, this.latest)
          } else {
            config.data = []
          }
          if (this.comparedTo) {
            return window.GHDataRepos[this.comparedTo][this.source]()
          }
          return new Promise((resolve, reject) => { resolve() });
        })
        .then((compareData) => {
          this.__download_data.compare = compareData;
          this.$refs.downloadJSON.href = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.__download_data))
          this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')
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
              console.log(key, compareData, config.data)
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
              config.data = GHDataStats.combine(config.data, rolling)
              config.colors = config.colors ||['#CCC', '#FF3647']
              config.y_accessor = 'value'
            } else {
              config.legend = config.legend || [config.title.toLowerCase()]
              config.colors = config.colors ||['#CCC', '#FF3647']
              config.y_accessor = 'value'
            }
            config.data = GHDataStats.convertKey(config.data, keys[0])
          }
          
          config.y_mouseover = '%d';

          config.legend_target = this.$refs.legend

          this.$refs.chart.className = 'linechart intro'
          $(this.$refs.holder).find('.hideme').removeClass('invis')

          $(config.target).hover((onEnterEvent) => {
            $(this.$refs.legend).hide()
          }, (onLeaveEvent) => {
            $(this.$refs.legend).show()
          })
          renderChart();
        }) // end then()
        .catch((reject) => {
          config = {
            error: config.title + 'is missing data',
            chart_type: 'missing-data',
            missing_text: config.title + ' is missing data',
            target: config.target,
            full_width: true,
            height: 200
          };
          renderChart();
        })
        return '<div class="loader">' + this.title + '...</div>' 
      } // end if (this.$store.repo)   
    } // end chart()
  }, // end computed
  methods: {
    downloadSVG (e) {
      var svgsaver = new SvgSaver()
      var svg = $(this.$refs.chartholder).find("svg")[0]
      svgsaver.asSvg(svg, this.__download_file + '.svg')
    },
    downloadPNG (e) {
      var svgsaver = new SvgSaver();
      var svg = $(this.$refs.chartholder).find("svg")[0]
      svgsaver.asPng(svg, this.__download_file + '.png')
    }
  }//end methods
} // end export default {}


</script>