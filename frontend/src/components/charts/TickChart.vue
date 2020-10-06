<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div>
      <div :id="source"></div>
      <vega-lite :spec="spec" :data="values"></vega-lite>
      <!-- <p class="note">*point values with total lines changed outside the bounds of [50.000, 1.000.000] are rounded to the corresponding edge limit</p> -->
      <!-- <div class="form-item form-checkboxes tickradios" class="tickChartDiv">


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
       -->
  </div>
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
import vegaEmbed from 'vega-embed'

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
      tick: 0,
      x:0,
      y:0
    }
  },
  mounted() {
    var win = window,
      doc = document,
      docElem = doc.documentElement,
      body = doc.getElementsByTagName('body')[0],
      x = win.innerWidth || docElem.clientWidth || body.clientWidth,
      y = win.innerHeight|| docElem.clientHeight|| body.clientHeight;
    this.x = x
    this.y = y
    this.spec;
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo
    },
    gitRepo() {
      return this.$store.state.gitRepo
    },
    earliest () {
      return this.$store.state.startDate
    },
    latest () {
      return this.$store.state.endDate
    },
    spec() {
      console.log("test")
      const vegaEmbed = window.vegaEmbed;
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
        "width": this.x / 1.5,
        "height": this.y / 2.4,
        "padding": {"left": -10, "top": 0, "right": 5, "bottom": 10},
        "config": {
          "tick": {
            "thickness": 8,
            "bandSize": 23
          },
          "axis":{
            "grid": false,
            "title": null,
            'labels': {
              'labelFontSize': 20
            },
          },
          "legend": {
           // "offset": -505,
            "titleFontSize": 10,
            "titlePadding": 10
          },
          "scale": {"minSize": 100, "maxSize": 500}
        },
        "layer": [
          {
            "transform": [
             
              // {
              //   "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
              //   "as": "Majority type of changes"
              // },
              // {
              //   "calculate": "(datum.additions - datum.deletions)",
              //   "as": "Net lines added"
              // },
              // {
              //   "calculate": "(datum.additions + datum.deletions) < 0000 ? 0000 : ((datum.additions + datum.deletions) > 100000000 ? 100000000 : (datum.additions + datum.deletions))",
              //   "as": "Total lines changed"
              // },
            ],
            "mark": type,
            
            "encoding": {
              "x": {"field": "cmt_author_date", "type": "temporal", "bin": bin, "axis": {"format": "%b %Y", "title": " "}},
              "y": {"field": "cmt_author_email", "type": "nominal"},
              "color": {
                "field": "Net lines added",
                "type": "quantitative",
                "scale": { "range": ["#FF0000", "#00FF00"]}
              },
              
              "size": size,
              "opacity": opacity
            },
            
          },
          // {
          //   "mark": "rule",
          //   "transform": [
          //     {
          //       "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
          //       "as": "Majority type of changes"
          //     },
          //     {
          //       "calculate": "(datum.additions - datum.deletions)",
          //       "as": "Net lines added"
          //     },
          //     {
          //       "calculate": "(datum.additions + datum.deletions) < 0000 ? 0000 : ((datum.additions + datum.deletions) > 1000000000 ? 1000000000 : (datum.additions + datum.deletions))",
          //       "as": "Total lines changed"
          //     },
          //   ],
            // "selection": {
            //   "tooltip": {"type": "multi", "on": "mouseover","nearest": false, "empty": "none"}
            // },
            // "encoding": {
            //   "size": {"value": 8},
            //   "opacity": {"value": 1.051},
            //   "x": {"field": "cmt_author_date", "type": "temporal"},              
              // "tooltip": [{"field": "cmt_author_email", "type": "nominal"},{
              //   "field": "Total lines changed",
              //   "type": "quantitative",
              // },
              // {
              //   "field": "Net lines added",
              //   "type": "quantitative",
              // }],
              // "color": {
                // "condition":{
                  // "selection": {"not": "tooltip"}, 
                  // "value": "transparent"
                // }
              // }
            // }
          // }
        ]
        
      }
      let repo = null

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
          let year = (new Date(change.cmt_author_date)).getFullYear()
          let month = (new Date(change.cmt_author_date)).getMonth()
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
        return (new Date(change.cmt_author_date)).getFullYear() > this.years[0]
      }
      let processData = (data) => {
        data.forEach((change) => {
          change.cmt_author_date = new Date(change.cmt_author_date)
        })
        data.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'cmt_author_email', change, filterDates)
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates)
            }
          }
        })
        
        //this.values = flattenAndSort(contributors, 'cmt_author_email', 'additions')
        //this.organizations = flattenAndSort(organizations, 'name', 'additions')
        this.contributors = flattenAndSort(contributors, 'cmt_author_email', 'additions')
        var careabout = []
        this.contributors.slice(0,10).forEach((obj) => {
          careabout.push(obj["cmt_author_email"])
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
          findObjectByKey(data, "cmt_author_email", name).forEach((obj) => {
            ary.push(obj)
          })
          // changes.find(obj => obj.cmt_author_email == name))
        })
      
        this.values = ary
      }
      if (this.data) {
        processData(this.data)
      } else {
        repo.changesByAuthor().then((changes) => {
          processData(changes)
        })
      }
      // Get the repos we need
      let repos = []
      if (this.repo) {
      }
      this.reloadImage(config)
      return config
    }
  },
  methods: {
    reloadImage (config) {
      console.log("TICK",this.values, config)
      config.data = {"values": this.values}
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -110}, mode: 'vega-lite',}) 
    }
  }
}
</script>