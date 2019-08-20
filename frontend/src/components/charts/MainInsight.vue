<template>
  <div ref="holder" style="position: relative;">
    <spinner v-if="!loaded" style="transform:translateY(3rem)"></spinner>
    <div v-if="loaded" class="chart hidefirst ">
      <!-- <vega-lite :spec="spec" :data="values"></vega-lite> -->
      <div :id="source"></div>
      <!-- <p> {{ chart }} </p> -->

    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
import Spinner from '../Spinner.vue'

export default {
  props: ['url', 'source', 'title', 'color', 'data', 'field', 'insight'],
  components: {
    Spinner
  },
  data() {
    return {
      values: [],
      user: null,
      loaded: true,
      computedField: 'commit_count',

    }
  },
  computed: {
    
  },
  mounted() {
    if (this.data) {
      let dataFilled = true
      console.log(this.data)
      console.log(JSON.stringify(this.data))
      if (dataFilled){
        this.spec(this.data)
      }
      
    } else {
      console.log("did not detect data")
      // this.endpoint({repos:this.repos, endpoints:[this.source]}).then((data) => {
      //   console.log("YAA",JSON.stringify(data))
      //   console.log(Object.keys(data).length)
      //   if (Object.keys(data).length > 1)
      //     this.spec(data)
      //   // processData(data)
      // }).catch((error) => {
      //   console.log(error)
      //   this.renderError()
      // }) // end batch request
    }
  },
  methods: {
    spec() {
      // repo[this.source]().then((data) => {
      this.values = this.data//this.convertKey(this.data)
      this.insertInsightLocation(this.values, this.insight)
      // })
      console.log(this.data, this.values)

      let config = {
        // "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 780,
        "height": 280,
        "padding": {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
        "selection": {
          "grid": {
            "type": "interval", "bind": "scales"
          }
        },
        "resolve": {"axis": {"labels":"independent"}},//,"scale": {"x": "independent"}},
        "layer": [
          // {
          //   "mark": "rect",
          //   "transform": [
          //   ],
          //   "encoding": {
          //     "x": {"field": "first_discovered", "type": "temporal"},
          //     "x2": {"field": "last_point", "type": "temporal"},
          //     "color":{"value":"red"},
          //     "opacity": {"value": 0.1}
          //   }
          // },
          {
            "mark": {
              "type":"line",
              "interpolate": "basis"
            },
            "encoding": {
              "x": {
                "field": "date", "type": "temporal", "timeUnit": "yearquarter", 
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "detail": {"field": "repo_name", "type": "nominal"},
              "y": {
                "aggregate": "mean","field": this.computedField,"type": "quantitative",
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "color": {"value": "red"}
            }
          },
          {
            "mark": {
              "type":"line",
              "interpolate": "basis"
            },
            "encoding": {
              "x": {
                "field": "date", "type": "temporal", "timeUnit": "yearquarter", 
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "detail": {"field": "repo_name", "type": "nominal"},
              "y": {
                "aggregate": "ci0","field": this.computedField,"type": "quantitative",
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "color": {"value": "red"}
            }
          },
          {
            "mark": {
              "type":"line",
              "interpolate": "basis"
            },
            "encoding": {
              "x": {
                "field": "date", "type": "temporal", "timeUnit": "yearquarter", 
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "detail": {"field": "repo_name", "type": "nominal"},
              "y": {
                "aggregate": "ci1","field": this.computedField,"type": "quantitative",
                "axis": {
                  // "labels": false,
                  "title": ""
                }
              },
              "color": {"value": "red"}
            }
          },
          {
            "mark": {
              "type":"line"
            },
            "encoding": {
              "x": {
                "field": "date", "type": "temporal", "timeUnit": "yearmonthdate",
                "axis": {
                  "labels": true,
                  "title": "date"
                }
              },
              "y": {
                // "aggregate": "sum", 
                "field": this.computedField,"type": "quantitative",
                "axis": {
                  "labels": true,
                  "title": this.computedField
                }
              },
              "color": {"value": this.color}
            }
          },
          {
            "mark": "rule",
            "encoding": {
              "x": {"field": "first_discovered", "type":"temporal"}
            }
          }
          // {
          //   "mark": {
          //     "type":"point"
          //   },
          //   "encoding": {
          //     "x": {
          //       "field": "first_discovered", "type": "temporal", //"timeUnit": "year", 
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "y": {
          //       // "aggregate": "sum", 
          //       "field": this.computedField,"type": "quantitative",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          //     },
          //     "color": {"value": this.color},
          //   }
          // },
          // {
          //   "mark": {
          //     "type":"rule"
          //   },
          //   "encoding": {
          //     "x": {
          //       "field": "date_found", "type": "temporal", //"timeUnit": "year", 
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "color": {"value": "green"}
          //   }
          // }
        ]
        
      }
      //show the chart again
      this.loaded = true
      this.reloadImage(config)
      return config

    },
    reloadImage (config) {

      config.data = {"values": this.values}
      if (this.values.length > 0) {
        console.log("values not 0",this.values)
        this.loaded = true
      }
      console.log(config)
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -100, offsetX: 40}, mode: 'vega-lite',}) 
    },
    convertKey(ary) {
      ary.forEach((el) => {
        
        let keys = Object.keys(el)
        let field = null
        keys.forEach((key) => {
          if (el[key] != null && key != 'date' && key != 'repo_name'){
            field = key
          }
        })
        el['value'] = el[field]
        el['field'] = field 
      })
      return ary
    },
    insertInsightLocation(data, insight) {
      let date_found = null
      insight.forEach((tuple) => {
        if (tuple.discovered){
          date_found = tuple.date
          return
        }
      })   
      data.forEach((tuple) => {
        // tuple.ci_date = '2018-02-01T00:00:00.000Z'
        if (tuple.date == date_found) {
          console.log("date found in data:", tuple)
          tuple.first_discovered = date_found
        }
      })
      console.log(data)
      if (data.length > 0){
        data[data.length-1].last_point = data[data.length-1].date
      }
      else {
        data[0].last_point = data[data.length-1].date
      }

    }
  }
  
}

</script>
