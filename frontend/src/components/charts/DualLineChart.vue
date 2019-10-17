<template>
  <div ref="holder">
    <div class="tickchart">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
      <div class="DualLineChartDiv3">
        <p></p>
      </div>
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'fieldone', 'fieldtwo'],
  data() {
    return {
      values: [],
      colors: ['red', 'green']
    }
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepo () {
      return this.$store.state.gitRepo
    },
    period () {
      return this.$store.state.trailingAverage
    },
    earliest () {
      return this.$store.state.startDate
    },
    latest () {
      return this.$store.state.endDate
    },
    compare () {
      return this.$store.state.compare
    },
    comparedRepos () {
      return this.$store.state.comparedRepos
    },
    rawWeekly () {
      return this.$store.state.rawWeekly
    },
    showArea () {
      return this.$store.state.showArea
    },
    showTooltip () {
      return this.$store.state.showTooltip
    },
    showDetail () {
      return this.$store.state.showDetail
    },
    spec() {
      let config = {
          "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
          "padding": {'left': 25, 'top': 15, 'right': 80, 'bottom': 50},
          "config": {
              // "bar": {
              //   "discreteBandSize": 10
              // },
              // "zero": false,
              // "scale": {
              //   "nice": false,

              // },
              "axis": {
                "tickRound": false
              },
              "title": {
                "fontSize": 1,
              }

          },
          "title": {
            "text": this.title,
            // "offset": 55
            "offset": 10,
            
          },
          "width": 1000,
          "height": 360,
          "layer": [ 
            {
              "encoding": {
                "x": {
                  "field": "date",
                  "type": "temporal",
                  "axis": {
                    "format": "%b %Y", "title": " "
                  }
                },
                "y": {
                  "field": this.fieldone,
                  "type": "quantitative",
                  "axis": {
                    "title": null
                  }
                },
                "color": {
                    "field": "type",
                    "type": "nominal",
                    "scale": { "range": this.colors},
                    "sort": false
                  },
              },
              "mark": {
                "type": "line",
                "interpolate": "basis",
                "clip": true
              }
            },
            {
              "encoding": {
                "x": {
                  "field": "date",
                  "type": "temporal",
                  "axis": {
                    "format": "%b %Y", "title": " "
                  }
                },
                "y": {
                  "field": this.fieldtwo,
                  "type": "quantitative",
                  "axis": {
                    "title": null
                  }
                },
                "color": {
                    "field": "type",
                    "type": "nominal",
                    "scale": { "range": this.colors},
                    "sort": false
                  },
              },
              "mark": {
                "type": "line",
                "interpolate": "basis",
                "clip": true
              }
            }
          ]
      }
      // Get the repos we need
      let repos = []
      if (this.repo) {
        if (window.AugurRepos[this.repo])
          repos.push(window.AugurRepos[this.repo])
        else if (this.gitRepo){
          let temp = window.AugurAPI.Repo({"gitURL": this.gitRepo})
          if (window.AugurRepos[temp.toString()])
            temp = window.AugurRepos[temp.toString()]
          else
            window.AugurRepos[temp.toString()] = temp
          repos.push(temp)
        }
      }// end if (this.$store.repo)

            /*
       * Takes a string like "commits,lines_changed:additions+deletions"
       * and makes it into an array of endpoints:
       *
       *   endpoints = ['commits','lines_changed']
       *
       * and a map of the fields wanted from those endpoints:
       *
       *   fields = {
       *     'lines_changed': ['additions', 'deletions']
       *   }
       */
      let endpoints = []
      let fields = {}
      this.source.split(',').forEach((endpointAndFields) => {
        let split = endpointAndFields.split(':')
        endpoints.push(split[0])
        if (split[1]) {
          fields[split[0]] = split[1].split('+')
        }
      })
      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
      $(this.$el).find('.stackedbarchart').removeClass('loader')
      let processGitData = (data) => {
        let repo = window.AugurAPI.Repo({ gitURL: this.repo })
        let dat = []
        repo.changesByAuthor().then((changes) => {
          dat.push(changes)
        })
      }
      let defaultProcess = (obj, key) => {
            let d = null
            if (typeof(field) == "string") field = [field]
            d = AugurStats.convertKey(obj[key], key)
            return d
          }
      let processData = (data) => {
        console.log(repos, data, "CHECK")
        // let sort = this.field == 'commit' ? "patches" : "net"
        // data.sort(function(a, b) {
        //   return b[sort] - a[sort];
        // });
        // let sum_commit = 0 
        // let sum_loc = 0
        // let max_loc = 0
        // let max_commit = 0
        // let min_loc = 0
        // let min_commit = 0
        // for (let i = 0; i < data.length; i++){
        //   sum_commit += data[i]['patches']
        //   sum_loc += data[i]['net']
        //   data[i]['index'] = i
        //   if (data[i]['net'] > max_loc)
        //     max_loc = data[i]['net']
        //   if (data[i]['patches'] > max_commit)
        //     max_commit = data[i]['patches']
        //   if (data[i]['net'] < min_loc)
        //     min_loc = data[i]['net']
        //   if (data[i]['patches'] < min_commit)
        //     min_commit = data[i]['patches']
        //   if (i == 0)
        //     data[i].key = "commits"
        //   else
        //     data[i].key = "net lines changed"
        //   // data[i]['length'] = data[i]['name'].length
        // }
        

        data.forEach((el) => {
          if('closed_count' in el){
            el.type = 'closed'
            this.total_closed += el.closed_count
          }
          if('open_count' in el){
            el.type = 'open'
            this.total_open += el.open_count
          }
        })
        

        repos.forEach((repo) => {
          this.values = data
        })
      }
      if (this.data) {
        processData(this.data)
      } else {
        let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
        repo[this.source]().then((data) => {
          console.log("batch data", data)
          processData(data)
        }, () => {
          //this.renderError()
        }) // end batch request
      }
      return config
    },
  }
}
</script>