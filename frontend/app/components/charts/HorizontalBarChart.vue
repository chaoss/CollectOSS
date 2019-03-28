<template>
  <div ref="holder">
    <div class="normalbar">
      <!-- <vega-lite :spec="spec" :data="values"></vega-lite> -->
      <div :id="source"></div>
      <p> {{ chart }} </p>
      <div style="position: relative; top: -0px !important"class="form-item form-checkboxes tickradios">
          <div class="inputGroup ">
            <input id="totalradio" name="lines" value="1" type="radio" v-model="type">
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
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'measure'],
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
  mounted () {
    this.spec;
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
        "width": 450,
        "height": 300,
        "padding": {"left": 10, "top": 35, "right": 5, "bottom": 0},
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
          "offset": 15
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
              
            },
            "encoding": {
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
            }
            
            
          },
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
      let changes = null

      if (this.data)
        changes = this.data
      else changes = repo.changesByAuthor()

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

      $(this.$el).find('.showme, .hidefirst').removeClass('invis')
      $(this.$el).find('.stackedbarchart').removeClass('loader')

      // Get the repos we need
      let repos = []
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo])
      }

      this.reloadImage(config)

      return config

    }
  },
  methods: {
    reloadImage (config) {
      config.data = {"values": this.values}
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -100, offsetX: 40}, mode: 'vega-lite'}) 
    }
  }
  
}

</script>
