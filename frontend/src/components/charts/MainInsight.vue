<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder" class="mainInsightDiv">
    <spinner v-if="!loaded" class="mainInsightSpinner"></spinner>
    <div :id="source"></div>
  </div>
</template>


<script>
import { mapState } from "vuex";
import AugurStats from "@/AugurStats.ts";
import Spinner from "../Spinner.vue";
import vegaEmbed from "vega-embed";

export default {
  props: ["url", "source", "title", "color", "data", "insight"],
  components: {
    Spinner
  },
  data() {
    return {
      values: [],
      user: null,
      loaded: true,
      computedField: "value",
      first_discovered: null,
      x: 0,
      y: 0,
      field: null
    };
  },
  computed: {},
  watch: {
    data: function() {
      if (this.data) {
        let dataFilled = true;
        console.log(this.data);
        console.log(JSON.stringify(this.data));
        if (this.data.length > 0) {
          this.spec(this.data);
        }
      } else {
        console.log("did not detect data");
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
    }
  },
  mounted() {
    this.$nextTick(() => {
      console.log(`WIDTH: ${this.$refs.holder.clientWidth}`);
      let specWidth = this.$refs.holder.clientWidth;
      let specHeight = this.$refs.holder.clientHeight;
      var win = window,
        doc = document,
        docElem = doc.documentElement,
        body = doc.getElementsByTagName("body")[0],
        x = win.innerWidth || docElem.clientWidth || body.clientWidth,
        y = win.innerHeight || docElem.clientHeight || body.clientHeight;
      
      this.x = this.$refs.holder.clientWidth;
      this.y = this.$refs.holder.clientHeight;
      this.loaded = false;
      if (this.data) {
        let dataFilled = true;
        console.log(this.data);
        console.log(JSON.stringify(this.data));
        if (this.data.length > 0) {
          this.spec(this.data);
        }
      } else {
        console.log("did not detect data");
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
    });
  },
  methods: {
    spec(data) {
      // repo[this.source]().then((data) => {
      this.values = this.convertKey(data); //this.convertKey(this.data)
      this.insertInsightLocation(this.values, this.insight);
      // })
      console.log(this.data, this.values);

      // find scale for x axis
      let maxDate = new Date();
      let minDate = new Date(maxDate.getFullYear() - 1, maxDate.getMonth(), maxDate.getDate());

      let config = {
        // "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        width: this.x * .85,
        padding: { left: 0, top: 10, right: 20, bottom: 0 },
        selection: {
          grid: {
            type: "interval",
            bind: "scales"
          }
        },
        resolve: { axis: { labels: "independent" } }, //,"scale": {"x": "independent"}},
        layer: [
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
          // {
          //   "mark": {
          //     "type": "line",
          //     "interpolate": "basis",
          //     "clip": true
          //   },
          //   "encoding": {
          //     "x": {
          //       "field": "date", "type": "temporal", "timeUnit": "yearquarter",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       },
          //       "scale": {
          //         "domain": [{"year": 2018, "month": new Date().getMonth(), "date": new Date().getDate()},{"year": new Date().getFullYear(), "month": new Date().getMonth(), "date": new Date().getDate()}]
          //       }
          //     },
          //     "detail": {"field": "repo_name", "type": "nominal"},
          //     "y": {
          //       "aggregate": "mean","field": this.computedField,"type": "quantitative",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       }
          //     },
          //     "opacity": {"value": 0.8},
          //     "color": {"value": "red"}
          //   }
          // },
          // {
          //   "mark": {
          //     "type": "line",
          //     "interpolate": "basis",
          //     "clip": true
          //   },
          //   "encoding": {
          //     "x": {
          //       "field": "date", "type": "temporal", "timeUnit": "yearquarter",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       },
          //       "scale": {
          //         "domain": [{"year": 2018, "month": new Date().getMonth(), "date": new Date().getDate()},{"year": new Date().getFullYear(), "month": new Date().getMonth(), "date": new Date().getDate()}]
          //       }
          //     },
          //     "detail": {"field": "repo_name", "type": "nominal"},
          //     "opacity": {"value": 0.8},
          //     "y": {
          //       "aggregate": "ci0","field": this.computedField,"type": "quantitative",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       }
          //     },
          //     "color": {"value": "red"}
          //   }
          // },
          // {
          //   "mark": {
          //     "type": "line",
          //     "interpolate": "basis",
          //     "clip": true
          //   },
          //   "encoding": {
          //     "x": {
          //       "field": "date", "type": "temporal", "timeUnit": "yearquarter",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       },
          //       "scale": {
          //         "domain": [{"year": 2018, "month": new Date().getMonth(), "date": new Date().getDate()},{"year": new Date().getFullYear(), "month": new Date().getMonth(), "date": new Date().getDate()}]
          //       }
          //     },
          //     "detail": {"field": "repo_name", "type": "nominal"},
          //     "opacity": {"value": 0.8},
          //     "y": {
          //       "aggregate": "ci1","field": this.computedField,"type": "quantitative",
          //       "axis": {
          //         // "labels": false,
          //         "title": ""
          //       }
          //     },
          //     "color": {"value": "red"}
          //   }
          // },
          {
            mark: {
              type: "line",
              // "interpolate": "basis",
              clip: true
            },
            encoding: {
              x: {
                field: "date",
                type: "temporal",
                timeUnit: "yearmonthdate",
                axis: {
                  labels: true,
                  title: "date"
                },
                scale: {
                  domain: [
                    {
                      year: minDate.getFullYear(),
                      month: minDate.getMonth(),
                      date: minDate.getDate()
                    },
                    {
                      year: maxDate.getFullYear(),
                      month: maxDate.getMonth(),
                      date: maxDate.getDate()
                    }
                  ]
                }
              },
              y: {
                // "aggregate": "sum",
                field: this.computedField,
                type: "quantitative",
                axis: {
                  labels: true,
                  title: this.field
                }
              },
              color: { value: this.color }
            }
          }
          // {
          //   // "transform": [
          //   //   {"filter": "datum.date = " + this.first_discovered}
          //   // ],
          //   "mark": "point",

          //   "encoding": {
          //     "x": {"field": "date", "type":"temporal"},
          //     "y": {
          //       // "aggregate": "sum",
          //       "field": this.computedField,"type": "quantitative",
          //       "axis": {
          //         "labels": true,
          //         "title": this.computedField
          //       }
          //     },
          //     "color": {"value": this.color}
          //   }
          // }
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
      };
      //show the chart again
      this.reloadImage(config);
      return config;
    },
    reloadImage(config) {
      config.data = { values: this.values };
      if (this.values.length > 0) {
        console.log("values not 0", this.values);
        this.loaded = true;
      }
      console.log(config);
      vegaEmbed("#" + this.source, config, {
        tooltip: { offsetY: -100, offsetX: 40 },
        mode: "vega-lite"
      });
    },
    convertKey(ary) {
      console.log("converting", ary);
      ary.forEach(el => {
        let keys = Object.keys(el);
        let field = null;
        let found = false;
        keys.forEach(key => {
          if (
            el[key] != null &&
            key != "date" &&
            key != "repo_name" &&
            key != "field" &&
            key != "value" &&
            !found
          ) {
            this.field = key;
            field = key;
            found = true;
          }
        });
        el["value"] = el[field];
        el["field"] = field;
      });
      return ary;
    },
    insertInsightLocation(data, insight) {
      let date_found = null;
      insight.forEach(tuple => {
        if (tuple.discovered) {
          date_found = tuple.date;
          return;
        }
      });
      data.forEach(tuple => {
        // tuple.ci_date = '2018-02-01T00:00:00.000Z'
        if (tuple.date == date_found) {
          console.log("date found in data:", tuple);
          tuple.first_discovered = date_found;
          this.first_discovered = date_found;
        }
      });
      console.log(data);
      try {
        if (data.length > 0) {
          data[data.length - 1].last_point = data[data.length - 1].date;
        } else {
          data[0].last_point = data[data.length - 1].date;
        }
      } catch (e) {
        console.log(e, "data issue", data);
      }
    }
  }
};
</script>

<style scoped>
.mainInsightDiv {
  width: 100% !important;
  margin: 40px auto;
}
</style>