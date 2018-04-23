<template>
  <div ref="holder">
    <div class="stackedbarchart hidefirst invis">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'

export default {
  props: ['citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate'],
  data() {
    return {
      values: []
    }
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo
      //TODO: add in functionality for date rate change (convertDates in AugurStats.js)
    },
    spec() {
      return {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": { "values": [] },        
        "title": "Issue Activity",
        "width": (this.$el) ? this.$el.offestWidth : 800, 
        "height": 400,
        "autosize": "fit",
        "mark": "bar",
        "encoding": {
          "y": {"aggregate": "sum",
                "field": "count", 
                "type": "quantitative"},
          "x": {"field": "date", 
                "type": "temporal"},
          "color": {"field": "action", 
                    "type": "nominal"}
        }
      }
    },
    chart() {
      $(this.$el).find('.showme').addClass('invis')
      $(this.$el).find('.stackedbarchart').addClass('loader')
      if (this.repo) {
        window.AugurRepos[this.repo].issueActivity().then((data) => {
          $(this.$el).find('.showme, .hidefirst').removeClass('invis')
          $(this.$el).find('.stackedbarchart').removeClass('loader')
          this.values = data
        })
      }
    }
  }
}

</script>