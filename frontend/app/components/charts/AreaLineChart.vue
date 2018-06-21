<template>
  <div ref="holder">
    <div class="arealinechart hidefirst invis">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
    </div>

    <div class="row below-chart">
      <div class="col col-4"><cite class="metric">Metric: <a v-bind:href="citeUrl" target="_blank">{{ citeText }}</a></cite></div>
      <div class="col col-4"><button class="button download graph-download" v-on:click="downloadSVG">&#11015; SVG</button><button class="button graph-download download" v-on:click="downloadPNG">&#11015; PNG</button><a class="button graph-download download" ref="downloadJSON" role="button">&#11015; JSON</a></div>
      <!-- <div class="form-item form-checkboxes">
        <label class="checkbox"><input name="hidearea" value="each" type="checkbox" v-model="ar">Individual area<sup class="warn"></sup></label><br>
      </div> -->
    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'



let numCharts = 0
let numRenders = []
let count = 0


// let mutations = {
//   UPDATE_SPEC(config, values){
//     let { key , value } = data

//     console.log("Updating form: ", key, value)
//     if(state.config.layer[key]){
//       state.form[key] = value
//     }
//   }
// }

// let store = new Vuex.Store({
//   config,
//   mutations
// })

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate'],
  // data: {
  //   hideArea: true
  // },
  data() {

    return {
      values: []
    }
  },
  watch: {
    // hideArea: function () {
    //   //count = 0
    //   numRenders[count]++
    //   if(count < 1) {
    //     if(hideArea) config.layer.push(area)
    //     else config.layer.pop(area)
    //   }
    //   // alert(count)
    //   // alert("changing")
    //   // this.$store.commit('UPDATE_SPEC',{
    //   //    area,
    //   //    areaS
    //   //  })
    // },

    // showTooltip: function () {
    //   count = 0
    //   config.layer[0] = tooltip
    //   alert("tooltip change")
    // },
    // rawWeekly: function () {

    //   this.$store.commit('setVizOptions', {
    //       rawWeekly: e.target.checked
    //     })

    // }

  },
  computed: {
    // ar: {
    //   get: function() {

    //       return this.$data.showArea;
    //   },
    //   set: function(val) {
    //       alert("set ", count)
    //       this.$data.showArea = val;
    //       console.log(this.showArea + " " + count)
    //       if(val)
    //       {
    //         count = 0
    //         numRenders[count]++
    //         if(count < 1) config.layer.push(area)
    //         //else config.layer.pop(area)
    //         alert(count)
    //       }
    //   },
    // },
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
    showArea() {
      return this.$store.state.showArea
    },
    showTooltip() {
      return this.$store.state.showTooltip
    },
    spec() {

      // let topStdDev = []
      // let lowStdDev = []

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": {
          "values": []
        },
        "width": 420,
        "height": 200,
        "config":{
          "axis":{
            "grid": false
          },
          "legend": {
            "offset": -80,
          },
          "selection": {
            "grid": {
              "type": "interval", "bind": "scales"
            }
          }
        },
        "layer": [

          {

            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "timeUnit": "yearmonth",
                "axis": {
                  "title": null
                }
              },
              "y": {
                "field": "value",
                "type": "quantitative",

                "axis": {
                  "title": null
                }
              },
              "color": {
                "field": "name",
                "type": "nominal",
                "scale":{"scheme": "set1"},

              }
            },
            "mark": {
              "type": "line",
              "interpolate": "basis",

              "clip": true
            }
          }
        ],

        "padding": {
          "top": 20,
          "left": 0,
          "right": 30,
          "bottom": 55


        }
      }
      let ogLayers = [{

                  "encoding": {
                    "x": {
                      "field": "date",
                      "type": "temporal",
                      "timeUnit": "yearmonth",
                      "axis": {
                        "title": null
                      }
                    },
                    "y": {
                      "field": "value",
                      "type": "quantitative",

                      "axis": {
                        "title": null
                      }
                    },
                    "color": {
                      "field": "name",
                      "type": "nominal",
                      "scale":{"scheme": "set1"},

                    }
                  },
                  "mark": {
                    "type": "line",
                    "interpolate": "basis",

                    "clip": true
                  }
                }]

      let area = {
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
                    "field": "value",
                    "type": "quantitative"

                  },
                  "y2": {
                    "aggregate": "ci0",
                    "field": "value",
                    "type": "quantitative"
                  },
                  "color": {"type": "nominal", "scale":{"scheme": "set1"}},
                  "opacity": {"value": 0.2}
                }
              }
      let raw = {
          "mark": {
            "type": "line",
            "clip": true
          },
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "timeUnit": "yearmonthdatehoursminutes",
              "scale": {

                "domain": "unaggregated"
              }
            },
            "y": {
              "field": "value",
              "type": "quantitative"

            },
            "color": {"value": "blue"},
            "opacity": {"value": 0.3}
          }
        }
      let tooltip =

      {

            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "timeUnit": "yearmonth",
                "axis": {
                  "title": null
                }
              },
              "y": {
                "field": "value",
                "type": "quantitative",

                "axis": {
                  "title": null
                }
              },
              "color": {
                "field": "name",
                "type": "nominal",
                "scale":{"scheme": "set1"},

              },
              "tooltip": {
                "field": "value",
                "type": "quantitative"
              }
            },
            "mark": {
              "type": "point",
              "interpolate": "basis",

              "clip": true
            }
          }


      //when we have rendered the number of total charts, reset the chart count, this is to prevent duplicate marks overlapping
      if(count > 10) count = 0

      //add unique title for each object to general spec/config var
      let newObj = {"title": this.title}
      for(var k in config) newObj[k] = config[k];



      //push the raw weekly mark to general spec
      if(this.rawWeekly) config.layer.push(raw)
      else {
        //if user doesn't want raw weekly mark, then iterate through all marks and pop the raw weekly marks
        for(var x = 0; x < config.layer.length; x++) {
          if(config.layer[x] == raw) {
            config.layer = ogLayers
          }
        }
      }

      //push the area to general spec
      if(this.showArea) {config.layer.push(area)}
      else {
        //if user doesn't want area mark, then set layers to og
        for(var x = 0; x < config.layer.length; x++) {
          if(config.layer[x] == area) {
            config.layer = ogLayers
          }
        }
      }

      //push the tooltip to general spec
      if(this.showTooltip) {
        config.layer.push(tooltip)


      }
      else {
        //if user doesn't want tooltip mark, then iterate through all marks and pop the tooltip marks
        for(var x = 0; x < config.layer.length; x++) {
          if(config.layer[x] == tooltip) {
            config.layer = ogLayers
          }
        }
      }



      // earliest: function (){
      for(var i = 0; i < config.layer.length; i++){
        config.layer[i].encoding.x["scale"] =
          {
            "domain": [{"year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate()},{"year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate()}]
          }
      }


      //have rendered one unique chart, so increment count
      count++
      return newObj
    },
    chart() {
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
        if (!this.comparedTo) {
          buildLines(data[this.repo], (obj, key, field, count) => {
            // Build basic chart using rolling averages
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(d, 'value', this.period)
            console.log('rolling, before+after', d, rolling)
            if (!this.disableRollingAverage) {
              normalized.push(rolling)
              legend.push(field)
              colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
            }
            if (this.rawWeekly || this.disableRollingAverage) {
              normalized.push(d)
              legend.push("raw " + field)
              colors.push(this.disableRollingAverage ? window.AUGUR_CHART_STYLE.brightColors[count] : window.AUGUR_CHART_STYLE.dullColors[count])
            }
          })
        } else if (this.compare === 'each' && this.comparedTo) {
          // Build comparison using z-scores
          buildLines(data[this.comparedTo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period)
            normalized.push(rolling)
            legend.push(this.comparedTo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          })
          buildLines(data[this.repo], (obj, key, field, count) => {
            let d = defaultProcess(obj, key, field, count)
            let rolling = AugurStats.rollingAverage(AugurStats.zscores(d, 'value'), 'value', this.period)
            normalized.push(rolling)
            legend.push(this.repo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.dullColors[count])
          })
        } else if (this.comparedTo) {
          // Build chart compared to baseline
          //this.mgConfig.baselines = [{value: 1, label: this.repo}]
          buildLines(data[this.comparedTo], (obj, key, field, count) => {
            normalized.push(AugurStats.makeRelative(obj[key], data[this.repo][key], field, {
              earliest: this.earliest,
              latest: this.latest,
              byDate: true,
              period: this.period
            }))
            legend.push(this.comparedTo + ' ' + field)
            colors.push(window.AUGUR_CHART_STYLE.brightColors[count])
          })
        }

        if (normalized.length == 0) {
          //this.mgConfig.missing_text = 'Data empty'

          this.renderError()
        } else {
          //shared.baseData = data.map((e) => { e.repo = this.repo.toString(); return e })
          for(var i = 0; i < legend.length; i++){
            normalized[i].forEach(d => {
              d.name = legend[i]
              d.color = colors[i]
              values.push(d)

            })
          }
          this.values = values
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

   //        {
   //    "encoding": {
   //      "x": {"field": "date", "type": "temporal"},
   //      "y": {"field": "value", "type": "quantitative"},
   //      "color": {"field": "name", "type": "nominal"}
   //    },
   //    "layer": [{
   //      "mark": "line"
   //    },{
   //      "selection": {
   //        "tooltip": {
   //          "type": "single",
   //          "nearest": true,
   //          "on": "mouseover",
   //          "encodings": [
   //            "x"
   //          ],
   //          "empty": "none"
   //        }
   //      },
   //      "mark": "point",
   //      "encoding": {
   //        "opacity": {
   //          "condition": {
   //            "selection": "tooltip",
   //            "value": 1
   //          },
   //          "value": 0
   //        }
   //      }
   //    }]
   //  }
   //  let tooltip =
   //  {
   //    "transform": [
   //      {
   //        "filter": {
   //          "selection": "tooltip"
   //        }
   //      }
   //    ],
   //    "layer": [{
   //      "mark": {
   //       "type": "rule",
   //       "color": "gray"
   //      },
   //      "encoding": {
   //        "x": {
   //          "type": "temporal",
   //          "field": "date"
   //        }
   //      }
   //    }, {
   //      "mark": {
   //        "type": "text",
   //        "align": "left",
   //        "dx": 5,
   //        "dy": -5
   //      },
   //      "encoding": {
   //        "text": {
   //          "type": "quantitative",
   //          "field": "value"
   //        },
   //        "color": {
   //          "type": "nominal",
   //          "field": "name"
   //        },
   //        "x": {
   //          "type": "temporal",
   //          "field": "date"
   //        },
   //        "y": {
   //          "type": "quantitative",
   //          "field": "value"
   //        }
   //      }
   //    }]
   // }


//--------------------------

// return {
//         "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
//         "data": {
//           "values": [],
//           // "url": "https://vega.github.io/vega-lite/data/stocks.csv",
//           "format": {
//           "type": "json",
//           "parse": {"date": "date"}
//           }
//         },
//         "title": "hahhahahahhah",
//         "config":{
//           "title": {
//             "offset": -1,
//             "baseline": "top",
//             "angle": 30,
//             "fontSize": 20
//           },
//           "view":{
//             "strokeWidth": 2
//           },
//           "trail":{
//             "size": 10
//           }
//         },
//         "layer":[
//           {
//             "encoding": {
//               "x": {
//                 "field": "date",
//                 "type": "temporal",
//                 "axis": {
//                   "format": "%Y"
//                 }
//               },
//               "y": {
//                 "field": "iterations",
//                 "type": "quantitative"
//               },
//               "tooltip": {
//                 "type": "quantitative",

//                 "field": "iterations"

//               },
//               "color": {
//                 "value": "#FF3647"
//               }
//             },"layer": [{
//               "mark": "line"
//             },{
//               "selection": {
//                 "tooltip": {
//                   "type": "single",
//                   "nearest": true,
//                   "on": "mouseover",
//                   "encodings": [
//                     "x"
//                   ],
//                   "empty": "none"
//                 }
//               },
//               "mark": "point",
//               "encoding": {
//                 "opacity": {
//                   "condition": {
//                     "selection": "tooltip",
//                     "value": 1
//                   },
//                   "value": 0
//                 }
//               }
//             },
//             {
//               "transform": [
//                 {
//                   "filter": {
//                     "selection": "tooltip"
//                   }
//                 }
//               ],
//               "layer": [
//                 {
//                   "mark": {
//                   "type": "rule",
//                   "color": "gray"
//                   },
//                   "encoding": {
//                     "x": {
//                       "type": "temporal",
//                       "field": "date"
//                     }
//                   }
//                 },
//                 {
//                   "mark": {
//                     "type": "text",
//                     "align": "center",
//                     "dy": -15
//                   },
//                   "encoding": {
//                     "text": {
//                       "type": "quantitative",
//                       "field": "iterations"
//                     },
//                     "color": {
//                       "type": "nominal",
//                       "field": "action"
//                     },
//                     "x": {
//                       "type": "temporal",
//                       "field": "date"
//                     },
//                     "y": {
//                       "type": "quantitative",
//                       "field": "iterations"
//                     }
//                   }
//                 }
//               ]
//             }
//           ]
//         }
//        ]
//       }

//--------------------------

// return {
      //   "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
      //   "data": {
      //     "values": [],
      //     // "url": "https://vega.github.io/vega-lite/data/stocks.csv",
      //     "format": {
      //     "type": "json",
      //     "parse": {"date": "date"}
      //     }
      //   },
      //   "title": this.title,
      //   "config":{
      //     "title": {
      //       "offset": 50
      //     }
      //   },
      //   "width": 820,
      //   "height": 350,
      //   "layer": [
      //     // {
      //     //   "encoding": {
      //     //     "x": {"field": "date", "type": "temporal", "axis": {"format": "%Y"}},
      //     //     "y": {"field": "commits", "type": "quantitative"},
      //     //     // "color": {"field": "status", "type": "nominal"},
      //     //     // "tooltip": {"field": "price", "type": "quantitative"},
      //     //     "size": {
      //     //       "field": "total",
      //     //       "type": "quantitative",
      //     //       "legend": {
      //     //         "title": this.title,
      //     //       },
      //     //       "scale": {
      //     //         "type": "sqrt"
      //     //       }
      //     //     },
      //     //   },

      //     //   "layer": [{
      //     //     "mark": "line"
      //     //   },

      //     //   // ,{
      //     //   //   "selection": {
      //     //   //     "tooltip": {
      //     //   //       "type": "single",
      //     //   //       "nearest": true,
      //     //   //       "on": "mouseover",
      //     //   //       "encodings": [
      //     //   //         "x"
      //     //   //       ],
      //     //   //       "empty": "none"
      //     //   //     }
      //     //   //   },
      //     //   //   "mark": "point",
      //     //   //   "encoding": {
      //     //   //     "opacity": {
      //     //   //       "condition": {
      //     //   //         "selection": "tooltip",
      //     //   //         "value": 1
      //     //   //       },
      //     //   //       "value": 0
      //     //   //     }
      //     //   //   }
      //     //   // }
      //     //   ]
      //     // },
      //     {
      //       // "transform": [{
      //       //   "calculate": "toDate(datum[\"date\"])", "as": "date"
      //       // },{
      //       //   "filter": {"selection": "tooltip"}
      //       // }],
      //       "layer": [
      //       // {
      //       //   "mark": {
      //       //    "type": "rule",
      //       //    "color": "white"
      //       //   },
      //       //   // "selection": {
      //       //   //   "paintbrush": {
      //       //   //     "type": "single",
      //       //   //     "on": "mouseover",
      //       //   //   },
      //       //   //   "grid": {
      //       //   //     "type": "interval", "bind": "scales"
      //       //   //   }
      //       //   // },
      //       //   "encoding": {
      //       //     "x": {
      //       //       "type": "temporal",
      //       //       "field": "date"
      //       //     }
      //       //   }
      //       // },
      //       {
      //         "mark": {
      //           "type": "line",
      //           // "align": "left",
      //           // "dx": 5,
      //           // "dy": -5
      //         },
      //         "encoding": {
      //           "x": {
      //             "field": "date",
      //             "type": "temporal",
      //             "axis": {
      //               "format": "%Y"
      //             }
      //           },
      //           "y": {
      //             "field": "commits",
      //             "type": "quantitative"
      //           },
      //           // "size": {
      //           //   "field": "commits",
      //           //   "type": "quantitative"
      //           // },
      //           "color": {
      //             "value": "#FF3647"
      //           }
      //         },
      //         "axes": [
      //          {
      //            "type": "x",
      //            "scale": "x",
      //            "title": "X-Axis",
      //            "properties": {
      //              "ticks": {
      //                "stroke": {"value": "steelblue"}
      //              },
      //              "majorTicks": {
      //                "strokeWidth": {"value": 10}
      //              },
      //              "labels": {
      //                "text": {"template": "{{datum.data|number:'+,'}}"},
      //                "fill": {"value": "steelblue"},
      //                "angle": {"value": 50},
      //                "fontSize": {"value": 14},
      //                "align": {"value": "left"},
      //                "baseline": {"value": "middle"},
      //                "dx": {"value": 3}
      //              },
      //              "title": {
      //                "fontSize": {"value": 16}
      //              },
      //              "axis": {
      //                "stroke": {"value": "#333"},
      //                "strokeWidth": {"value": 1.5}
      //              }
      //            }
      //          }
      //         ]
      //       }]
      //    }
      //  ]
      // }

//--------------------------------


//   {
//   "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
//   "data": {
//     "url": "data/stocks.csv",
//     "format": {
//       "type": "csv",
//       "parse": {
//         "date": "date"
//       }
//     }
//   },
//   "width": 700,
//   "height": 350,
//   "title": "hahhahahahhah",
//   "config":{
//     "title": {
//       "offset": -1,
//       "baseline": "top",
//       "angle": 30,
//       "fontSize": 20
//     },
//     "view":{
//       "strokeWidth": 2
//     },
//     "trail":{
//       "size": 10
//     }
//   },
//   "transform": [{"filter": "datum.symbol==='GOOG'"}],
//   "layer":[
//     {
//       "encoding": {
//         "x": {
//           "field": "date",
//           "type": "temporal",
//           "axis": {
//             "format": "%Y"
//           }
//         },
//         "y": {
//           "field": "price",
//           "type": "quantitative"
//         },
//         "tooltip": {
//           "type": "quantitative",

//           "field": "price"

//         },
//         "color": {
//           "value": "#FF3647"
//         }
//       },"layer": [{
//         "mark": "line"
//       },{
//         "selection": {
//           "tooltip": {
//             "type": "single",
//             "nearest": true,
//             "on": "mouseover",
//             "encodings": [
//               "x"
//             ],
//             "empty": "none"
//           }
//         },
//         "mark": "point",
//         "encoding": {
//           "opacity": {
//             "condition": {
//               "selection": "tooltip",
//               "value": 1
//             },
//             "value": 0
//           }
//         }
//       },
//       {
//         "transform": [
//           {
//             "filter": {
//               "selection": "tooltip"
//             }
//           }
//         ],
//         "layer": [
//           {
//             "mark": {
//             "type": "point",
//             "color": "gray"
//             },
//             "encoding": {
//               "x": {
//                 "type": "temporal",
//                 "field": "date"
//               }
//             }
//           },
//           {
//             "mark": {
//               "type": "text",
//               "align": "center",
//               "dy": -15
//             },
//             "encoding": {
//               "text": {
//                 "type": "quantitative",
//                 "field": "price"
//               },
//               "color": {
//                 "type": "nominal",
//                 "field": "symbol"
//               },
//               "x": {
//                 "type": "temporal",
//                 "field": "date"
//               },
//               "y": {
//                 "type": "quantitative",
//                 "field": "price"
//               }
//             }
//           }
//         ]
//       }
//     ]
//   }
// ]


// }

</script>
