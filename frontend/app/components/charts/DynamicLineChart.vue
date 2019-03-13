<template>
  <div ref="holder">
    <div class="spacing"></div>
    <div class="error hidden"><br>Data is missing or unavailable for metric: <p style="color: black !important">{{ title }}</p></div>
    <div class="spinner loader"></div>
    <div class="hidefirst linechart" v-bind:class="{ invis: !detail, invisDet: detail }">
      <!-- <div class="row">
        <div class="col col-4" ><input type="radio" name="timeoption" value="month" v-model="timeperiod">Month</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="year" v-model="timeperiod">Year</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="all" v-model="timeperiod">All</div>        
      </div> -->
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
    </div>

    <div class="row below-chart">
      <div class="col col-1"></div>
      <div class="col col-3" style="padding-left: 10px; position: relative; top: -8px !important;">
        <span style="font-size: 12px">Data source: {{ metricSource }}</span>
      </div>
      <div class="col col-2" style="width:154px !important;height: 38px !important; position: relative; top: -12px !important;">
        <!-- <cite class="metric">Metric: <a v-bind:href="citeUrl" target="_blank">{{ citeText }}</a></cite> -->
        <cite class="metric"><a style="width:100px !important;height: 38px !important; position: absolute;" v-bind:href="citeUrl" target="_blank"><img style="width:100px;position: relative;" src="https://i.ibb.co/VmxHk3q/Chaoss-Definition-Logo.png" alt="Chaoss-Definition-Logo" border="0"></a></cite>
      </div>
      <div class="col col-4" style="position: relative; top: -8px !important;"><button class="button download graph-download" v-on:click="downloadSVG">&#11015; SVG</button><button class="button graph-download download" v-on:click="downloadPNG">&#11015; PNG</button><a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
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
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'domain', 'data'],
  data() {
    return {
      legendLabels: [],
      values: [],
      status: {},
      detail: this.$store.state.showDetail,
      compRepos: this.$store.state.comparedRepos,
      metricSource: null,
      timeperiod: 'all',
      forceRecomputeCounter: 0
    }
  },
  watch: {
    compRepos: function() {
      let allFalse = true
      for(var key in this.status)
        if(this.status[key]) allFalse = false
      if(allFalse) {
        $(this.$el).find('.spinner').addClass('loader')
        $(this.$el).find('.error').addClass('hidden')
      }
      $(this.$el).find('.hidefirst').addClass('invis')
      $(this.$el).find('.hidefirst').addClass('invisDet')
      $(this.$el).find('.spinner').addClass('loader')
      $(this.$el).find('.spacing').removeClass('hidden')
    }
  },
  beforeUpdate() {
    this.$store.watch(
      // When the returned result changes...
      function (state) {
        console.log("WORKED")
        this.thisShouldTriggerRecompute()
        return 
      },
      // // Run this callback
      // callback
    )
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepos () {
      return this.$store.state.gitRepo
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
      this.forceRecomputeCounter;
      // Get the repos we need
      let repos = []
      if (this.repo) {
        if (window.AugurRepos[this.repo])
          repos.push(window.AugurRepos[this.repo])
        else if (this.domain){
          let temp = window.AugurAPI.Repo({"gitURL": this.gitRepo})
          if (window.AugurRepos[temp])
            temp = window.AugurRepos[temp]
          else
            window.AugurRepos[temp] = temp
          repos.push(temp)
        }
        // repos.push(this.repo)
      } // end if (this.$store.repo)
      this.comparedRepos.forEach(function(repo) {
        repos.push(window.AugurRepos[repo])
      });

      repos.forEach((repo) => {
        this.status[repo] = true
      })

      //COLORS TO PICK FOR EACH REPO
      var colors = ["black", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
      let brush = {"filter": {"selection": "brush"}}
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
            "layer": [
              {
                "transform": [
                  brush
                ],
                "mark": "rule",
                "encoding":{
                  "x": {
                    "field": "date",
                    "type": "temporal",
                    "axis": {
                      "labels": !this.showDetail
                    }
                  },
                  "color": {
                    "field": "name",
                    "type": "nominal",
                    "scale": { "range": colors},
                    "sort": false
                  },
                  "opacity":{
                    "value": 0
                  }
                }

              }
            ]
          }
        ]
      }

      
      if(!this.showDetail) brush = {"filter": "datum.date > 0"}

      //cannot have duplicate selection, so keep track if it has already been added
      var selectionAdded = false

      let getStandardLine = (key, color) => {
        let raw = (key.substring(key.length - 7) == "Rolling" ? false : true)
        return {
            "transform": [
              brush
          ],
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {
                      "labels": !this.showDetail,
                    "format": "%b %Y", "title": " "}
              },
              "y": {
                "field": key,
                "type": "quantitative",
                "axis": {
                  "title": null
                }
              },
              "color": {
                    "value": color
                  },
            },
            "mark": {
              "type": "line",
              //"interpolate": "basis",
              "clip": true
            }
          }
      }

      let getRawLine = (key, color) => {
        let raw = (key.substring(key.length - 7) == "Rolling" ? false : true)
        return {
            "transform": [
              brush
          ],
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {
                      "labels": !this.showDetail,
                    "format": "%b %Y", "title": " "}
              },
              "y": {
                "field": key,
                "type": "quantitative",
                "axis": {
                  "title": null
                }
              },
              "color": {
                    "value": color
                  },
                  "opacity": {"value": .3}
            },
            "mark": {
              "type": "line",
              //"interpolate": "basis",
              "clip": true
            }
          }
      }

      let getToolPoint = (key) => { 
        let selection = (!selectionAdded ? {
              "tooltip": {
                "type": "single",
                "on": "mouseover",
                "encodings": [
                  "x"
                ],
                "empty": "none"
              }
            } : null)
        let size = 17
        var timeDiff = Math.abs(this.latest.getTime() - this.earliest.getTime());
        var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
        size = diffDays / 150
        if (this.rawWeekly) size = 3
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
              "color": {
                    // "field": "name",
                    // "type": "nominal",
                    // "scale": { "range": colors}
                    "value": "black"
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

      let getStandardPoint = (key, color) => {
        let selection = (!selectionAdded ? {
              "tooltip": {
                "type": "single",
                "on": "mouseover",
                "encodings": [
                  "x"
                ],
                "empty": "none"
              }
            } : null)
        selectionAdded = true
        let raw = (key.substring(key.length - 7) == "Rolling" ? false : true)
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
                // "value": color
                "value": "black"
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
            },
            brush
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
            },
            brush
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
            },
            brush
          ],
          "mark": {
            "type": "text",
            "align": "left",
            "dx": 5,
            "dy": -15
            // "baseline": "top"
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
        let color = (this.comparedTo && this.status.compared ? '#FF3647' : 'black')
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

      //DONE WITH SPEC PORTION

      //push the area to general spec
      //can change repo to whatever
      if(this.showArea && repos.length < 3) {
        repos.forEach((repo) => {
          config.vconcat[0].layer.push(getArea(repo))
        })
      } else {
        repos.forEach((repo) => {
          for(var x = 0; x < config.vconcat[0].layer.length; x++) {
            if(config.vconcat[0].layer[x] == getArea(repo)) {
              config.vconcat[0].layer[x] = {}
              buildMetric()
            }
          }
        })
      }

      let buildMetric = () => {
        var color = 0;
        repos.forEach((repo) => {
          buildLines("valueRolling" + repo, colors[color])

          if(this.rawWeekly) 
            config.vconcat[0].layer.push(getRawLine("value" + repo, colors[color]))
          // if user doesn't want detail, then set vconcat to og
          if(this.showDetail) 
            config.vconcat[1] = getDetail("valueRolling" + this.repo)
          else if (config.vconcat[1]) 
            config.vconcat.pop()
          color++
        });
      }

      let buildLines = function (key, color) {
        config.vconcat[0].layer.push(getStandardLine(key, color))
      }

      let buildTooltip = function (key) {
        config.vconcat[0].layer.push(getToolPoint(key))
        if (repos.length < 3) {
          var col = -1;
          repos.forEach((repo) => {
            config.vconcat[0].layer.push(getStandardPoint(key, colors[col]))
            col++
          });
          config.vconcat[0].layer.push(getValueText(key))
          config.vconcat[0].layer.push(getDateText(key))
          //push parts of layer that use "valueCompared" key if there is a comparedRepo
          if(repos.length > 1){
            config.vconcat[0].layer.push(rule)
          }
        }
      }

      //push the tooltip to general spec
      //can change this.repo to whatever repo user wants tooltip on
      if(this.showTooltip) {
        //let temp = [this.repo]
        repos.forEach((repo) => {
          let key = (this.rawWeekly ? "value" + repo : "valueRolling" + repo)
          buildTooltip(key)
        })
      } else {
        //if user doesn't want tooltip mark, then iterate through all marks and pop the tooltip marks
        // for(var x = 0; x < config.vconcat[0].layer.length; x++) {
          // if(config.vconcat[0].layer[x] == getValueText("valueRolling" + this.repo)) {
          //   config.vconcat[0].layer[x] = {}
            // buildMetric()
          // }
        // }
      }

      buildMetric()

      //set dates from main control options
      if(this.showDetail) {
        let today = new Date()
        let startyear = (this.timeperiod && this.timeperiod != 'all') ? (() => {
          let d = new Date()
          switch (this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate()-30))
              return d.getFullYear();
            case "year":
              d = new Date(d.setDate(d.getDate()-365))
              return d.getFullYear();
          }
        })() : this.earliest.getFullYear()
        let startmonth = (this.timeperiod && this.timeperiod != 'all') ? (() => {
          let d = new Date()
          switch (this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate()-30))
              return d.getMonth();
            case "year":
              d = new Date(d.setDate(d.getDate()-365))
              return d.getMonth();
          }
        })() : this.earliest.getMonth()
        let startdate = (this.timeperiod && this.timeperiod != 'all') ? (() => {
          let d = new Date()
          switch (this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate()-30))
              return d.getDate();
            case "year":
              d = new Date(d.setDate(d.getDate()-365))
              return d.getDate();
          }
        })() : this.earliest.getDate()
        // for(var i = 0; i < config.vconcat[0].layer.length; i++){
        //   config.vconcat[0].layer[i].encoding.x["scale"] =
        //     {
        //       "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
        //     }
        // }
        config.vconcat[1].encoding.x["scale"] = {
            "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
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

      let compare = this.compare
      let processData = (data) => {
        // Make it so the user can save the data we are using
          this.__download_data = data
          this.__download_file = this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()
          this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
          this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')


          // We usually want to limit dates and convert the key to being vega-lite friendly
          let defaultProcess = (obj, key, field, count) => {
            let d = null
            if (typeof(field) == "string") field = [field]

            d = AugurStats.convertKey(obj[key], field)


            d = AugurStats.convertDates(d, this.earliest, this.latest, 'date')

            return d
          }

          // Normalize the data into [{ date, value },{ date, value }]
          // BuildLines iterates over the fields requested and runs onCreateData on each
          let normalized = []
          let aggregates = []
          let buildLines = (obj, onCreateData, repo) => {
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
                    this.status[repo] = false
                    this.renderError()

                    //return
                  }
                }
              } // end hasOwnProperty
            } // end for in
          } // end normalize function

          // Build the lines we need
          let legend = []
          let values = []
          let colors = []
          let baselineVals = null
          let baseDate = null
          repos.forEach((repo) => {
              buildLines(data[repo], (obj, key, field, count) => {
                // Build basic chart using rolling averages
                let d = defaultProcess(obj, key, field, count)
                
                let rolling = null
                if (repo == this.repo) baseDate = d[0].date
                else d = AugurStats.alignDates(d, baseDate, this.period)
                if (this.compare == 'zscore') {
                  rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period, repo)
                } //else if (this.rawWeekly || this.disableRollingAverage) rolling = AugurStats.convertKey(d, 'value', 'value' + repo)
                else if (this.compare == 'baseline') {
                  if(repo.githubURL == this.repo){
                    baselineVals = AugurStats.rollingAverage(d, 'value', this.period, repo)
                  }
                  rolling = AugurStats.rollingAverage(d, 'value', this.period, repo)
                  if(baselineVals){

                    for (var i = 0; i < baselineVals.length; i++){
                    if (rolling[i] && baselineVals[i])
                      rolling[i].valueRolling -= baselineVals[i].valueRolling                   
                    }
                  }
                } else {
                  rolling = AugurStats.rollingAverage(d, 'value', this.period, repo)
                }

                normalized.push(AugurStats.standardDeviationLines(rolling, 'valueRolling', repo))
                aggregates.push(AugurStats.convertKey(d, 'value', 'value' + repo))
                legend.push(repo + " " + field)
                colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
              }, repo)

          });

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
              if (this.rawWeekly) {
                aggregates[i].forEach(d => {
                  // d.name = "raw " + legend[i]
                  d.name = legend[i]
                  d.color = colors[i]
                  values.push(d)
                })
              }
            }
            repos.forEach((repo) => {
              if(!this.status[repo]) {
                let temp = JSON.parse(JSON.stringify(values))
                temp = temp.map((datum) => {
                  datum.name = repo + ": data n/a"
                  // datum.valueRolling = datum.valueComparedRolling

                  return datum
                })
                values.push.apply(values, temp)
              }
            })  

            this.legendLabels = legend
            this.values = values

            let allFalse = true
            for(var key in this.status)
              if(this.status[key]) allFalse = false
            if(!allFalse) $(this.$el).find('.error').addClass('hidden')

            // config.config.legend.offset = -(String(this.legendLabels[0]).length * 6.5) - 20

            $(this.$el).find('.hidefirst').removeClass('invis')
            $(this.$el).find('.hidefirst').removeClass('invisDet')
            $(this.$el).find('.spinner').removeClass('loader')
            $(this.$el).find('.spacing').addClass('hidden')
            $(this.$el).find('.hidefirst').removeClass('invisDet')


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
          //this.renderError()
        }) // end batch request
      }

      return config
    }

  }, // end computed
  methods: {
    thisShouldTriggerRecompute() {
      this.forceRecomputeCounter++;
    },
    downloadSVG (e) {
      var svgsaver = new window.SvgSaver()
      var svg = window.$(this.$refs.holder).find('svg')[0]
      svgsaver.asSvg(svg, this.__download_file + '.svg')
    },
    downloadPNG (e) {
      var svgsaver = new window.SvgSaver()
      var svg = window.$(this.$refs.holder).find('svg')[0]
      svgsaver.asPng(svg, this.__download_file + '.png')
    },
    renderChart () {
      this.$refs.chart.className = 'linechart intro'
      window.$(this.$refs.holder).find('.hideme').removeClass('invis')
      window.$(this.$refs.holder).find('.showme').removeClass('invis')
      window.$(this.$refs.holder).find('.hideme').removeClass('invisDet')
      window.$(this.$refs.holder).find('.showme').removeClass('invisDet')
      window.$(this.$refs.holder).find('.deleteme').remove()
      this.$refs.chartholder.innerHTML = ''
      this.$refs.chartholder.appendChild(this.mgConfig.target)
    },
    renderError () {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.error').removeClass('hidden')
    }
  },// end methods
  created () {
      var query_string = "chart_mapping=" + this.source
      window.AugurAPI.getMetricsStatus(query_string).then((data) => {
        this.metricSource = data[0].data_source
      })
  }
}
</script>
