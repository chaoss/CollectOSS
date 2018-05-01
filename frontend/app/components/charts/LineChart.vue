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
import AugurStats from 'AugurStats'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'percentage',
    'comparedTo', 'disableRollingAverage', 'alwaysByDate', 'innerKey'],
  data () {
    return {
      mgConfig: {
        time_series: true,
        full_width: true,
        height: 200,
        y_mouseover: '%d'
      },
      graphData: {}
    }
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    period () {
      return this.$store.state.trailingAverage
    },
    earliest () {
      return this.$store.state.startDate
    },
    latest () {
      return this.$store.state.endDate
    },
    compare () {
      return this.$store.state.compare
    },
    rawWeekly () {
      return this.$store.state.rawWeekly
    },
    chart () {
      // Set the MetricsGraphics config as much as we can
      this.mgConfig.title = this.title || 'Activity'
      this.mgConfig.x_accessor = 'date'
      this.mgConfig.format = this.percentage ? 'percentage' : undefined
      this.mgConfig.compare = this.compare
      this.mgConfig.byDate = true
      this.mgConfig.area = this.rawWeekly
      this.mgConfig.y_accessor = 'value'
      this.mgConfig.legend_target = this.$refs.legend
      this.mgConfig.colors = []
      this.mgConfig.legend = []
      this.mgConfig.baselines = []

      this.__download_data = {}
      this.__download_file = this.mgConfig.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()

      // Hide the old chart
      if (this.$refs.chart) {
        this.$refs.chart.className = 'linechart loader'
        window.$(this.$refs.holder).find('.hideme').addClass('invis')
        window.$(this.$refs.holder).find('.showme').removeClass('invis')
      }
      this.mgConfig.target = document.createElement('div')

      /*
       * Takes a string like "commits,lines_changed:additions+deletions"
       * and makes it into an array of endpoints:
       *
       *   endpoints = ['commits','lines_changed']
       *
       * and a map of the fields wanted from those endpoints:
       *
       *   fields = {
       *     'lines_changed': ['additions', 'deletions']
       *   }
       */
      let endpoints = []
      let fields = {}
      this.source.split(',').forEach((endpointAndFields) => {
        let split = endpointAndFields.split(':')
        endpoints.push(split[0])
        if (split[1]) {
          fields[split[0]] = split[1].split('+')
        }
      })

      console.log('endp, f', endpoints, fields)

      // Get the repos we need
      let repos = []
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo])
      } // end if (this.$store.repo)
      if (this.comparedTo) {
        repos.push(window.AugurRepos[this.comparedTo])
      }

      // Make a batch request for all the data we need
      window.AugurAPI.batchMapped(repos, endpoints).then((data) => {
        // Make it so the user can save the data we are using
        this.__download_data = data
        this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
        this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')

        // We usually want to limit dates and convert the key to being metrics-graphics friendly
        let defaultProcess = (obj, key, field, count) => {
          let d = AugurStats.convertKey(obj[key], field)
          d = AugurStats.convertDates(d, this.earliest, this.latest)
          return d
        }

        // Normalize the data into [{ date, value },{ date, value }]
        // BuildLines iterates over the fields requested and runs onCreateData on each
        let normalized = []
        let buildLines = (obj, onCreateData) => {
          if (!obj) {
            return
          }
          if (!onCreateData) {
            onCreateData = (obj, key, field, count) => {
              let d = defaultProcess(obj, key, field, count)
              normalized.push(d)
            }
          }
          let count = 0
          for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
              if (fields[key]) {
                fields[key].forEach((field) => {
                  onCreateData(obj, key, field, count)
                  count++
                })
              } else {
                let field = Object.keys(obj[key][0]).splice(1)
                onCreateData(obj, key, field, count)
                count++
              }
            } // end hasOwnProperty
          } // end for in
        } // end normalize function

        // Build the lines we need
        if (!this.comparedTo) {
          buildLines(data[this.repo], (obj, key, field, count) => {
            // Build basic chart using rolling averages
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(d, 'value', this.period)
            if (!this.disableRollingAverage) {
              normalized.push(rolling)
              this.mgConfig.legend.push(field)
              this.mgConfig.colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }
            if (this.rawWeekly || this.disableRollingAverage) {
              normalized.push(d)
              this.mgConfig.legend.push(field)
              this.mgConfig.colors.push(this.disableRollingAverage ? window.AUGUR_CHART_STYLE.brightColors[count] : window.AUGUR_CHART_STYLE.dullColors[count])
            }
          })
        } else if (this.compare === 'each' && this.comparedTo) {
          // Build comparison using z-scores
          buildLines(data[this.comparedTo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period)
            normalized.push(rolling)
            this.mgConfig.legend.push(this.comparedTo + ' ' + field)
            this.mgConfig.colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          })
          buildLines(data[this.repo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period)
            normalized.push(rolling)
            this.mgConfig.legend.push(this.repo + ' ' + field)
            this.mgConfig.colors.push(window.AUGUR_CHART_STYLE.dullColors[count])
          })
        } else if (this.comparedTo) {
          // Build chart compared to baseline
          this.mgConfig.baselines = [{value: 1, label: this.repo}]
          buildLines(data[this.comparedTo], (obj, key, field, count) => {
            normalized.push(AugurStats.makeRelative(obj[key], data[this.repo][key], field, {
              earliest: this.earliest,
              latest: this.latest,
              byDate: true,
              period: this.period
            }))
            this.mgConfig.legend.push(this.comparedTo + ' ' + field)
            this.mgConfig.colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          })
        }

        this.mgConfig.data = normalized
        this.mgConfig.legend_target = this.$refs.legend
        this.renderChart()
      }) // end batch request

      return '<div class="loader deleteme">' + this.title + '...</div>'
    } // end chart()
  }, // end computed
  methods: {
    downloadSVG (e) {
      var svgsaver = new window.SvgSaver()
      var svg = window.$(this.$refs.chartholder).find('svg')[0]
      svgsaver.asSvg(svg, this.__download_file + '.svg')
    },
    downloadPNG (e) {
      var svgsaver = new window.SvgSaver()
      var svg = window.$(this.$refs.chartholder).find('svg')[0]
      svgsaver.asPng(svg, this.__download_file + '.png')
    },
    renderChart () {
      this.$refs.chart.className = 'linechart intro'
      window.$(this.$refs.holder).find('.hideme').removeClass('invis')
      window.$(this.$refs.holder).find('.showme').removeClass('invis')
      window.$(this.$refs.holder).find('.deleteme').remove()
      window.$(this.mgConfig.target).hover((onEnterEvent) => {
        window.$(this.$refs.legend).hide()
      }, (onLeaveEvent) => {
        window.$(this.$refs.legend).show()
      })
      this.$refs.chartholder.innerHTML = ''
      this.$refs.chartholder.appendChild(this.mgConfig.target)
      this.mgConfig.target.className = 'deleteme'
      window.MG.data_graphic(this.mgConfig)
    }
  }// end methods
} // end export default {}
</script>