<template>
  <div ref="holder" style="position: relative;">
    <spinner v-if="!loaded" style="transform:translateY(3rem)"></spinner>
    <div v-if="loaded" class="chart hidefirst ">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <!-- <p> {{ chart }} </p> -->

    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
import Spinner from '../Spinner.vue'

export default {
  props: ['url', 'source', 'title', 'color', 'data'],
  components: {
    Spinner
  },
  data() {
    return {
      values: [],
      user: null,
      loaded: true
    }
  },
  computed: {
    spec() {
      // repo[this.source]().then((data) => {
      this.values = this.data//this.convertKey(this.data)
      // })
      console.log(this.values)

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 780,
        "height": 280,
        "padding": {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
        "layer": [
          // {
          //   "mark": {"type": "errorband", "extent": "ci"},
          //   "encoding": {
          //     "x": {
          //       "timeUnit": "yearmonth", "field": "date", "type": "temporal",
          //       "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          //     },
          //     "y": {
          //       "field": "value","type": "quantitative",
          //       "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          //     }
          //   }
          // },
          {
            "mark": {
              "type":"line"
            },
            "encoding": {
              "x": {
                "timeUnit": "yearmonth", "field": "date", "type": "temporal",
                "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
              },
              "y": {
                // "aggregate": "sum", 
                "field": this.field,"type": "quantitative",
                "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
              },
              "color": {"value": this.color}
            }
          }
        ]
        
      }
      //show the chart again
      this.loaded = true
      return config
    }
  },
  methods: {
    renderChart() {

    },
    convertKey(ary) {
      ary.forEach((el) => {
        
        let keys = Object.keys(el)
        let field = null
        keys.forEach((key) => {
          if (el[key] != null && key != 'date'){
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
