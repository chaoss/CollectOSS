<template>

  <div ref="holder">
    
    <div style="color: black" class="error" :class="{hidden: error}"><br><p style="font-size: 70px; padding-bottom: 3px">🕵️</p> Data is missing or unavailable for metric: <p style="color: blue !important">{{ source }}</p></div>
    <div v-if="!loaded" class="spinner loader"></div>
    <div class="spacing"></div>
    <div v-if="loaded" class="linechart"> <!-- v-bind:class="{ invis: !detail, invisDet: detail }"> -->
      <!-- <div class="row">
        <div class="col col-4" ><input type="radio" name="timeoption" value="month" v-model="timeperiod">Month</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="year" v-model="timeperiod">Year</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="all" v-model="timeperiod">All</div>
      </div> -->
      <div v-if="mount" :id="source"></div>
      <vega-lite v-if="!mount" :spec="spec" :data="values"></vega-lite>
      <p v-if="!mount"> {{ chart }} </p>
<!--       <nav class="tabs">
        <ul>
          <li :class="{ active: (timeperiod == '1825'), hidden: !repo }"><input @change="respec" type="radio" :name="source" value="1825" :id="source + '5year'" v-model="timeperiod"><label :for="source + '5year'">5 Years</label></li>
          <li :class="{ active: (timeperiod == '730'), hidden: !repo }"><input @change="respec" type="radio" :name="source" value="730" :id="source + '2year'" v-model="timeperiod"><label :for="source + '2year'">2 Years</label></li>
          <li :class="{ active: (timeperiod == '365'), hidden: !repo }"><input @change="respec" type="radio" :name="source" value="365" :id="source + 'year'" v-model="timeperiod"><label :for="source + 'year'">Year</label></li>
          <li :class="{ active: (timeperiod == 'all'), hidden: !repo }"><input @change="respec" type="radio" :name="source" value="all" :id="source + 'all'" v-model="timeperiod"><label :for="source + 'all'">All</label></li>
        </ul>
      </nav> -->
    </div>
<!-- 
    <div class="row below-chart" style="top: -28px !important">
      <div class="col col-1"></div>
      <div class="col col-3" style="padding-left: 10px; position: relative; top: -8px !important;">
        <span style="font-size: 12px">Data source: {{ metricSource }}</span>
      </div>
      <div class="col col-2" style="width:154px !important;height: 38px !important; position: relative; top: -12px !important;">
        <cite class="metric"><a style="width:100px !important;height: 38px !important; position: absolute;" v-bind:href="citeUrl" target="_blank"><img style="width:100px;position: relative;" src="https://i.ibb.co/VmxHk3q/Chaoss-Definition-Logo.png" alt="Chaoss-Definition-Logo" border="0"></a></cite>
      </div>
      <div class="col col-4" style="position: relative; top: -8px !important;">
        <a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
    </div>
 -->
  </div>
</template>

<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats'
import { mapActions, mapGetters } from "vuex";

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
      forceRecomputeCounter: 0,
      mount: true,
      loaded: false,
      error: false
    }
  },

  watch: {
    compare: function() {
      this.spec;
    },
    earliest: function () {
      this.spec;
    },
    data: function (newVal, oldVal) {
      if (newVal != []) this.spec;
    },
    compRepos: function() {
      let allFalse = true
      for(var key in this.status)
        if(this.status[key]) allFalse = false
    },
  },
  computed: {
    repo () {
      return this.$store.state.compare.base
    },
    gitRepos () {
      return this.$store.getters.gitRepo
    },
    period () {
      return this.$store.getters.trailingAverage
    },
    earliest () {
      return this.$store.state.compare.startDate
    },
    latest () {
      return this.$store.state.compare.endDate
    },
    compare () {
      return this.$store.state.compare.compare
    },
    comparedRepos () {
      return this.$store.state.compare.comparedRepos
    },
    rawWeekly () {
      return this.$store.state.compare.rawWeekly
    },
    showArea () {
      return this.$store.state.compare.showArea
    },
    showTooltip () {
      return this.$store.getters.showTooltip
    },
    showDetail () {
      return this.$store.getters.showDetail
    },
    spec() {

      // declare constant for vegaEmbed module since we use its cdn in index.html rather than add it to package.json
      const vegaEmbed = window.vegaEmbed;
      // Get the repos we need
      let repos = []
      for (key in Object.keys(this.data)) {
        if (!repos.includes(key))
          repos.push(key)
      }
      
      this.comparedRepos.forEach(function(repo) {
        repos.push(repo.split('/')[1])
      });

      repos.forEach((repo) => {
        this.status[repo] = true
      })
      console.log(repos)

      //COLORS TO PICK FOR EACH REPO
      var colors = ["black", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
      let brush = this.showDetail ? {"filter": {"selection": "brush"}} : {"filter": "datum.date > 0"}
      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": {
          "values": []//this.data
        },
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
                      "labels": this.showDetail,
                      "format": "%ba %Y",
                      "title": " "
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

              },

            ]
          }
        ]
      }

      //cannot have duplicate selection, so keep track if it has already been added
      var selectionAdded = false

      let getStandardLine = (key, color) => {
        // key = key.split('/').join('');
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
              "interpolate": "basis",
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
            "mark": {"type": "line","clip": true}
          }
      }

      let getToolPoint = (key) => {
        let selection = (!selectionAdded ? {
            "tooltip": {"type": "single", "on": "mouseover","nearest": false}
          } : null
        )
        let size = 17
        var timeDiff = Math.abs(this.latest.getTime() - this.earliest.getTime());
        var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
        let field = "valueRolling" + this.repo
        size = diffDays / 150
        if (this.rawWeekly) size = 3
        selectionAdded = true
        return {
          "transform": [
              brush
          ],
          "mark": "rule",
          "selection": {
            "tooltip": {"type": "single", "on": "mouseover","nearest": false, "empty": "none"}
          },
          "encoding": {
            "size": {"value": 20},
            "opacity": {"value": 0.001},
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": null,
            },
            "tooltip": [
              {"field": field, "type": "quantitative"}
            ],
          }
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
              // "y": {
              //   "field": key,
              //   "type": "quantitative",
              //   "axis": {
              //     "title": null
              //   }
              // },
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
              "type": "rule"
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
          "transform": [{"filter": {"selection": "tooltip"}},brush],
          "mark": {"type": "text","align": "left","dx": 5,"dy": -5},
          "encoding": {"text": {"type": "quantitative","field": key},"x": {"field": "date","type": "temporal","axis": {"format": "%b %Y", "title": " "}},"y": {"field": key,"type": "quantitative","axis": {"title": null}},"color": {"value": "green"}}
        }
      }

      let getDateText = function (key) {
        return {
          "transform": [{"filter": {"selection": "tooltip"}},brush],
          "mark": {"type": "text","align": "left","dx": 5,"dy": -15},
          "encoding": {"text": {"type": "temporal","field": "date"},"x": {"field": "date","type": "temporal","axis": {"format": "%b %Y", "title": " "}},"y": {"field": key,"type": "quantitative","axis": {"title": null}},"color": {"value": "black"}}
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
          // config.vconcat[0].layer.push(getValueText(key))
          // config.vconcat[0].layer.push(getDateText(key))
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
      let today = new Date()
      let startyear = (this.timeperiod && this.timeperiod != 'all') ? (() => {
        let d = new Date()
        return new Date(d.setDate(d.getDate()-Number(this.timeperiod))).getFullYear()
      })() : this.earliest.getFullYear()
      let startmonth = (this.timeperiod && this.timeperiod != 'all') ? (() => {
        let d = new Date()
        return new Date(d.setDate(d.getDate()-Number(this.timeperiod))).getMonth()
      })() : this.earliest.getMonth()
      let startdate = (this.timeperiod && this.timeperiod != 'all') ? (() => {
        let d = new Date()
        return new Date(d.setDate(d.getDate()-Number(this.timeperiod))).getDate()
      })() : this.earliest.getDate()
      for(var i = 0; i < config.vconcat[0].layer.length; i++){
        config.vconcat[0].layer[i].encoding.x["scale"] =
          {
            "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
          }
      }
      if(this.showDetail) {
        config.vconcat[1].encoding.x["scale"] = {
            "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
          }
      } else {
      //OLD ELSE KEEP for now
        // for(var i = 0; i < config.vconcat[0].layer.length; i++){
        //   config.vconcat[0].layer[i].encoding.x["scale"] =
        //     {
        //       "domain": [{"year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate()},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
        //     }
        // }
      }

      // if base repo fails and it is the only repo, or if base repo AND only compared repo fails
      // makes blank chart invisible to user
      if ((!this.status.base && !this.comparedTo) || (!this.status.compared && !this.status.base)) {
        if(!this.showDetail){
          // window.$(this.$refs.holder).find('.hidefirst').removeClass('invisDet')
          // window.$(this.$refs.holder).find('.hidefirst').addClass('invis')
        } else {
          // window.$(this.$refs.holder).find('.hidefirst').removeClass('invis')
          // window.$(this.$refs.holder).find('.hidefirst').addClass('invisDet')
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

      let processData = (data) => {
        // Make it so the user can save the data we are using
          this.__download_data = data
          this.__download_file = this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()
          // this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
          // this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')


          // We usually want to limit dates and convert the key to being vega-lite friendly
          let defaultProcess = (obj, key, field, count) => {
            let d = null
            if (typeof(field) == "string") {
              field = [field]
            }

            d = AugurStats.convertKey(obj[key], field)
            d = AugurStats.convertDates(d, this.earliest, this.latest, 'date')
            return d
          }

          // Normalize the data into [{ date, value },{ date, value }]
          // BuildLines iterates over the fields requested and runs onCreateData on each
          let normalized = []
          let aggregates = []
          let buildLines = (obj, onCreateData, repo) => {
            console.log(obj, onCreateData, repo)
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
              console.log(key)
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
          let legend = [] //repo + field strings for vega legend
          let values = []
          let colors = []
          let baselineVals = null
          let baseDate = null
          repos.forEach((repo) => {
            console.log(data,repo)
            // let relevant = this.data ? data
              buildLines(data[repo], (obj, key, field, count) => {
                // Build basic chart using rolling averages
                let d = defaultProcess(obj, key, field, count)
                console.log(d)
                let rolling = null
                if (repo == this.repo && d[0]) baseDate = d[0].date
                else d = AugurStats.alignDates(d, baseDate, this.period)
                if (this.compare == 'zscore') { // && this.comparedRepos.length > 0
                  rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period, repo)
                } //else if (this.rawWeekly || this.disableRollingAverage) rolling = AugurStats.convertKey(d, 'value', 'value' + repo)
                else if (this.compare == 'baseline') { //&& this.comparedRepos.length > 0
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
                // colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
              }, repo)

          });

          if (normalized.length == 0) {
            // this.renderError()
          } else {
            values = []
            // let today = new Date()
            for(var i = 0; i < legend.length; i++){
              normalized[i].forEach(d => {

                if (d.date < (new Date(startyear,startmonth,startdate))){
                  d = {}
                } else {
                  d.name = legend[i]
                  d.color = colors[i]
                  values.push(d);
                }
              })
              if (this.rawWeekly) {
                aggregates[i].forEach(d => {
                  if (d.date < (new Date(startyear,startmonth,startdate))){
                    d = {}
                  } else {
                    d.name = legend[i]
                    d.color = colors[i]
                    values.push(d);
                  }
                })
              }
            }
            repos.forEach((repo) => {
              if(!this.status[repo]) {
                let temp = JSON.parse(JSON.stringify(values))
                temp = temp.map((datum) => {
                  datum.name = repo + ": data n/a"

                  return datum
                })
                values.push.apply(values, temp)
              }
            })

            this.legendLabels = legend
            config.data = {"values": values}
            console.log(config.data)
            this.values = values

            this.renderChart()
            this.loaded = true
          }
      }
      if (this.data) {
        processData(this.data)
        repos = Object.keys(this.data)
      } else {
        console.log("did not detect data")
        this.$store.state.common.AugurAPI.batchMapped(repos, endpoints).then((data) => {
          processData(data)
        }, () => {
          this.renderError()
        }) // end batch request
      }
      if (this.mount)
        this.reloadImage(config)
      
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
      let allFalse = true
      for(var key in this.status)
        if(this.status[key]) allFalse = false
    },
    renderError () {
      console.log("ERROR ERROR")
      this.error = true
    },
    thisShouldTriggerRecompute() {
      this.forceRecomputeCounter++;
    },
    respec(){this.spec;},
    reloadImage (config) {
      console.log(config.data, this.source)
      if (config.data.length == 0){
        this.spec;
        this.renderError()
        return
      }
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -110}, mode: 'vega-lite'})
    }
  },// end methods
  mounted() {
    this.spec;
  },
  created () {
    var query_string = "chart_mapping=" + this.source
    this.$store.state.common.AugurAPI.getMetricsStatus(query_string).then((data) => {
      this.metricSource = data[0].data_source
    })
  }
}
</script>
