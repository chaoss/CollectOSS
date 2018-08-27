<template>
  <div ref="holder">
    <div class="spacing"></div>
    <div class="error hidden"><br>Data is missing or unavailable</div>
    <div class="spinner loader"></div>
    <div class="hidefirst linechart" v-bind:class="{ invis: !detail, invisDet: detail }">
      <vega-lite :spec="spec" :data="values"></vega-lite>

      <p> {{ chart }} </p>
    </div>




    <div class="row below-chart">
      <div class="col col-5"><cite class="metric">Metric: <a v-bind:href="citeUrl" target="_blank">{{ citeText }}</a></cite></div>
      <div class="col col-6"><button class="button download graph-download" v-on:click="downloadSVG">&#11015; SVG</button><button class="button graph-download download" v-on:click="downloadPNG">&#11015; PNG</button><a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
      <!-- <div class="form-item form-checkboxes">
        <label class="checkbox"><input name="hidearea" value="each" type="checkbox" v-model="ar">Individual area<sup class="warn"></sup></label><br>
      </div> -->
    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'


export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'comparedTo'],
  data() {
    return {
      legendLabels: [],
      values: [],
      status: {
        base: true,
        compared: true
      },
      detail: this.$store.state.showDetail
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
    comparedRepos () {
      return this.$store.state.comparedRepos
    },
    rawWeekly () {
      return this.$store.state.rawWeekly
    },
    showArea () {
      return this.$store.state.showArea
    },
    showTooltip () {
      return this.$store.state.showTooltip
    },
    showDetail () {
      return this.$store.state.showDetail
    },
    spec() {

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "config":{
              "axis":{
                "grid": false
              },
              "legend": {
                "offset": -505,
                "titleFontSize": 0,
                "titlePadding": 10
              },
            },
        "vconcat": [
          {
            "title": {
            "text": this.title,
            "offset": 15
            },
            "width": 520,
            "height": 250,
            "layer": []
          }
        ]
      }

      let brush = {"filter": {"selection": "brush"}}
      if(!this.showDetail) brush = {"filter": "datum.date > 0"}

      //cannot have duplicate selection, so keep track if it has already been added
      let selectionAdded = false

      let getStandardLine = (key) => {
        let raw = true
        let opacity = 1
        if(key.substring(key.length - 7) == "Rolling") raw = false
        let range = ['#FF3647', '#4736FF']
        if (!this.status.base){
          range = ['#7d7d7d', '#4736FF']
        }
        if (!this.status.compared){
          range = ['#7d7d7d', '#4736FF']
        }
        selectionAdded = true
        return {
            "transform": [
              brush
          ],
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {"format": "%b %Y", "title": " "}
              },
              "y": {
                "field": key,
                "type": "quantitative",
                "axis": {
                  "title": null
                }
              },
              "color": {
                "field": "name",
                "type": "nominal",
                "scale": { "range": range }
                // "value": color
              },
              "opacity": {
                "value": opacity
              }
            },
            "mark": {
              "type": "line",
              //"interpolate": "basis",
              "clip": true
            }
          }
      }

      let getToolPoint = (key) => {
        let selection = {
              "tooltip": {
                "type": "single",
                "on": "mouseover",
                "encodings": [
                  "x"
                ],
                "empty": "none"
              }
            }
        let size = 17

        var timeDiff = Math.abs(this.latest.getTime() - this.earliest.getTime());
        var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
        size = diffDays / 150
        if (this.rawWeekly) size = 3
        if (selectionAdded) {
          selection = null
        }
        selectionAdded = true
        return {
            "transform": [
              brush
            ],
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {"format": "%b %Y", "title": " "}
              },
              "opacity": {
                "value": 0
              },
              "size": {
                "value": size
              }
            },
            "mark": {
              "type": "rule",
              "clip": true
            },
            "selection": selection
          }
      }

      let getStandardPoint = (key) => {
        let selection = {
              "tooltip": {
                "type": "interval",
                "nearest": true,
                "on": "mouseover",
                "encodings": [
                  "x"
                ],
                "empty": "none"
              }
            }
        if (selectionAdded) {
          selection = null
        }
        selectionAdded = true
        let raw = true
        if(key.substring(key.length - 7) == "Rolling") raw = false
        let range = ['#FF3647', '#4736FF']
        if (!this.status.base){
          range = ['#7d7d7d', '#4736FF']
        }
        if (!this.status.compared){
          range = ['#7d7d7d', '#4736FF']
        }
        return {
            "transform": [
              brush
          ],
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {
                  "title": " ",
                  "format": "%b %Y"
                },
              },
              "y": {
                "field": key,
                "type": "quantitative",
                "axis": {
                  "title": null
                }
              },
              "color": {
                "field": "name",
                "type": "nominal",
                "scale": { "range": range }
                // "value": color
              },
              "opacity": {
                "condition": {
                  "selection": "tooltip",
                  "value": 1
                },
                "value": 0
              }
            },
            "mark": {
              "type": "point"
            },
            "selection": selection
          }
      }

    let getArea = function (extension) {
      return {
        "transform": [
          brush
        ],
        "mark": {
          "type": "area",
          "interpolate": "basis",
          "clip": true
        },
        "encoding": {
                  "x": {
                    "field": "date",
                    "type": "temporal",
                    "axis": {"format": "%b %Y", "title": " "}
                  },
                  "y": {
                    "field": "lower" + extension,
                    "type": "quantitative",
                    "axis": {
                      "title": null
                    }
                  },
                  "y2": {
                    "field": "upper" + extension,
                    "type": "quantitative",
                    "axis": {
                      "title": null
                    }
                  },
                  "color": {
                    "value": "gray"
                  },
                  "opacity": {"value": 0.14}
                }
      }
    }

    let rule =
      {
      "transform": [
            {
              "filter": {
                "selection": "tooltip"
              }
            }
          ],
      "mark": "rule",
      "encoding": {
        "x": {
              "type": "temporal",
              "field": "date",
              "axis": {"format": "%b %Y", "title": " "}
            },
            "color": {
              "value": "black"
            }
        }
      }

      let getValueText = function (key){
          return {

          "transform": [
            {
              "filter": {
                "selection": "tooltip"
              }
            }
          ],
          "mark": {
            "type": "text",
            "align": "left",
            "dx": 5,
            "dy": -5
          },
          "encoding": {
            "text": {
              "type": "quantitative",
              "field": key
            },
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": {"format": "%b %Y", "title": " "}
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
                "value": "green"
              }
          }
        }
      }

      let getDateText = function (key) {
        return {

          "transform": [
            {
              "filter": {
                "selection": "tooltip"
              }
            }
          ],
          "mark": {
            "type": "text",
            "align": "left",
            "dx": 5,
            "dy": -15
          },
          "encoding": {
            "text": {
              "type": "temporal",
              "field": "date"
            },
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": {"format": "%b %Y", "title": " "}
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
                "value": "black"
              }
          }
        }
      }

      let getDetail = (key) => {
        let color = '#FF3647'
        if (!this.status.compared || !this.status.base) color = '#4736FF'
        return {
            "width": 520,
            "height": 60,
            "mark": "line",
            "title": {
              "text": " "
            },
            "selection": {
              "brush": {"type": "interval", "encodings": ["x"]}
            },
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {"format": "%b %Y", "title": " "}
              },
              "y": {
                "field": key,
                "type": "quantitative",
                "axis": {
                  "title": null
                }
              },
              "opacity": {
                "value": 0.5
              },
              "color": {
                "value": color
              }
            }


          }
      }

      //so we can reference these props inside of functions
      let comparedTo = this.comparedTo
      let rawWeekly = this.rawWeekly

      let buildMetric = () => {
        //build lines and points for initial repo
        buildLines("valueRolling")

        //build lines and points for compared repo
        if(this.comparedTo) buildLines("comparedValueRolling")
        if(this.rawWeekly) {
          buildLines("value")
          if(comparedTo) buildLines("comparedValue")
        }

      }

      let buildLines = function (key) {
        config.vconcat[0].layer.push(getStandardLine(key))
      }

      let buildTooltip = function (key) {
        config.vconcat[0].layer.push(getToolPoint(key))
        config.vconcat[0].layer.push(getStandardPoint(key))
        config.vconcat[0].layer.push(getValueText(key))
        config.vconcat[0].layer.push(getDateText(key))
      }

      if(this.showDetail) {
        if (this.comparedTo && !this.status.compared)
          config.vconcat[1] = (getDetail("comparedValueRolling"))
        else
          config.vconcat[1] = (getDetail("valueRolling"))

        //if (this.comparedTo) config.vconcat[1] = (getDetail("comparedValueRolling"))
      }
      else {
        //if user doesn't want detail, then set vconcat to og
        if (config.vconcat[1]) config.vconcat.pop()
      }

      //push the area to general spec
      if(this.showArea) {
        config.vconcat[0].layer.push(getArea(""))
        if(comparedTo){
          config.vconcat[0].layer.push(getArea("Compared"))
        }
      }
      else {
        //if user doesn't want area mark, then set layers to og
        for(var x = 0; x < config.vconcat[0].layer.length; x++) {
          if(config.vconcat[0].layer[x] == getArea("")) {
            buildMetric()
          }
        }
      }

      //push the tooltip to general spec
      if(this.showTooltip) {
        if(this.rawWeekly){
          buildTooltip("value")
        } else buildTooltip("valueRolling")

        //push parts of layer that use "comparedValue" key if there is a comparedRepo
        if(this.comparedTo){
          if(this.rawWeekly){
            buildTooltip("comparedValue")
          } else buildTooltip("comparedValueRolling")
          config.vconcat[0].layer.push(rule)
        }
      } else {
        //if user doesn't want tooltip mark, then iterate through all marks and pop the tooltip marks
        for(var x = 0; x < config.vconcat[0].layer.length; x++) {
          if(config.vconcat[0].layer[x] == getValueText("valueRolling")) {
            config.vconcat[0].layer = []
            buildMetric()
          }
        }
      }

      buildMetric()

      //set dates from main control options
      if(this.showDetail) {
        config.vconcat[1].encoding.x["scale"] =
          {
            "domain": [{"year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate()},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
          }
      }
      else {
        for(var i = 0; i < config.vconcat[0].layer.length; i++){
          config.vconcat[0].layer[i].encoding.x["scale"] =
            {
              "domain": [{"year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate()},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
            }
        }
      }

      if ((!this.status.base && !this.comparedTo) || (!this.status.compared && !this.status.base)) {
        if(!this.showDetail){
          window.$(this.$refs.holder).find('.hidefirst').removeClass('invisDet')
          window.$(this.$refs.holder).find('.hidefirst').addClass('invis')
        } else {
          window.$(this.$refs.holder).find('.hidefirst').removeClass('invis')
          window.$(this.$refs.holder).find('.hidefirst').addClass('invisDet')

        }
      }

      let hideRaw = !this.rawWeekly
      let compare = this.compare
      let period = this.period

      //$(this.$el).find('.showme').addClass('invis')
      //$(this.$el).find('.linechart').addClass('loader')
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

      // Get the repos we need
      let repos = []
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo])
      } // end if (this.$store.repo)
      if (this.comparedTo) {
        repos.push(window.AugurRepos[this.comparedTo])
      }

      let processData = (data) => {
        // Make it so the user can save the data we are using
          this.__download_data = data
          this.__download_file = this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()
          this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
          this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')


          // We usually want to limit dates and convert the key to being vega-lite friendly
          let defaultProcess = (obj, key, field, count, compared) => {
            let d = null
            if (typeof(field) == "string") field = [field]
            if(compared) {
              d = AugurStats.convertComparedKey(obj[key], field)
            }
            else {
              d = AugurStats.convertKey(obj[key], field)
            }

            d = AugurStats.convertDates(d, this.earliest, this.latest)
            return d
          }

          // Normalize the data into [{ date, value },{ date, value }]
          // BuildLines iterates over the fields requested and runs onCreateData on each
          let normalized = []
          let aggregates = []
          let buildLines = (obj, onCreateData, compared) => {
            if (!obj) {
              return
            }
            if (!onCreateData) {
              onCreateData = (obj, key, field, count) => {
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
                  if (Array.isArray(obj[key]) && obj[key].length > 0) {
                    let field = Object.keys(obj[key][0]).splice(1)
                    onCreateData(obj, key, field, count)
                    count++
                  } else {
                    if(!compared)this.status.base = false
                    else this.status.compared = false
                    this.renderError()

                    return
                  }
                }
              } // end hasOwnProperty
            } // end for in
          } // end normalize function


          // Build the lines we need
          let legend = []
          let values = []
          let colors = []
          if (!this.comparedTo) {
            buildLines(data[this.repo], (obj, key, field, count) => {
              // Build basic chart using rolling averages
              let d = defaultProcess(obj, key, field, count, false)
              let rolling = AugurStats.rollingAverage(d, 'value', period)
              normalized.push(AugurStats.standardDeviationLines(rolling, 'valueRolling', ""))
              //if we want stddev area available on raw weekly
              //aggregates.push(AugurStats.standardDeviationLines(d, 'value', ""))
              aggregates.push(d)
              legend.push(field)
              if (!this.disableRollingAverage) { colors.push(window.AUGUR_CHART_STYLE.brightColors[count]) }
              if (!hideRaw || this.disableRollingAverage) { colors.push(this.disableRollingAverage ? window.AUGUR_CHART_STYLE.brightColors[count] : window.AUGUR_CHART_STYLE.dullColors[count]) }
            }, false)
          } else if (compare == 'zscore' || compare == 'baseline' && this.comparedTo) {
            // Build comparison using z-scores
            buildLines(data[this.comparedTo], (obj, key, field, count) => {
              let d = defaultProcess(obj, key, field, count, false)
              let rolling = null
              if (compare == 'zscore') {
                rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', period)
                d = AugurStats.zscores(d, 'value')
              }
              else rolling = AugurStats.rollingAverage(d, 'value', period)
              normalized.push(AugurStats.standardDeviationLines(rolling, 'valueRolling', ""))
              //if we want stddev area available on raw weekly
              //aggregates.push(AugurStats.standardDeviationLines(d, 'value', ""))
              aggregates.push(d)
              legend.push(this.comparedTo + ' ' + field)
              colors.push(window.AUGUR_CHART_STYLE.dullColors[count])
            }, true)
            buildLines(data[this.repo], (obj, key, field, count) => {
              let d = defaultProcess(obj, key, field, count, true)
              //let rolling = AugurStats.rollingAverage(d, 'comparedValue', period)
              let rolling = null
              if (compare == 'zscore') {
                rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'comparedValue'), 'comparedValue', period)
                d = AugurStats.zscores(d, 'comparedValue')
              }
              else rolling = AugurStats.rollingAverage(d, 'comparedValue', period)

              normalized.push(AugurStats.standardDeviationLines(rolling, 'comparedValueRolling', "Compared"))

              //if we want stddev area available on raw weekly
              //aggregates.push(AugurStats.standardDeviationLines(d, 'comparedValue', "Compared"))
              aggregates.push(d)
              legend.push(this.repo + ' ' + field)
              colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }, false)
          } else if (this.comparedTo) {
            // Build chart compared to baseline
            //this.mgConfig.baselines = [{value: 1, label: this.repo}]
            buildLines(data[this.comparedTo], (obj, key, field, count) => {
              normalized.push(AugurStats.makeRelative(obj[key], data[this.repo][key], field, {
                earliest: this.earliest,
                latest: this.latest,
                byDate: true,
                period: period
              }))
              legend.push(this.comparedTo + ' ' + field)
              colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }, true)
          }

          if (normalized.length == 0) {
            // this.renderError()
          } else {
            values = []

            for(var i = 0; i < legend.length; i++){
              normalized[i].forEach(d => {
                d.name = legend[i]
                d.color = colors[i]
                values.push(d);

              })
            }
            if (!hideRaw) {
              for(var i = 0; i < legend.length; i++){
                aggregates[i].forEach(d => {
                  d.name = "raw " + legend[i]
                  d.color = colors[i]
                  values.push(d)
                })
              }
            }
            if(!this.status.base) {
              let temp = JSON.parse(JSON.stringify(values))
              temp = temp.map((datum) => {
                datum.name = "data n/a for " + this.repo
                return datum
              })
              values.unshift.apply(values, temp)
            }
            if(!this.status.compared) {
              let temp = JSON.parse(JSON.stringify(values))
              temp = temp.map((datum) => {
                datum.name = "data n/a for " + this.comparedTo
                return datum
              })
              values.unshift.apply(values, temp)
            }

            this.legendLabels = legend
            this.values = values

            // config.config.legend.offset = -(String(this.legendLabels[0]).length * 6.5) - 20

            //$(this.$el).find('.showme, .hidefirst').removeClass('loader')
            $(this.$el).find('.hidefirst').removeClass('invis')
            $(this.$el).find('.hidefirst').removeClass('invisDet')
            $(this.$el).find('.spinner').removeClass('loader')
            $(this.$el).find('.spacing').addClass('hidden')


            //this.mgConfig.legend_target = this.$refs.legend
            this.renderChart()



          }
      }

      if (this.data) {
        processData(this.data)
      } else {
        window.AugurAPI.batchMapped(repos, endpoints).then((data) => {
          processData(data)
        }, () => {
          this.renderError()
        }) // end batch request
      }

      return config
    }

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
      window.$(this.$refs.holder).find('.hideme').removeClass('invisDet')
      window.$(this.$refs.holder).find('.showme').removeClass('invisDet')
      window.$(this.$refs.holder).find('.deleteme').remove()
      // window.$(this.mgConfig.target).hover((onEnterEvent) => {
      //   window.$(this.$refs.legend).hide()
      // }, (onLeaveEvent) => {
      //   window.$(this.$refs.legend).show()
      // })
      this.$refs.chartholder.innerHTML = ''
      this.$refs.chartholder.appendChild(this.mgConfig.target)
      //this.mgConfig.target.className = 'deleteme'
      //window.MG.data_graphic(this.mgConfig)
    },
    renderError () {
      if (!this.comparedTo || (this.status.base == false && this.status.compared == false)) {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.error').removeClass('hidden')
      } else if (this.status.base == false){
        console.log("base failed")
      } else if (this.status.compared == false) {
        console.log("compared failed")
      }

      // this.$refs.chart.className = 'linechart intro error'
      // window.$(this.$refs.holder).find('.deleteme').remove()
      // this.$refs.chartholder.innerHTML = ''
      // this.$refs.chartholder.appendChild(this.mgConfig.target)
      // //this.mgConfig.target.className = 'deleteme'
      // //this.mgConfig.chart_type = 'missing-data'
      // //window.MG.data_graphic(this.mgConfig)
    }
  }// end methods
}
</script>
