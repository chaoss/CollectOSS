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
  props: ['url', 'source', 'title', 'color', 'data', 'field'],
  components: {
    Spinner
  },
  data() {
    return {
      values: [],
      user: null,
      loaded: true,
      computedField: 'value'
    }
  },
  computed: {
    spec() {
      // repo[this.source]().then((data) => {
      this.values = this.convertKey(this.data)
      // })
      console.log(this.values)

      let config = {
        // "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 780,
        "height": 280,
        "padding": {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
        "transform": [
            {
              "aggregate": [
                {"op": "mean", "field": this.computedField, "as": "mean"},
                {"op": "ci0", "field": this.computedField, "as": "ci0"},
                {"op": "ci1", "field": this.computedField, "as": "ci1"}
              ],
              "groupby": []
            },
        ],
        // "layer": [
          // {
          //   "mark": "line",
          //   "encoding": {
          //     "x": {
          //       "timeUnit": "yearmonthdate", "field": "date", "type": "temporal",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "y": {
          //       "field": "mean","type": "quantitative",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          //     }
          //   }
          // },
          // {
          //   "mark": "line",
          //   "encoding": {
          //     "x": {
          //       "timeUnit": "yearmonthdate", "field": "date", "type": "temporal",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "y": {
          //       "field": "ci0","type": "quantitative",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          //     }
          //   }
          // },
          // {
          //   "mark": "line",
          //   "encoding": {
          //     "x": {
          //       "timeUnit": "yearmonthdate", "field": "date", "type": "temporal",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "y": {
          //       "field": "ci1","type": "quantitative",
          //       // "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          //     }
          //   }
          // },
          // {
            "mark": {
              "type":"line"
            },
            "encoding": {
              "x": {
                "field": "issues", "type": "quantitative", //"timeUnit": "yearmonthdate", 
                // "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
              },
              "y": {
                // "aggregate": "sum", 
                "field": this.computedField,"type": "quantitative",
                // "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
              },
              "color": {"value": this.color}
            }
          // }
        // ]
        
      }
      //show the chart again
      this.loaded = true
      this.reloadImage(config)
      return config

    }
  },
  mounted() {
    this.spec;
  },
  methods: {
    reloadImage (config) {
      config.data = {"values": this.values}
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
    }
  }
  
}

</script>
