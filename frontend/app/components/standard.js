import AugurStats from 'AugurStats'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'percentage',
    'comparedTo', 'disableRollingAverage', 'alwaysByDate', 'innerKey'],
  data () {
    return {
      data: []
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
      let config = {}

      config.earliest = this.earliest || new Date('01-01-2005')
      config.latest = this.latest || new Date()
      config.title = this.title || 'Activity'
      config.full_width = true
      config.height = 200
      config.x_accessor = 'date'
      config.format = this.percentage ? 'percentage' : undefined
      config.compare = this.compare
      config.byDate = true
      config.time_series = true
      config.area = this.rawWeekly

      this.__download_data = {}
      this.__download_file = config.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()

      var renderChart = () => {
        window.$(this.$refs.holder).find('.showme').removeClass('invis')
        this.$refs.chartholder.innerHTML = ''
        this.$refs.chartholder.appendChild(config.target)
        this.$refs.chart.className = 'linechart'
        window.MG.data_graphic(config)
      }

      if (this.repo) {
        if (this.$refs.chart) {
          this.$refs.chart.className = 'linechart loader'
          window.$(this.$refs.holder).find('.hideme').addClass('invis')
          window.$(this.$refs.holder).find('.showme').removeClass('invis')
        }
        // Create element to hold the chart
        config.target = document.createElement('div')
        window.AugurRepos[this.repo][this.source]()
          .then((baseData) => {
            this.__download_data.base = baseData
            this.$refs.chartStatus.innerHTML = ''
            if (baseData && baseData.length) {
              config.data = AugurStats.convertDates(baseData, this.earliest, this.latest)
            } else {
              config.data = []
            }
            if (this.comparedTo) {
              return window.AugurRepos[this.comparedTo][this.source]()
            }
            return new Promise((resolve, reject) => { resolve() })
          })
          .then((compareData) => {
            this.__download_data.compare = compareData
            this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
            this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')
            let keys = Object.keys(config.data[0]).splice(1)
            let key = this.innerKey || keys[0]
            if (config.data && compareData && compareData.length) {
            // If there is comparedData, do the necesarry computations for
            // the comparision
              if (config.compare === 'each') {
                compareData = AugurStats.convertDates(compareData, this.earliest, this.latest)

                let compare = AugurStats.rollingAverage(AugurStats.zscores(compareData, key), 'value', this.period)
                let base = AugurStats.rollingAverage(AugurStats.zscores(config.data, key), 'value', this.period)
                config.data = [base, compare]
                config.legend = [window.AugurRepos[this.repo].toString(), window.AugurRepos[this.comparedTo].toString()]
                config.colors = config.colors || ['#FF3647', '#999']
              } else {
                config.format = 'percentage'
                config.baselines = [{value: 1, label: config.baseline}]
                config.data = AugurStats.makeRelative(config.data, compareData, {
                  earliest: config.earliest,
                  latest: config.latest,
                  byDate: config.byDate,
                  period: this.period
                })
                config.x_accessor = (config.byDate) ? 'date' : 'x'
              }
            } else {
            // Otherwise, render a normal timeseries chart
              if (!this.disableRollingAverage) {
                config.legend = config.legend || [config.title.toLowerCase(), this.period + ' day average']
                let rolling = AugurStats.rollingAverage(config.data, key, this.period)
                if (this.rawWeekly) {
                  config.data = AugurStats.combine(rolling, config.data)
                } else {
                  config.data = rolling
                }
                config.colors = config.colors || ['#FF3647', '#CCC']
                config.y_accessor = 'value'
              } else {
                config.legend = config.legend || [config.title.toLowerCase()]
                config.colors = config.colors || ['#FF3647', '#CCC']
                config.y_accessor = 'value'
              }
              config.data = AugurStats.convertKey(config.data, key)
            }

            config.y_mouseover = '%d'

            config.legend_target = this.$refs.legend

            this.$refs.chart.className = 'linechart intro'
            window.$(this.$refs.holder).find('.hideme').removeClass('invis')

            window.$(config.target).hover((onEnterEvent) => {
              window.$(this.$refs.legend).hide()
            }, (onLeaveEvent) => {
              window.$(this.$refs.legend).show()
            })
            renderChart()
          }) // end then()
          .catch((reject) => {
            config = {
              error: config.title + 'is missing data',
              chart_type: 'missing-data',
              missing_text: config.title + ' is missing data',
              target: config.target,
              full_width: true,
              height: 200
            }
            renderChart()
          })
        return '<div class="loader">' + this.title + '...</div>'
      } // end if (this.$store.repo)
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
    }
  }// end methods
} // end export default {}
