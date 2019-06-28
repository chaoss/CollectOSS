<template>
  <div ref="holder" style="position: relative; z-index: 5">
    <spinner v-if="!loaded" :size="30" style="top: 5%; position: relative; transform: translateY(-50%);"></spinner>
    <div class="chart hidefirst">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
    </div>

  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'
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
      loaded: false
    }
  },
  computed: {
    spec() {
      let repo = window.AugurAPI.Repo({"gitURL": this.url})
      repo[this.source]().then((data) => {
        this.values = this.convertKey(data)
      })

      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 80,
        "height": 50,
        "padding": 0,
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
            "field": "value","type": "quantitative",
            "axis": {"labels": false, "grid": false, "title": false, "ticks": false},
          },
          "color": {"value": this.color}
        }

      }

      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
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
