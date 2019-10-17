<template>
  <div ref="holder" class="insightChartDiv">
    <spinner v-if="!loaded" class="insightChartSpinner"></spinner>
    <div v-if="loaded" class="">
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
      loaded: true,
      x:0,
      y:0
    }
  },
  computed: {
    spec() {
      var win = window,
      doc = document,
      docElem = doc.documentElement,
      body = doc.getElementsByTagName('body')[0],
      x = win.innerWidth || docElem.clientWidth || body.clientWidth,
      y = win.innerHeight|| docElem.clientHeight|| body.clientHeight;
      this.x = x
      this.y = y
      // repo[this.source]().then((data) => {
        this.values = this.data//this.convertKey(this.data)
      // })
      console.log(this.values)
      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": this.x / 4,//263.7,
        "height": this.y / 4,//166,
        "padding": {'left': 0, 'top': 0, 'right': 0, 'bottom': 0},
        "mark": {
          "type":"line",
          "interpolate": "basis"
        },
        "encoding": {
          "x": {
            "timeUnit": "yearmonthdate", "field": "date", "type": "temporal",
            "axis": {"grid": false, "format": "%b %d"}
          },
          "y": {
            // "aggregate": "sum", 
            "field": "value","type": "quantitative",
            "axis": {"grid": false, "title":false, "ticks": false},
          },
          "color": {"value": this.color}
        }
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