<template>
  <div ref="holder">
    <div class="bubblechart hidefirst invis">
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
    },
    spec() {
      return {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "title": "Contributors",
        "data": { "values": [] },
        "width": (this.$el) ? this.$el.offestWidth : 800,
        "height": 400,
        "autosize": "fit",
        "mark": "circle",
        "encoding": {
          "x": {
            "field": "issues", 
            "type": "nominal",
          },
          "y": {
            "field": "commits", 
            "type": "quantitative",
            "scale": {
              "type": "sqrt"
            }
          },
          "size": {
            "field": "total", 
            "type": "quantitative",
            "scale": {
              "type": "sqrt"
            }
          },
          "color": {
            "field": "issue_comments",
            "type": "quantitative",
            "scale": {
              "scheme": "spectral"
            }
          }
        }
      }
    },
    chart() {
      $(this.$el).find('.showme').addClass('invis')
      $(this.$el).find('.bubblechart').addClass('loader')
      console.log('called chart()', this.repo)
      if (this.repo) {
        window.GHDataRepos[this.repo].contributors().then((data) => {
          $(this.$el).find('.showme, .hidefirst').removeClass('invis')
          $(this.$el).find('.bubblechart').removeClass('loader')
          this.values = data;
        })
      }
    }
  }
}

</script>