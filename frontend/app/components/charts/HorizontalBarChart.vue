<template>
  <div ref="holder">
    <div class="normalbar">
      <!-- <h3>Lines of code added by the top 10 authors as Percentages - All Time</h3> -->
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <p> {{ chart }} </p>
      <div style="position: relative; top: -60px !important"class="form-item form-checkboxes tickradios">

          
          <div class="inputGroup ">
            <input id="totalradio" name="lines" value="1" type="radio" checked v-model="type">
            <label id="front" for="totalradio">Total</label>
          </div>
          <div class="inputGroup ">
            <input id="netradio" name="lines" value="0" type="radio" v-model="type">
            <label id="front" for="netradio">Net</label>
          </div>
          <div class="inputGroup ">
            <input id="addedradio" name="lines" value="2" type="radio" v-model="type">
            <label id="front" for="addedradio">Added</label>
          </div>
          
          

        
      </div>
    </div>
  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from 'AugurStats'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'type'],
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
      tick: 0,
      type: 1
    }
  },
  created () {
    this.type = 1
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

      // let init = () => {
      //   let type;
      //   switch(this.tick) {
      //     case 0: //circle
      //       type = "circle"
      //       // bin = false
      //       // size = {
      //       //         "field": "total",
      //       //         "type": "quantitative",
      //       //         "min": "15"
      //       //       }
      //       break
      //     case 1: //tick
      //       type = "tick"
      //       // bin = false
      //       // size = {}
      //       break
      //     case 2: //rect
      //       type = "rect"
      //       // bin = {"maxbins": 40}
      //       // size = {}
      //     default:
      //       break
      //   }
      //   return type
      // }
      
      let field = null;


      if (this.type == 0) {
        field = "netratio"
      } else if (this.type == 1) {
        field = "totalratio"
      } else if (this.type == 2) {
        field = "addedratio"
      }

      var colors = ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 700,
        "height": 310,
        "config": {
          "tick": {
            "thickness": 8,
            "bandSize": 23
          },
          "axis":{
            "grid": false
          },
        },
        "title": {
          "text": this.title,
          "offset": 15,
          
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
                "calculate": "((datum.additions - datum.deletions) / datum.commits)",
                "as": "netratio"
              },
              {
                "calculate": "(datum.additions / datum.commits)",
                "as": "addedratio"
              },
              {
                "calculate": "(datum.lines / datum.commits)",
                "as": "totalratio"
              },
            ],
            "mark": {
              "type":"bar",
              "tooltip": {"content": "data"}
            },
            "encoding": {
              // "y": {"field": "author_date", "type": "temporal", "bin": true, "axis": {"format": "%b %Y", "title": " "}},
              "x": {"field": field, "type": "quantitative"},
              "y": {
                "field": "author_email",
                "sort": {
                  "field": field,
                  "op": "mean",
                  "order": "descending"
                },
                "type": "nominal",
                "axis": {"title": null}
              },
              "color": {
                "field": "author_email",
                "type": "nominal",
                "scale": {"scheme": "category10"},
                "legend": null
              },
              // "size": size,
              // "opacity":{
              //   "field": "Total lines changed",
              //   "type": "quantitative",
              //   "min": ".5"
              // },
            }
            
            
          },
          // {
          //   "mark": {
          //     "type": "text",
          //     "dx": -15,
          //     "dy": -15
          //   },
          //   "encoding": {
          //     // "x": {"field": "author_date", "type": "temporal", "axis": {"format": "%b %Y", "title": " "}},
          //     "x": {"field": "flag", "type": "quantitative","stack": "normalize"},
          //     "color": {
          //       "field": "author_email",
          //       "type": "nominal",
          //       "scale": { "range": colors}
          //     },
          //     "text":{
          //       "field": "flag",
          //       "type": "quantitative",

          //     },

          //   },
          // }
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

      let authors = []
      let track = {}
      repo.changesByAuthor().then((changes) => {
        changes.forEach((change) => {
          // change.author_date = new Date(change.author_date)
          // change["commits"] = change["commits"] ? change["commits"] + 1 : 1
          track[change.author_email] = track[change.author_email] ? track[change.author_email] : {'commits': 0, 'lines': 0, 'additions': 0, 'deletions': 0}
          track[change.author_email]['commits'] = track[change.author_email]['commits'] ? track[change.author_email]['commits'] + 1 : 1
          // track["total_commits"] += 1
          // change["lines"] = change["lines"] ? change["lines"] + change.additions : change.additions
          track[change.author_email]['lines'] = track[change.author_email]['lines'] ? track[change.author_email]['lines'] + change.additions + change.deletions : change.additions + change.deletions
          track[change.author_email]['additions'] = track[change.author_email]['additions'] ? track[change.author_email]['additions'] + change.additions : change.additions
          track[change.author_email]['deletions'] = track[change.author_email]['deletions'] ? track[change.author_email]['deletions'] + change.deletions : change.deletions
          // track["total_lines"] += change.additions
        })

        changes.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates)
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates)
            }
          }
          if(!authors.includes(change["author_email"])) {
            authors.push(change["author_email"])
            change["flag"] = ((track[change.author_email] / track["total"] * 100).toFixed(4))
            // console.log(change, track)
          } //else change["flag"] = 100

          
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
        
        for (var key in track) {
          if (careabout.includes(key))
            ary.push({"author_email": key, "commits": track[key]['commits'], "lines": track[key]['lines'], "additions": track[key]['additions'], "deletions": track[key]['deletions']})
        }
      

        this.values = ary
        console.log("TRACK", ary, careabout)
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
