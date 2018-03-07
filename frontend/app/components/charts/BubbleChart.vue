<template>
  <div ref="holder">
    <div class="bubblechart hidefirst invis">
      <vega-interactive ref="vega" :data="values"></vega-interactive>
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
            "field": "repo",
            "type": "nominal",
            "scale": { "range": ['#FF3647', '#4736FF'] }
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
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover",
        }
      },
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
            "field": "repo",
            "type": "nominal",
            "scale": { "range": ['#FF3647', '#4736FF'] }
          },
          "value": "grey"
        },
      }
    }]
  }
};

export default {
  props: ['citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'comparedTo'],
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
      console.log('chart', this.$refs.vega)
      return this.$store.state.baseRepo
    },
    chart() {
      $(this.$el).find('.showme').addClass('invis')
      $(this.$el).find('.bubblechart').addClass('loader')
      let shared = {};
      if (this.repo) {
        window.GHDataRepos[this.repo].contributors().then((data) => { 
          shared.baseData = data.map((e) => { e.repo = this.repo.toString(); return e }) 
          shared.baseData = data;   
          if (this.comparedTo) {
            return window.GHDataRepos[this.comparedTo].contributors();
          } else {
            return new Promise((resolve, reject) => { resolve() });
          }
        }).then((compareData) => {
          if (compareData) {
            compareData = compareData.map((e) => { e.repo = this.comparedTo; return e })
            this.values = _.concat(shared.baseData, compareData)
          } else {
            this.values = shared.baseData;
          }
          console.log('final chart', this.$refs.vega)
          $(this.$el).find('.showme, .hidefirst').removeClass('invis')
          $(this.$el).find('.bubblechart').removeClass('loader')
        })
      }
    }
  }
}

</script>