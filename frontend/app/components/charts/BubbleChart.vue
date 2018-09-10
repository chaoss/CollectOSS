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
import AugurStats from 'AugurStats'

let spec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
  "spec": {
    "hconcat": [{
      "title": "Code Engagement",
      "width": 475,
      "height": 300,
      "mark": {
        "type": "circle",
        "cursor": "pointer"
      },
      "transform": [{
        "calculate": "'https://www.google.com/search?q=' + datum.name", "as": "url"
      }],
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover",
        },
        "grid": {
          "type": "interval", "bind": "scales"
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
        "tooltip": {
          "field": "name",
          "type": "nominal"
        },
        //"href": {"field": "url", "type": "nominal"},
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
      "width": 475,
      "height": 300,
      "mark": {
        "type": "circle",
        "cursor": "pointer"
      },
      "transform": [{
        "calculate": "'https://www.google.com/search?q=' + datum.name", "as": "url"
      }],
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover",
        },
        "grid": {
          "type": "interval", "bind": "scales"
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
          "tooltip": {
            "field": "name",
            "type": "nominal"
          },
          // "href": {"field": "url", "type": "nominal"},
          "value": "grey"
        },
      }
    }]
  }
};

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'comparedTo'],
  data() {
    return {
      values: []
    }
  },
  components: {
    'vega-interactive': window.VueVega.mapVegaLiteSpec(spec)
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo
    },
    showBelowAverage() {
      return this.$store.state.showBelowAverage
    },
    chart() {
      // so that this will get re-rendered consistently
      let removeBelowAverageContributors = !this.showBelowAverage
      $(this.$el).find('.showme').addClass('invis')
      $(this.$el).find('.bubblechart').addClass('loader')
      let shared = {};
      let processData = (data) => {
        window.AugurRepos[this.repo][this.source]().then((data) => {
          shared.baseData = data.map((e) => { e.repo = this.repo.toString(); return e })
          if (removeBelowAverageContributors) {
            shared.baseData = AugurStats.aboveAverage(shared.baseData, 'total')
          }
          if (this.comparedTo) {
            return window.AugurRepos[this.comparedTo].contributors();
          } else {
            return new Promise((resolve, reject) => { resolve() });
          }
        }).then((compareData) => {
          if (compareData) {
            compareData = compareData.map((e) => { e.repo = this.comparedTo; return e })
            if (removeBelowAverageContributors) {
              compareData = AugurStats.aboveAverage(compareData, 'total')
            }
            this.values = _.concat(shared.baseData, compareData)
          } else {
            this.values = shared.baseData;
          }
          $(this.$el).find('.showme, .hidefirst').removeClass('invis')
          $(this.$el).find('.bubblechart').removeClass('loader')
        })
      }
      if (this.repo) {

        if (this.data){
          processData(this.data)
        } else {
          window.AugurRepos[this.repo][this.source]().then((data) => {
            shared.baseData = data.map((e) => { e.repo = this.repo.toString(); return e })
            if (removeBelowAverageContributors) {
              shared.baseData = AugurStats.aboveAverage(shared.baseData, 'total')
            }
            if (this.comparedTo) {
              return window.AugurRepos[this.comparedTo].contributors();
            } else {
              return new Promise((resolve, reject) => { resolve() });
            }
          }).then((compareData) => {
            if (compareData) {
              compareData = compareData.map((e) => { e.repo = this.comparedTo; return e })
              if (removeBelowAverageContributors) {
                compareData = AugurStats.aboveAverage(compareData, 'total')
              }
              this.values = _.concat(shared.baseData, compareData)
            } else {
              this.values = shared.baseData;
            }
            $(this.$el).find('.showme, .hidefirst').removeClass('invis')
            $(this.$el).find('.bubblechart').removeClass('loader')
          })
        }


      }
    }
  }
}

</script>
