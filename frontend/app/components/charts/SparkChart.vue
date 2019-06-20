<template>
  <div ref="holder" style="position: relative; z-index: 5">
    <!-- <div class="spinner "></div> -->
    <div class="chart hidefirst ">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>

    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'

export default {
  props: ['repo', 'owner', 'source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'color'],
  data() {
    return {
      values: [],
      user: null
    }
  },
  computed: {
    spec() {
      console.log(this.owner)
      console.log(this.data)
      this.values = this.convertKey(this.data)

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 80,
        "height": 50,
        "padding": 0,

        //"autosize": {"type": "fit", "contains": "padding"},
      
      
        // "data": {"url": "https://vega.github.io/vega-lite/data/unemployment-across-industries.json"},
        "mark": {
          "type":"line",
          "interpolate": "basis"
        },
        "encoding": {
          "x": {
            "timeUnit": "yearmonth", "field": "date", "type": "temporal",
            "axis": {"labels": false, "grid": false, "title": false, "ticks": false}
          },
          "y": {
            // "aggregate": "sum", 
            "field": "value","type": "quantitative",
            "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          },
          "color": {"value": this.color}
        }
        

        
      }

      
      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
      $(this.$el).find('.spinner').removeClass('loader')


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
            console.log(key)
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
