<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder">
    <div class="groupedbarchart">
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
      <div class="timeIntervalChartDiv">
        <p>*The black "baseline" represents the averages of both LoC and commits for this repo across all months. Wherever this bar stretches to shows how far above or below the raw value of the statistic is from the regular average.</p>
      </div>
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'field'],
  data() {
    return {
      values: []
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
    months() { return {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',  11: 'Nov',  12: 'Dec', 
      } 
    },
    spec() {
      let config = {
          "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
          "padding": {'left': 60, 'top': 10, 'right': 70, 'bottom': 20},
          "config": {
              "bar": {
                "discreteBandSize": 24
              },
              "zero": false,
              "scale": {
                "nice": false,

              },
              "axis": {
                "tickRound": false
              }

          },
          "title": {
            "text": this.title,
            // "offset": 55
            "offset": 10,
            "fontSize": 3
          },
          "width": 1000,
          "height": 250,
          "layer": [ 
            {
              "transform": [
                {
                  "calculate": "datum.month + 0.155", "as": "loc_location"
                },
                
              ],
              "mark": {
                "type": "bar",
                "clip": "true"
              },
              "encoding": {
                  // "column": {
                  //   "field": "name", "type": "ordinal",
                  //   "scale": {"rangeStep": 12},
                  //   "axis": {"title": ""}
                  // },
                  "y": {
                    "field": "net_lines_minus_whitespace", "type": "quantitative",
                    "axis": {"title": "net loc","grid": false},
                    "scale": {
                      "domain": [-1000000, 1000000],
                      "nice": false,
                    }
                  },
                  "y2": {
                    "field": "avg_loc", "type": "quantitative","axis": {"title": "","grid": false},
                    "scale": {
                      "domain": [-1000000, 1000000],
                     "nice": false,
                    }
                  },
                  "x": {
                    "field": "loc_location", "type": 'quantitative',
                    // "field": "name", "type": "ordinal",
                    // "scale": {"rangeStep": 12},
                    "axis": {"title": "", "labels": false},
                    // "sort": {
                    //   "field": "net",
                    //   "op": "mean",
                    //   "order": "descending"
                    // },
                  },
                  "color": {
                    "value": "#FF3647"
                    // "field": "name", "type": "ordinal",
                    // "scale": {"range": ["black", "#CC0314", "#1403CC","#098118","#CCAE00","#C24F00","#5E0081","#0FA1C1","#BD00B3"]},

                  }
              },
            },
            {
              "transform": [
                {
                  "calculate": "datum.month - 0.155", "as": "commit_location"
                },

              ],
              "mark": {
                "type": "bar",
                "clip": "true"
              },
              "encoding": {
                  "y": {
                    "field": "avg_commits",
                    "axis": {"title": "commits","grid": false},
                    "scale": {
                      "domain": [-100, 100],
                      "nice": false,
                    }
                  },
                  "y2": {
                    "field": "commits", "type": "quantitative",
                    "axis": {"title": "commits","grid": false},
                    "scale": {
                      "domain": [-100, 100],
                      "nice": false,
                    }
                  },
                  "x": {
                    "field": "commit_location", "type": 'quantitative',
                    "axis": {"title": "", "labels": false},
                  },
                  "color": {
                    "value": "#4736FF",
                    // "field": "name", "type": "ordinal",
                    // "scale": {"range": ["#666666", "#FF697A", "#7A69FF","#6FE77E","#FFFF4C","#FFB564","#C451E7","#75FFFF","#FF65FF"]},
                    "legend": null
                  }
              },
            },
            {
              "transform": [
                {
                  "calculate": "datum.month", "as": "text_location"
                },
                {
                  "calculate": "-10", "as": "y"
                },
                
              ],
              "mark": {
                "type": "text",
                // "angle": 330
              },
              "encoding": {
                "text": {
                  "field": "month_name", "type": "nominal"
                },
                "y": {
                  "value": 270,
                  // "field": "y", "type": 'quantitative',
                  "axis": {
                    "title": "",
                    "grid": false
                  },
                  "scale": {
                      "domain": [-1000000, 1000000],
                      "nice": false,
                    }

                },
                "x": {
                  "field": "text_location", "type": 'quantitative',
                  "axis": {"title": "", "labels": false},
                },
                
              },
            },
            {
              "transform": [

              ],
              "mark": {
                "type": "rule",
              },
              "encoding": {

                "y": {
                  "aggregate": "mean",
                  "field": "commits",
                  "axis": {
                    "title": "","grid": false
                  },
                  "scale": {
                      "domain": [-100, 100],
                      "nice": false,
                    }
                },
                
              },
            },
            {
              "transform": [

              ],
              "mark": {
                "type": "rule",
              },
              "encoding": {

                "y": {
                  "aggregate": "mean",
                  "field": "net_lines_minus_whitespace",
                  "axis": null,
                  "scale": {
                      "domain": [-1000000, 1000000],
                      "nice": false,
                    }
                },
                
              },
            },
            {
              "transform": [

              ],
              "mark": {
                "type": "bar",
                "clip": "true"
              },
              "encoding": {

                "y": {
                  "aggregate": "mean",
                  "field": "net_lines_minus_whitespace",
                  "axis": null,
                  "scale": {
                      "nice": false,
                    },
                    
                },
                "opacity": {"value": 0},
                "color": {
                  "field": "key",
                  "type": "ordinal",
                  "scale": {"range": ["#4736FF", "#FF3647"]},
                  "legend": {"offset": -16}
                }
                
              },
            },

          ],
          "resolve": {"scale": {"y": "independent", "color": "independent"}},
      }
      // Get the repos we need
      let repos = []
      if (this.gitRepo) {
        repos.push(window.AugurAPI.Repo({ gitURL: this.gitRepo }))
      } // end if (this.$store.repo)

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
      if (this.data) {
        processGitData(this.data)
      } else {
        let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
        repo[this.source]().then((data) => {
          console.log("batch data", data)
          processData(data)
        }, () => {
          //this.renderError()
        }) // end batch request
      }
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
        let sum_commit = 0 
        let sum_loc = 0
        let max_loc = 0
        let max_commit = 0
        let min_loc = 0
        let min_commit = 0
        for (let i = 0; i < data.length; i++){
          sum_commit += data[i]['commits']
          sum_loc += data[i]['net_lines_minus_whitespace']
          console.log(i, data[i]['commits'], data[i]['net_lines_minus_whitespace'])
          data[i]['index'] = i
          if (data[i]['net_lines_minus_whitespace'] > max_loc)
            max_loc = data[i]['net_lines_minus_whitespace']
          if (data[i]['commits'] > max_commit)
            max_commit = data[i]['commits']
          if (data[i]['net_lines_minus_whitespace'] < min_loc){
            min_loc = data[i]['net_lines_minus_whitespace']
            console.log("min = ", data[i]['net_lines_minus_whitespace'])
          }
          if (data[i]['commits'] < min_commit)
            min_commit = data[i]['commits']
          if (i == 0)
            data[i].key = "commits"
          else
            data[i].key = "net lines changed"
          // data[i]['length'] = data[i]['name'].length
        }
        

        data.forEach((el) => {
          el.avg_commits = sum_commit / data.length
          el.avg_loc = sum_loc / data.length
          el.month_name = this.months[el.month]

        })
        

        // data.push({'upper_loc': max_loc })
        // data.push({'lower_loc': sum_loc / data.length - max_loc})
        let dif_loc = Math.abs(max_loc - sum_loc / data.length) > Math.abs(min_loc - sum_loc / data.length) ? Math.abs(max_loc - sum_loc / data.length) : Math.abs(min_loc - sum_loc / data.length)
        let dif_commit = Math.abs(max_commit - sum_commit / data.length) > Math.abs(min_commit - sum_commit / data.length) ? Math.abs(max_commit - sum_commit / data.length) : Math.abs(min_commit - sum_commit / data.length)
        console.log("HERE", sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc)
        config.layer[0].encoding.y.scale.domain  = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc]
        config.layer[0].encoding.y2.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc]
          config.layer[1].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit]
          config.layer[1].encoding.y2.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit]
          config.layer[2].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc]
          config.layer[3].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit]
          config.layer[4].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc]

        repos.forEach((repo) => {
          // let d = defaultProcess(data[repo], Object.keys(data[this.repo])[0])
          // d[0].repo = repo.gitURL ? repo.gitURL : repo.githubURL
          // this.values.push(d[0])
          // console.log("repo data", data)
          this.values = data
        })
      }
      return config
    },
  }
}
</script>