<template>
  <div ref="holder">
    <div class="arealinechart hidefirst invis">
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
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate'],
  data() {
    return {
      legendLabels: [],
      values: []
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
    comparedRepo () {
      return this.$store.state.comparedRepo
    },
    rawWeekly () {
      return this.$store.state.rawWeekly
    },
    showArea() {
      return this.$store.state.showArea
    },
    showTooltip() {
      return this.$store.state.showTooltip
    },
    spec() {

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "title": {
          "text": this.title,
          "offset": 15
        },
        "width": 420,
        "height": 200,
        "config":{
          "axis":{
            "grid": false
          },
          "legend": {

            "offset": 0,
            "titleFontSize": 0,
            "titlePadding": 10

          }
        },
        "layer": [],
        "padding": {
          "top": 20,
          "left": 0,
          "right": 30,
          "bottom": 55
        }
      }

      //cannot have duplicate selection, so keep track if it has already been added
      let selectionAdded = false

      let getStandardLine = function (key) {
        let color = "FF3647"
        if (key != "value"){
          color = "4736FF"
        }
        return {
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal"
              },
              "y": {
                "field": key,
                "type": "quantitative"
              },
              "color": {
                "value": color
              }
            },
            "mark": {
              "type": "line",
              "interpolate": "basis",
              "clip": true
            },

          }
      }

      let getStandardPoint = function (key) {
        let selection = {
              "tooltip": {
                "type": "single",
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
        return {
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {
                  "title": null
                }
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
                "scale": { "range": ['#FF3647', '#4736FF'] }
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

    let getArea = function (key) {
        return {
              "mark": {
                "type": "area",
                "interpolate": "basis",
                "clip": true
              },
              "encoding": {
                "x": {
                  "field": "date",
                  "type": "temporal",
                  "timeUnit": "year"
                },
                "y": {
                  "aggregate": "ci1",
                  "field": key,
                  "type": "quantitative"

                },
                "y2": {
                  "aggregate": "ci0",
                  "field": key,
                  "type": "quantitative"
                },
                "color": {
                  "value": "green"
                },
                "opacity": {"value": 0.2}
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
              "field": "date"
            },
            "color": {
              "field": "name",
              "type": "nominal",
              "scale":{"scheme": "set1"},
            },
            "opacity": {
              "value": 1
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
              "type": "temporal",
              "field": "date"
            },
            "y": {
              "field": key,
              "type": "quantitative"
            },
            "color": {
                "value": "green"
              }
          }
        }
      }

      let getDateText = function (key){
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
              "type": "temporal",
              "field": "date"
            },
            "y": {
              "field": key,
              "type": "quantitative"
            },
            "color": {
                "value": "black"
              }
          }
        }
      }

      //so we can reference the comparedRepo inside of functions ("buildMetric()" specifically)
      let comparedRepo = this.comparedRepo

      let buildMetric = function () {
        //build lines and points for initial repo
        buildLines("value")

        //build lines and points for compared repo
        if(comparedRepo) buildLines("comparedValue")
      }

      let buildLines = function (key) {
        config.layer.push(getStandardLine(key))
        config.layer.push(getStandardPoint(key))
      }

      let buildTooltip = function (key) {
        config.layer.push(getValueText(key))
        config.layer.push(getDateText(key))
      }

      buildMetric()

      //push the area to general spec
      if(this.showArea) {
        config.layer.push(getArea("value"))
        if(this.comparedRepo){
          config.layer.push(getArea("comparedValue"))
        }
      }
      else {
        //if user doesn't want area mark, then set layers to og
        for(var x = 0; x < config.layer.length; x++) {
          if(config.layer[x] == getArea("value")) {
            buildMetric()
          }
        }
      }

      //push the tooltip to general spec
      if(this.showTooltip) {
        buildTooltip("value")
        //push parts of layer that use "comparedValue" key if there is a comparedRepo
        if(this.comparedRepo){
          buildTooltip("comparedValue")
          config.layer.push(rule)
        }
      }
      else {
        //if user doesn't want tooltip mark, then iterate through all marks and pop the tooltip marks
        for(var x = 0; x < config.layer.length; x++) {
          if(config.layer[x] == getValueText("value")) {
            buildMetric()
          }
        }
      }

      //set dates from main control options
      //can either have first priority being to show data points across whole graph, or following user defined dates as first priority
      for(var i = 0; i < config.layer.length; i++){
        config.layer[i].encoding.x["scale"] =
          {
            "domain": [{"year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate()},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
          }
      }

      let hideRaw = !this.rawWeekly

      $(this.$el).find('.showme').addClass('invis')
      $(this.$el).find('.arealinechart').addClass('loader')
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
      if (this.comparedRepo) {
        repos.push(window.AugurRepos[this.comparedRepo])
      }


      // Make a batch request for all the data we need
      window.AugurAPI.batchMapped(repos, endpoints).then((data) => {
        // Make it so the user can save the data we are using
        this.__download_data = data
        this.__download_file = this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()
        this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
        this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')


        // We usually want to limit dates and convert the key to being metrics-graphics friendly
        let defaultProcess = (obj, key, field, count, compared) => {
          // let a = null
          //let b = AugurStats.convertKey(obj[key], field)
          let d = null
          if(compared) {
            d = AugurStats.convertComparedKey(obj[key], field)
            //d = b.concat(a)

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
              let d = defaultProcess(obj, key, field, count, compared)
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
        let max = 0
        if (!this.comparedRepo) {
          buildLines(data[this.repo], (obj, key, field, count) => {
            // Build basic chart using rolling averages
            let d = defaultProcess(obj, key, field, count, false)
            let rolling = AugurStats.rollingAverage(d, 'value', this.period)
            if (!this.disableRollingAverage) {
              normalized.push(rolling)
              aggregates.push(d)
              legend.push(field)
              colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }
            if (!hideRaw || this.disableRollingAverage) {
              normalized.push(rolling)
              aggregates.push(d)
              legend.push(field)
              colors.push(this.disableRollingAverage ? window.AUGUR_CHART_STYLE.brightColors[count] : window.AUGUR_CHART_STYLE.dullColors[count])
            }
          }, false)
        } else if (this.compare === 'each' && this.comparedRepo) {
          // Build comparison using z-scores
          buildLines(data[this.repo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count, false)
            let rolling = AugurStats.rollingAverage(d, 'value', this.period)

            //let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period)
            normalized.push(rolling)
            aggregates.push(d)
            legend.push(this.repo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.dullColors[count])
          }, false)
          buildLines(data[this.comparedRepo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count, true)
            let rolling = AugurStats.rollingAverage(d, 'comparedValue', this.period)
            //let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'comparedValue'), 'comparedValue', this.period)
            normalized.push(rolling)
            aggregates.push(d)
            legend.push(this.comparedRepo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          }, true)
        } else if (this.comparedRepo) {
          // Build chart compared to baseline
          //this.mgConfig.baselines = [{value: 1, label: this.repo}]
          buildLines(data[this.comparedRepo], (obj, key, field, count) => {
            normalized.push(AugurStats.makeRelative(obj[key], data[this.repo][key], field, {
              earliest: this.earliest,
              latest: this.latest,
              byDate: true,
              period: this.period
            }))
            legend.push(this.comparedRepo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          }, true)
        }

        if (normalized.length == 0) {
          this.renderError()
        } else {
          //shared.baseData = data.map((e) => { e.repo = this.repo.toString(); return e })


          if(hideRaw) {
            for(var i = 0; i < legend.length; i++){
              normalized[i].forEach(d => {
                d.name = legend[i]
                d.color = colors[i]
                values.push(d);
              })
            }
          }
          else {
            for(var i = 0; i < legend.length; i++){
              aggregates[i].forEach(d => {
                d.name = "raw " + legend[i]
                d.color = colors[i]
                values.push(d)
              })
            }
          }

          //if(this.comparedRepo){this.legendLabels = legend}
          //else{for (var label in legend){this.legendLabels.push(label[0])}}
          this.legendLabels = legend
          this.values = values

          //function getMaxY(arr){
            // var temp = normalized[0]
            // console.log(temp[0].value)
            // var output = [];
            // for (var i=0; i < temp.length ; ++i)
            //     if(temp[i]) output.push(temp[i][value]);
            // console.log("output" + output);
            // var result = objArray.map(temp => temp.value);
            // console.log(result)
            // console.log(normalized[0])
            //return result[0][0].reduce((max, b) => Math.max(max, b.value), data[0].value);
          //}
          //console.log(getMaxY())
          //console.log("LOOK " + normalized[1][0].value)
          config.config.legend.offset = -(String(this.legendLabels[0]).length * 6.5) - 20
          //console.log("range " + normalized[0][0].value)
          //if(this.values[this.values.length - 1].value > Math.max.apply(Math, normalized) * .6) {
            //console.log("IT IS HAPPENING HAHAH")
            //config.config.legend.titlePadding = 175
          //}

          $(this.$el).find('.showme, .hidefirst').removeClass('invis')
          $(this.$el).find('.arealinechart').removeClass('loader')
          //this.mgConfig.legend_target = this.$refs.legend
          this.renderChart()
        }

      }, () => {
        //this.mgConfig.missing_text = 'Data is missing or unavaliable'
        this.renderError()
      }) // end batch request
      //return '<div class="loader deleteme">' + this.title + '...</div>'
      return config
    },

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
      this.$refs.chart.className = 'linechart intro'
      window.$(this.$refs.holder).find('.deleteme').remove()
      this.$refs.chartholder.innerHTML = ''
      this.$refs.chartholder.appendChild(this.mgConfig.target)
      //this.mgConfig.target.className = 'deleteme'
      //this.mgConfig.chart_type = 'missing-data'
      //window.MG.data_graphic(this.mgConfig)
    }
  }// end methods
}
</script>
