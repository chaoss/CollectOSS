<template>
  <div ref="holder">
    <div class="tickchart ">
      <h3>Contributions By Time Interval for 2018</h3>
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>

      
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
  data() {
    let years = []
    for (let i = 9; i >= 0; i--) {
      years.push((new Date()).getFullYear() - i)
    }
    let monthNames = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    let monthDecimals = [1,2,3,4,5,6,7,8,9,10,11,12];
    return {
      values: [],
      contributors: [],
      organizations: [],
      view: 'year',
      monthNames: monthNames,
      monthDecimals: monthDecimals,
      years: years,
      setYear: 0,
      tick: 0
    }
  },
  created () {
    this.tick = 0
  },
  computed: {
    repo() {
      return this.$store.state.gitRepo
    },
    earliest () {
      return this.$store.state.startDate
    },
    latest () {
      return this.$store.state.endDate
    },
    spec() {
      let type = null, bin = null, size = null, opacity = null;

      if(this.tick == 0) {
        type = "circle"
        bin = false
        size = {
                "field": "Total lines changed",
                "type": "quantitative",
                "min": "15",
                "scale": {"minSize": 30, "maxSize": 31}
              }
        opacity = {}
      }
      if (this.tick == 1) {
        type = "tick"
            bin = false
            size = {}
        opacity = {
                "field": "Total lines changed",
                "type": "quantitative",
                "min": ".5"
              }
      }
      if (this.tick == 2) {
        type = "rect"
            bin = {"maxbins": 40}
            size = {}
        opacity = {
                "field": "Total lines changed",
                "type": "quantitative",
                "min": ".5"
              }
      }


      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 800,
        "height": 300,
        "config": {
          "tick": {
            "thickness": 8,
            "bandSize": 23
          },
          "axis":{
                "grid": false,
                "title": null
              },
              "legend": {
               // "offset": -505,
                "titleFontSize": 10,
                "titlePadding": 10
              },"scale": {"minSize": 100, "maxSize": 500}
        },
        "layer": [
          {
            "transform": [
              // {"filter": {"timeUnit": "date", "field": "date", "equal": "1"}}                          
            ],
            "mark": "bar",
            "encoding": {
              "y": {
                "field": "commits", "type": "quantitative",
                "axis": {"grid": false}
              },
              "x": {
                "field": "month", "type": "temporal",
                "axis": {"title": ""}
              },
              "color": {
                "value": "red"
              }
            }
          },
          {
            "transform": [
              {
                "window": [{
                  "op": "sum",
                  "field": "commits",
                  "as": "avg_commits"
                }]
              }
            ],
            "mark": "text",
            "encoding": {
              "text": {"field": "avg_commits", "type": "quantitative"},
              "y": {"value": 10},
              "x": {
                "field": "month", "type": "temporal",
                "axis": {"title": ""}
              },
              "color": {
                "value": "black"
              }
            }
          },
          {
            "transform": [
              // {"filter": {"timeUnit": "date", "field": "date", "equal": "6"}}
            ],
            "mark": "bar",
            "encoding": {
              "y": {
                "field": "rate", "type": "quantitative",
                "axis": {"grid": false}
              },
              "x": {
                "field": "month", "type": "temporal",
                "axis": {"title": ""}
              },
              "color": {
                "value": "blue"
              }
            }
          }
          
        ],
        "resolve": {"scale": {"y": "independent"}},
        "config": {
          "view": {"stroke": "transparent"},
          "axis": {"domainWidth": 1}
        }
        
      }

      let repo = window.AugurAPI.Repo({ gitURL: this.repo })
      let contributors = {}
      let organizations = {}

      let addChanges = (dest, src) => {
        if (dest && src) {
          if (typeof dest !== 'object') {
            dest['additions'] = 0
            dest['deletions'] = 0
          }
          dest['additions'] += (src['additions'] || 0)
          dest['deletions'] += (src['deletions'] || 0)
        }
      }

      let group = (obj, name, change, filter) => {
        if (filter(change)) {
          let year = (new Date(change.author_date)).getFullYear()
          let month = (new Date(change.author_date)).getMonth()
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 }
          addChanges(obj[change[name]], change)
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 }
          addChanges(obj[change[name]][year], change)
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 }
          addChanges(obj[change[name]][year + '-' + month], change)
        }
      }

      let flattenAndSort = (obj, keyName, sortField) => {
        return Object.keys(obj)
            .map((key) => {
              let d = obj[key]
              d[keyName] = key
              return d
            })
            .sort((a, b) => {
              return b[sortField] - a[sortField]
            })
      }

      let filterDates = (change) => {
        return (new Date(change.author_date)).getFullYear() > this.years[0]
      }

      repo.cdRepTpIntervalLocCommits().then((changes) => {
        console.log("CHANGE", changes)
        // changes.forEach((change) => {
        //   change.author_date = new Date(change.author_date)
        // })

        // changes.forEach((change) => {
        //   if (isFinite(change.additions) && isFinite(change.deletions)) {
        //     group(contributors, 'author_email', change, filterDates)
        //     if (change.author_affiliation !== 'Unknown') {
        //       group(organizations, 'affiliation', change, filterDates)
        //     }
        //   }
        // })
        
        // this.contributors = flattenAndSort(contributors, 'author_email', 'additions')
        // var careabout = []
        // this.contributors.slice(0,10).forEach((obj) => {
        //   careabout.push(obj["author_email"])
        // })



        // let findObjectByKey = (array, key, value) => {
        //     let ary = []
        //     for (var i = 0; i < array.length; i++) {
        //         if (array[i][key] == value) {
        //             ary.push(array[i]);
        //         }
        //     }
        //     return ary;
        // }


        // var ary = []
        
        // careabout.forEach((name) => {
        //   findObjectByKey(changes, "author_email", name).forEach((obj) => {
        //     ary.push(obj)
        //   })
        //   // changes.find(obj => obj.author_email == name))
        // })
      
        // this.values = ary
        this.values = changes
      })
        


      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
      $(this.$el).find('.stackedbarchart').removeClass('loader')

      // let endpoints = []
      // let fields = {}
      // this.source.split(',').forEach((endpointAndFields) => {
      //   let split = endpointAndFields.split(':')
      //   endpoints.push(split[0])
      //   if (split[1]) {
      //     fields[split[0]] = split[1].split('+')
      //   }
      // })

      // Get the repos we need
      let repos = []
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo])
      }


      return config

    }
  }
  
}

</script>
