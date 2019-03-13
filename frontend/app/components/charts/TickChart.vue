<template>
  <div ref="holder" style="position: relative; z-index: 5">
    <div class="tickchart">
      <h3 style="text-align: center">Lines of code added by the top 10 authors visualized</h3>
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
      <!-- <p class="note">*point values with total lines changed outside the bounds of [50.000, 1.000.000] are rounded to the corresponding edge limit</p> -->
      <div class="form-item form-checkboxes tickradios" style="transform: translateY(-35px) !important">


          <div class="inputGroup" >
            <input id="circradio" name="comparebaseline" value="0" type="radio" v-model="tick">
            <label id="front" for="circradio">Circle</label>
          </div>
          <div class="inputGroup ">
            <input id="tickradio"name="comparebaseline" value="1" type="radio" v-model="tick">
            <label id="front" for="tickradio">Tick</label>
          </div>
          <div class="inputGroup ">
            <input id="rectradio"name="comparebaseline" value="2" type="radio" v-model="tick">
            <label id="front" for="rectradio">Rectangle</label>
          </div>

        
      </div>
      
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
        "width": 950,
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
             
              {
                "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
                "as": "Majority type of changes"
              },
              {
                "calculate": "(datum.additions - datum.deletions)",
                "as": "Net lines added"
              },
              {
                "calculate": "(datum.additions + datum.deletions) < 50000 ? 50000 : ((datum.additions + datum.deletions) > 1000000 ? 1000000 : (datum.additions + datum.deletions))",
                "as": "Total lines changed"
              },
            ],
            "mark": type,
            "encoding": {
              "x": {"field": "author_date", "type": "temporal", "bin": bin, "axis": {"format": "%b %Y", "title": " "}},
              "y": {"field": "author_email", "type": "nominal"},
              "color": {
                "field": "Net lines added",
                "type": "quantitative",
                "scale": { "range": ["#FF0000", "#00FF00"]}
              },
              "size": size,
              "opacity": opacity

            },
            
          }
        ]
        
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

      repo.changesByAuthor().then((changes) => {
        changes.forEach((change) => {
          change.author_date = new Date(change.author_date)
        })

        changes.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates)
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates)
            }
          }
        })
        

        //this.values = flattenAndSort(contributors, 'author_email', 'additions')
        //this.organizations = flattenAndSort(organizations, 'name', 'additions')
        this.contributors = flattenAndSort(contributors, 'author_email', 'additions')
        var careabout = []
        this.contributors.slice(0,10).forEach((obj) => {
          careabout.push(obj["author_email"])
        })



        let findObjectByKey = (array, key, value) => {
            let ary = []
            for (var i = 0; i < array.length; i++) {
                if (array[i][key] == value) {
                    ary.push(array[i]);
                }
            }
            return ary;
        }


        var ary = []
        
        careabout.forEach((name) => {
          findObjectByKey(changes, "author_email", name).forEach((obj) => {
            ary.push(obj)
          })
          // changes.find(obj => obj.author_email == name))
        })
      
        this.values = ary

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

      let processData = (data) => {
        // // We usually want to limit dates and convert the key to being vega-lite friendly
        // let defaultProcess = (obj, key, field, count) => {
        //   let d = AugurStats.convertKey(obj[key], field)
        //   return AugurStats.convertDates(d, this.earliest, this.latest)
        // }

        // // Normalize the data into [{ date, value },{ date, value }]
        // // BuildLines iterates over the fields requested and runs onCreateData on each
        // let normalized = []
        // let buildLines = (obj, onCreateData) => {
        //   if (!obj) {
        //     return
        //   }
        //   if (!onCreateData) {
        //     onCreateData = (obj, key, field, count) => {
        //       let d = defaultProcess(obj, key, field, count)
        //       normalized.push(d)
        //     }
        //   }
        //   let count = 0
        //   for (var key in obj) {
        //     if (obj.hasOwnProperty(key)) {
        //       if (fields[key]) {
        //         fields[key].forEach((field) => {
        //           onCreateData(obj, key, field, count)
        //           count++
        //         })
        //       } else {
        //         if (Array.isArray(obj[key]) && obj[key].length > 0) {
        //           let field = Object.keys(obj[key][0]).splice(1)
        //           onCreateData(obj, key, field, count)
        //           count++
        //         } else {
        //           this.renderError()
        //           return
        //         }
        //       }
        //     } // end hasOwnProperty
        //   } // end for in
        // } // end normalize function

        // let values = []

        // buildLines(data[this.repo], (obj, key, field, count) => {
        //   // Build basic chart
        //   normalized.push(defaultProcess(obj, key, field, count))
        // })

        // if (normalized.length == 0) {
        //   this.renderError()
        // } else {
        //     for(var i = 0; i < normalized.length; i++){
        //       normalized[i].forEach(d => {
        //         //d.name = legend[i]
        //         //d.color = colors[i]
        //         values.push(d);
        //       })
        //     }
        //   }

        // $(this.$el).find('.showme, .hidefirst').removeClass('invis')
        // $(this.$el).find('.stackedbarchart').removeClass('loader')
        // this.values = values
      }

      // if (this.data) {
      //   processData(this.data)
      // } else {
      //   window.AugurAPI.batchMapped(repos, endpoints).then((data) => {
      //     processData(data)
      //   })
      // }



      return config

    }
  }
  
}

</script>
