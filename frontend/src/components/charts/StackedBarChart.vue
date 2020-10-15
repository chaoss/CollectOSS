<!-- #SPDX-License-Identifier: MIT -->
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
import AugurStats from '@/AugurStats.ts'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
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
      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": { "values": [] },
        "title": this.title,
        "width": (this.$el) ? this.$el.offestWidth : 800,
        "height": 400,
        "autosize": "fit",
        "mark": "bar",
        "encoding": {
          "y": {"aggregate": "sum",
                "field": "value",
                "type": "quantitative"},
          "x": {"field": "date",
                "type": "temporal"},
          "color": {"field": "field",
                    "type": "nominal"}
        }
      }


      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
      $(this.$el).find('.stackedbarchart').removeClass('loader')

      let endpoints = []
      let fields = {}
      this.source.split(',').forEach((endpointAndFields) => {
        let split = endpointAndFields.split(':')
        endpoints.push(split[0])
        if (split[1]) {
          fields[split[0]] = split[1].split('+')
        }
      })

      // Get the repos we need
      let repos = []
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo])
      }

      let processData = (data) => {
        // We usually want to limit dates and convert the key to being vega-lite friendly
        let defaultProcess = (obj, key, field, count) => {
          let d = AugurStats.convertKey(obj[key], field)
          return AugurStats.convertDates(d, this.earliest, this.latest)
        }

        // Normalize the data into [{ date, value },{ date, value }]
        // BuildLines iterates over the fields requested and runs onCreateData on each
        let normalized = []
        let buildLines = (obj, onCreateData) => {
          if (!obj) {
            return
          }
          if (!onCreateData) {
            onCreateData = (obj, key, field, count) => {
              let d = defaultProcess(obj, key, field, count)
              normalized.push(d)
            }
          }
          let count = 0
          for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
              if (fields[key]) {
                fields[key].forEach((field) => {
                  onCreateData(obj, key, field, count)
                  count++
                })
              } else {
                if (Array.isArray(obj[key]) && obj[key].length > 0) {
                  let field = Object.keys(obj[key][0]).splice(1)
                  onCreateData(obj, key, field, count)
                  count++
                } else {
                  this.renderError()
                  return
                }
              }
            } // end hasOwnProperty
          } // end for in
        } // end normalize function

        let values = []

        buildLines(data[this.repo], (obj, key, field, count) => {
          // Build basic chart
          normalized.push(defaultProcess(obj, key, field, count))
        })

        if (normalized.length == 0) {
          this.renderError()
        } else {
            for(var i = 0; i < normalized.length; i++){
              normalized[i].forEach(d => {
                //d.name = legend[i]
                //d.color = colors[i]
                values.push(d);
              })
            }
          }

        $(this.$el).find('.showme, .hidefirst').removeClass('invis')
        $(this.$el).find('.stackedbarchart').removeClass('loader')
        this.values = values
      }

      if (this.data) {
        processData(this.data)
      } else {
        window.AugurAPI.batchMapped(repos, endpoints).then((data) => {
          processData(data)
        })
      }



      return config

    },
  }
}

</script>
