<!-- #SPDX-License-Identifier: MIT -->
<template>

  

<!-- <<<<<<< Updated upstream -->
  <div class="normalizedStackedDiv1 tickchart">
    <!-- <div :id="source" style="padding: 0"></div> -->
    <vega-lite :spec="spec" :data="values"></vega-lite>
    <!-- <div style="position: relative; top: -0px !important; transform: translateY(-0rem)"class="form-item form-checkboxes tickradios">
        <div class="inputGroup "  style="padding-top: 5px;">
          <input id="yearradio" name="timeframe" value="0" type="radio" v-model="group">
          <label id="front" for="yearradio" >Year</label>
        </div>
        <div class="inputGroup "  style="padding-top: 5px;">
          <input id="monthradio" name="timeframe" value="1" type="radio" v-model="group">
          <label id="front" for="monthradio" >Month</label>
        </div>
        <div class="inputGroup " style="padding-top: 5px;">
          <input id="contradio" name="timeframe" value="2" type="radio" v-model="group">
          <label id="front" for="contradio">Continuous</label>
        </div>
    </div> -->
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
      group: 1,
      x: 0,
      y: 0
    }
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
      console.log("HEY")
      let type = null, bin = null, size = null, timeUnit = null, format = null;

      if(this.group == 0) {
        timeUnit = 'year'
        format = '%Y'
        type = "bar"
        bin = false
        size = 30
      }
      if (this.group == 1) {
        timeUnit = 'yearmonth'
        format = '%y %b'
        type = "bar"
            bin = false
            size = 13
      }
      if (this.group == 2) {
        timeUnit = 'yearmonth'
        format = '%y %b'
            bin = false
            size = 13
        type = "area"
      }


      var colors = ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
      let config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": this.x / 2.5,
        "height": this.y / 3,
        "padding": {"left": 0, "top": 0, "right": 0, "bottom": -70},
        "config": {
          "axis":{
                "grid": false
              },
          "legend": {
            "offset": -0,
            "orient": "bottom",
            "titlePadding": 10,
            "padding": 20,
            "labelFontSize": 16,
            // "labelFont": "Open Sans",
            "labelOffset": 3,
            "titleFontSize": 18,
            "labelLimit": 460 
          },
          // "scale": {"minSize": 100, "maxSize": 500},
          "bar": {
            "continuousBandSize": size,
            "binSpacing": 0,
          }
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
                "calculate": "(datum.additions + datum.deletions)",
                "as": "Total lines changed"
              },
              {
                "calculate": "(datum.count * 100)",
                "as": "percent"
              },
            ],
            
            "mark": {
              "type": type,
              
              "cornerRadius": 1
            },
            "encoding": {
              "x": {
                "field": "cmt_author_date", 
                "type": "temporal", 
                "timeUnit": timeUnit, 
                "axis": {"domain": false, "format": format}
              },
              "y": {
                "field": "count", 
                "type": "quantitative",
                "aggregate": "sum",
                "stack": "center",
                "axis": null,
              },
              "color": {
                "field": "cmt_author_email",
                "type": "nominal",
                "scale": {"scheme": "category10"}
              },
              
            },
          },
          {
            "mark": {
              "type": type,
              
              "cornerRadius": 1
            },
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
                "calculate": "(datum.additions)",// + datum.deletions)",
                "as": "Total lines added"
              },
              {
                "calculate": "(datum.count * 100)",
                "as": "percent"
              },
            ],
            "selection": {
              "tooltip": {
                "type": "multi",
                "on": "mouseover",
                "nearest": false,
                "empty": "none",
                "fields": ["_vgsid_"],
                "toggle": "event.shiftKey",
                "resolve": "global"
              }
            },

            "encoding": {
              "opacity": {"value": 1.001},
              "x": {
                "field": "cmt_author_date", 
                "type": "temporal", 
                "timeUnit": timeUnit, 
                "axis": {"domain": false, "format": format}
              },
              "y": {
                "field": "count", 
                "type": "quantitative",
                "aggregate": "sum",
                "stack": "center",
                "axis": null,
              },
              "tooltip": [{
                "aggregate": "sum",
                "field": "Total lines added",
                "type": "quantitative"
              },{
                "aggregate": "sum",
                "field": "Net lines added",
                "type": "quantitative"
              },{
                "field": "cmt_author_date", 
                "type": "temporal", 
                "timeUnit": timeUnit
              },{
                "field": "cmt_author_email",
                "type": "nominal",
              }],
              "color": {
                "condition":{
                  "selection": {"not": "tooltip"}, "value": "transparent"
                },
                // "value": "black"
                "value": "transparent"
              }
            }
          }
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

      let authors = []
      let track = {"total": 0}

      let changes = null
      if (this.data) changes = this.data
      else changes = repo.changesByAuthor()
      
        changes.forEach((change) => {
          change.cmt_author_date = new Date(change.cmt_author_date)
          change["count"] = change["count"] ? change["count"] + 1 : 1
          track[change.cmt_author_email] = track[change.cmt_author_email] ? track[change.cmt_author_email] + 1 : 1
          track["total"] += 1
        })

        changes.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'cmt_author_email', change, filterDates)
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates)
            }
          }
          if(!authors.includes(change["cmt_author_email"])) {
            authors.push(change["cmt_author_email"])
            change["flag"] = (track[change.cmt_author_email] / track["total"]).toFixed(4)
          } //else change["flag"] = 100

          
        })
        
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
          findObjectByKey(changes, "cmt_author_email", name).forEach((obj) => {
            ary.push(obj)
          })
        })
      
        this.values = ary

      
      // Get the repos we need
      let repos = []

      this.reloadImage(config)
      return config

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
  methods: {
    reloadImage (config) {
      config.data = {"values": this.values}
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -100, offsetX: 40}, mode: 'vega-lite',}) 
    }
  }
  
}

</script>
