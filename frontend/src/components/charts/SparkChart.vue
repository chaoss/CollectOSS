<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder" class="sparkChartDiv">
    <h3 class="sparkChartHeader">{{ title }}</h3>
    <!-- <spinner :size="30" class="sparkChartSpinner"></spinner> -->
    <div class="chart">
      <!-- <div id="hi"></div> -->
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
import Spinner from '../Spinner.vue'

export default {
  props: ['url', 'source', 'title', 'data', 'color'],
  components: {
    Spinner
  },
  data() {
    return {
      values: [],
      user: null,
      loaded: false,
      chart: null,
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

      this.values = this.data//this.convertKey(this.data)

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": this.x / 15,
        "height": this.y / 25,
        "padding": 0,
        "mark": {
          "type":"line",
          "interpolate": "basis"
        },
        "encoding": {
          "x": {
            "timeUnit": "yearmonthdate", "field": "date", "type": "temporal",
            "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          },
          "y": {
            "field": "value","type": "quantitative",
            "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          },
          "color": {"value": this.color}
        }

      }
      // if (config.data.length == 0){
      //   this.spec;
      //   this.renderError()
      //   return
      // }
      // config.data = {"values": this.values}
      // vegaEmbed('#hi', config, {tooltip: {offsetY: -110}, mode: 'vega-lite'}) 
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
