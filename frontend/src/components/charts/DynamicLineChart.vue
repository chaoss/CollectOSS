<template>

  <d-card-body v-if="!error" :title="title">
  <!-- <div style="color: black" class="error" :class="{hidden: !error}"><br><p style="font-size: 70px; padding-bottom: 3px">🕵️</p> Data is missing or unavailable for metric: <p style="color: blue !important"> {{ source }}</p></div> -->
  <d-card-body>
    <div v-if="mount" :id="source"></div>
    <div v-if="!loaded">
      <spinner></spinner>
    </div>
    <div v-if="loaded" class="linechart"> 
      <!-- <div class="row">
        <div class="col col-4" ><input type="radio" name="timeoption" value="month" v-model="timeperiod">Month</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="year" v-model="timeperiod">Year</div>
        <div class="col col-4" ><input type="radio" name="timeoption" value="all" v-model="timeperiod">All</div>
      </div> -->
      
      <vega-lite v-if="!mount" :spec="spec(values)" :data="values"></vega-lite>
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
    <div class="row below-chart DynamicLineChartDiv13">
      <div class="col col-1"></div>
      <div class="col col-3 DynamicLineChartDiv15">
        <span class="DynamicLineChartSpan">Data source: {{ metricSource }}</span>
      </div>
      <div class="col col-2 DynamicLinechartDiv17">
        <cite class="metric"><a class="DynamicLineChartDiv18-1" v-bind:href="citeUrl" target="_blank"><img class="DynamicLineChart18-2" src="https://i.ibb.co/VmxHk3q/Chaoss-Definition-Logo.png" alt="Chaoss-Definition-Logo" border="0"></a></cite>
      </div>
      <div class="col col-4 DynamicLineChart20">
        <a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
    </div>
 -->
  </d-card-body>
</template>

<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats'
import { mapActions, mapGetters } from "vuex";
import vegaEmbed from 'vega-embed'
import Spinner from '../../components/Spinner.vue'

export default {

  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'domain', 'data', 'endpoints'],
  components: {
    Spinner
  },
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
      error: false,
      x:0,
      y:0
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
    gitRepos () {
      return this.$store.getters.gitRepo
    },
    period () {
      return this.$store.state.common.trailingAverage
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
      return this.$store.state.common.showTooltip
    },
    showDetail () {
      return this.$store.state.common.showDetail
    },
    ...mapGetters('common',[
      'repoRelations',
      'apiRepos'
    ]),
    ...mapGetters('compare',[
      'base',
      'comparedAPIRepos'
    ]),
    

  }, // end computed
  methods: {
    ...mapActions('common',[
      'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                  // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
    ]),
    ...mapActions('compare',[
      'setComparedRepos'
    ]),
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
      // console.log("DLC","ERROR ERROR")
      this.error = true
      this.loaded = true
    },
    thisShouldTriggerRecompute() {
      this.forceRecomputeCounter++;
    },
    respec(){this.spec;},
    reloadImage (config) {
      // console.log("DLC",config, this.source)
      if (config.data.values.length == 0){
        // console.log("DLC","yo")
        // this.spec;
        this.renderError()
        return
      }
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -110}, mode: 'vega-lite'})
    },
    convertKey(ary) {
      ary.forEach((el) => {
        
        let keys = Object.keys(el)
        let field = null
        keys.forEach((key) => {
          if (el[key] != null && key != 'date' && key != 'repo_name' && key != 'repo_id' && key != 'field' && key != 'value'){
            field = key
          }
        })
        el['value'] = el[field]
        el['field'] = field 
      })
      return ary
    },
    spec(data) {
      // console.log("DLC","DATAAAA", data, this.$store.state)

      let repos = this.repos

      // declare constant for vegaEmbed module since we use its cdn in index.html rather than add it to package.json
      // const vegaEmbed = window.vegaEmbed

      //COLORS TO PICK FOR EACH REPO
      var colors = ["black", "#FF3647","#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
      let brush = this.showDetail ? {"filter": {"selection": "brush"}} : {"filter": "datum.date > 0"}
      let config = {
        // "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": {
          "values": []//this.data
        },
        // "padding": {'left': 0, 'top': 0, 'right': this.x / 2, 'bottom': 0},
        "config":{
              "axis":{
                "grid": true
              },
              "legend": {
                "offset": -(this.x / 3.15),
                "titleFontSize": 0,
                "titlePadding": 10
              },
            },
        // "resolve": {"scale": {"x": "independent"}},
        "vconcat": [
          {
            "width": this.x / 3,
            "height": this.y / 3,
            
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
                      "labels": true,
                      "format": "%b %Y",
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

      let getStandardLine = (key, color, extension) => {
        // key = key.split('/').join('');
        let raw = (key.substring(key.length - 7) == "Rolling" ? false : true)
        return {
            // "transform": [
            //   brush
            // ],
            "encoding": {
              "x": {
                "field": "date" + extension,
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
                    "field": "date" + extension,
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

      let buildLines = function (key, color, extension) {
        config.vconcat[0].layer.push(getStandardLine(key, color, extension))

      }


      let buildMetric = () => {
        var color = 0;
        repos.forEach((repo) => {
          buildLines("valueRolling" + repo.replace(/\//g,'').replace(/\./g,''), colors[color], repo.replace(/\//g,'').replace(/\./g,''))

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

      //push the area to general spec
      //can change repo to whatever
      if(this.showArea && repos.length < 3) {
        repos.forEach((repo) => {
          config.vconcat[0].layer.push(getArea(repo.replace(/\//g,'').replace(/\./g,'')))
        })
      } else {
        repos.forEach((repo) => {
          for(var x = 0; x < config.vconcat[0].layer.length; x++) {
            if(config.vconcat[0].layer[x] == getArea(repo.replace(/\//g,'').replace(/\./g,''))) {
              config.vconcat[0].layer[x] = {}
              buildMetric()
            }
          }
        })
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
        // repos.forEach((repo) => {
        //   let key = (this.rawWeekly ? "value" + repo : "valueRolling" + repo)
        //   buildTooltip(key)
        // })
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


      buildLines("valueRolling" + repos[0].replace(/\//g,'').replace(/\./g,''), colors[0])
      if (repos[1])
        buildLines("valueRolling" + repos[1].replace(/\//g,'').replace(/\./g,''), colors[1])

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
        // config.vconcat[0].layer[i].encoding.x["scale"] =
        //   {
        //     "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
        //   }
      }
      if(this.showDetail) {
        // config.vconcat[1].encoding.x["scale"] = {
        //     "domain": [{"year": startyear, "month": startmonth, "date": startdate},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
        //   }
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

          // this.repos.forEach((repo) => {
          //   Object.keys(data[repo]).forEach((metric) => {
          //     data = this.convertKey(data[repo][metric])
          //   })
          // })
          
        // Make it so the user can save the data we are using
          this.__download_data = data
          this.__download_file = this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase()
          // this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(this.__download_data))
          // this.$refs.downloadJSON.setAttribute('download', this.__download_file + '.json')


          // We usually want to limit dates and convert the key to being vega-lite friendly
          let defaultProcess = (obj, key, field, count) => {
            // console.log("DLC begin default process: ", obj, key, field, count)
            let d = obj[key]
            if (typeof(field) == "string") {
              field = [field]
            }
            console.log("DLC","default process prior to convertKey:",obj, key, field)
            // let goodField = null
            // for (let f in field) {
            //   if (f != 'date' && f != 'value' && f != 'field')
            //     goodField = f
            // }
            // d = AugurStats.convertKey(obj[key], field)
            // console.log("DLC","default process prior to convertDates:",d, this.earliest, this.latest, 'date')
            d = AugurStats.convertDates(d, this.earliest, this.latest, 'date')
            return d
          }

          // Normalize the data into [{ date, value },{ date, value }]
          // BuildLines iterates over the fields requested and runs onCreateData on each
          let normalized = []
          let aggregates = []
          let buildLines = (obj, onCreateData, repo) => {
            // console.log("DLC start of buildLines",obj, repo)
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
              // console.log("DLC key:",key)
              if (obj.hasOwnProperty(key)) {
                if (fields[key]) {
                  fields[key].forEach((field) => {
                    onCreateData(obj, key, field, count)
                    count++
                  })
                } else {
                  // console.log("DLC","hehrere",Array.isArray(obj[key]),obj, key)
                  if (Array.isArray(obj[key]) && obj[key].length > 0) {
                    let field = Object.keys(obj[key][0]).splice(1)
                    onCreateData(obj, key, field, count)
                    count++
                  } else {
                    this.status[repo] = false
                    let noRepoWithData = true
                    Object.keys(this.status).forEach((repo) => {
                      if (this.status[repo]) noRepoWithData = false
                    })
                    if (noRepoWithData){
                      // console.log("DLC","logging no data for any repo error")
                      this.renderError()
                    }
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
          let x = 0
          this.repos.forEach((repo) => {
            buildLines(data[repo], (obj, key, field, count) => {
              // Build basic chart using rolling averages
              let d = defaultProcess(obj, key, field, count)
              // console.log("DLC",d)
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
                d = this.convertKey(d)
                // console.log("DLC prerolling",d, this.period, repo)
                rolling = AugurStats.rollingAverage(d, 'value', this.period, repo)
                // console.log("DLC rolling:",rolling)
                while (rolling[0].valueRolling == 0)
                  rolling.shift()
                rolling.forEach((tuple) => {
                  tuple.date.setDate(tuple.date.getDate() + x);
                })
                // console.log("DLC",rolling)
              }

              normalized.push(AugurStats.standardDeviationLines(rolling, 'valueRolling', repo))
              aggregates.push(AugurStats.convertKey(d, 'value', 'value' + repo))
              legend.push(repo + " " + key)
              // colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }, repo)
            x++
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
            this.repos.forEach((repo) => {
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
            this.values = values

            if (values.length < 2)
              this.renderError()
            else {
              this.renderChart()
              this.loaded = true
            }

            
          }
      }

      processData(data)
      
      if (this.mount)
        this.reloadImage(config)
      
      return config

    }
  },// end methods
  mounted() {
    var win = window,
    doc = document,
    docElem = doc.documentElement,
    body = doc.getElementsByTagName('body')[0],
    x = win.innerWidth || docElem.clientWidth || body.clientWidth,
    y = win.innerHeight|| docElem.clientHeight|| body.clientHeight;
    this.x = x
    this.y = y

    function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Get the repos we need
    let repos = []
    let apiRepos = []
    let promises = []

    if (this.base) {
      apiRepos.push(this.base)
      // console.log("DLC base",this.base)
      let ref = this.base.url || this.base.repo_name
      repos = [ref]
    }
    else {
      //allow to retrieve from route... eventually

      // console.log(this.$router.currentRoute.params)
      // let ref = this.repoRelations[this.$router.currentRoute.params.group][this.$router.currentRoute.params.repo].url || this.repoRelations[this.$router.currentRoute.params.group][this.$router.currentRoute.params.repo].repo_name
      // repos.push(ref)
    }
    
    // if (this.comparedAPIRepos){
    //   this.comparedAPIRepos.forEach((repo) => {
    //     apiRepos.push(repo)
    //     let ref = repo.url || repo.repo_name
    //     repos.push(ref)
    //   });
    // } else {
    let compares = null
    if ('compares' in this.$router.currentRoute.params) {
      
      compares = this.$router.currentRoute.params.compares
      
      if (compares in this.apiRepos) {

        // console.log("DLC Api repos already loaded",this.apiRepos, compares)
        apiRepos.push(this.apiRepos[compares])
        let ref = this.repoRelations[compares.split('/')[0]][compares.split('/')[1]].url || this.repoRelations[compares.split('/')[0]][compares.split('/')[1]].repo_name
        repos.push(ref)

      } else {

        // console.log("DLC Api repos not loaded, getting repo from route then setting comp repos: ", compares)
        let ids = !this.$router.currentRoute.params.comparedRepoIds ? [] : this.$router.currentRoute.params.comparedRepoIds.split(',')
        promises.append(this.setComparedRepos({ 'names': [compares], 'ids': ids }))

      }
      //got api repos
      
    }
    //got repo names

    // console.log("DLC starting promises...")
    Promise.all(promises).then(() => {
      if (compares) {
        apiRepos.push(this.apiRepos[compares])
        let ref = this.repoRelations[compares.split('/')[0]][compares.split('/')[1]].url || this.repoRelations[compares.split('/')[0]][compares.split('/')[1]].repo_name
        repos.push(ref)
      }
      
    
      repos.forEach((repo) => {
        this.status[repo] = true
      })
      this.repos = repos

      if (this.data) {
        let dataFilled = true
        Object.keys(this.data).forEach((key) => {
          // console.log("DLC",key, this.data[key])
          if (this.data[key].length < 1) dataFilled = false
        })
        if (dataFilled){
          this.spec(this.data)
          repos = Object.keys(this.data)
        }
        
      } else {
        // console.log("DLC","did not detect data")
        this.endpoint({ repos:apiRepos, endpoints:[this.source] }).then((data) => {
          // console.log("DLC","YAA",data)
          // console.log("DLC",Object.keys(data).length)
          if (Object.keys(data).length > 0)
            this.spec(data)
          // processData(data)
        }).catch((error) => {
          // console.log("DLC",error)
          this.renderError()
        }) // end batch request
      }

    })
      
  },
  created () {
    var query_string = "chart_mapping=" + this.source
    this.$store.state.common.AugurAPI.getMetricsStatus(query_string).then((data) => {
      this.metricSource = data[0].data_source
    })
  }
}
</script>
