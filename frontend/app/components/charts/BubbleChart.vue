<template>
  <div ref="holder">
    <div class="bubblechart hidefirst invis">
      <vega-interactive :spec="spec" :data="values"></vega-interactive>
      <p> {{ chart }} </p>
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'

let spec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
  "spec": {
    "hconcat": [{
      "title": "Code Engagement",
      "width": 375,
      "height": 300,
      "mark": "circle",
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover",
        }
      },
      "encoding": {
        "x": {
          "field": "commit_comments", 
          "type": "quantitative",
        },
        "y": {
          "field": "commits", 
          "type": "quantitative",
          "scale": {
            "type": "sqrt"
          }
        },
        "color": {
          "condition": {
            "selection": "paintbrush",
            "value": "#FF3647"
          },
          "value": "grey"
        },
        "size": {
          "field": "total", 
          "type": "quantitative",
          "legend": {
            "title": "all contributions",
          },
          "scale": {
            "type": "sqrt"
          }
        },
      }
    }, {
      "title": "Community Engagement",
      "width": 375,
      "height": 300,
      "mark": "circle",
      "encoding": {
        "x": {
          "field": "issue_comments", 
          "type": "quantitative",
          "scale": {
            "type": "sqrt",
            "bandPaddingInner": 3
          },
          "axis": {
            "tickCount": 10
          }
        },
        "y": {
          "field": "issues", 
          "type": "quantitative",
          "scale": {
            "type": "sqrt"
          }
        },
        "size": {
          "field": "total", 
          "type": "quantitative",
          "legend": {
            "title": "all contributions",
          },
          "scale": {
            "type": "sqrt"
          }
        },
        "color": {
          "condition": {
            "selection": "paintbrush",
            "value": "#FF3647"
          },
          "value": "grey"
        },
      }
    }]
  }
};

export default {
  props: ['citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate'],
  data() {
    return {
      values: []
    }
  },
  components: {
    'vega-interactive': VueVega.mapVegaLiteSpec(spec)
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo
    },
    spec() {
      return 
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