<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder">
    <div class="tickchart ">
      <h3>Lines of code added by the top 10 authors visualized</h3>
      <div :id="source"></div>
      <p> {{ chart }} </p>
      <div class="form-item form-checkboxes tickradios">
        <div class="inputGroup ">
          <input id="circradio" name="comparebaseline" value="0" type="radio" v-model="tick">
          <label id="circradio_front" for="circradio">Circle</label>
        </div>
        <div class="inputGroup ">
          <input id="tickradio" name="comparebaseline" value="1" type="radio" v-model="tick">
          <label id="tickradio_front" for="tickradio">Tick</label>
        </div>
        <div class="inputGroup ">
          <input id="rectradio" name="comparebaseline" value="2" type="radio" v-model="tick">
          <label id="rectradio_front" for="rectradio">Rectangle</label>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
  export default {
    props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
    data() {
      let years = [];
      for (let i = 9; i >= 0; i--) {
        years.push((new Date()).getFullYear() - i)
      }
      let monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      let monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
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
        care: []
      }
    },
    mounted() {
      this.spec;
    },
    computed: {
      repo() {
        return this.$store.state.baseRepo
      },
      gitRepo() {
        return this.$store.state.gitRepo
      },
      earliest() {
        return this.$store.state.startDate
      },
      latest() {
        return this.$store.state.endDate
      },
      spec() {
        let [type, bin, size, opacity] = Array(4).fill(null);

        if (this.tick == 0) {
          type = "circle";
          bin = false;
          size = {
            "field": "Total lines changed",
            "type": "quantitative",
            "min": "15",
            "scale": {"minSize": 30, "maxSize": 31}
          };
          opacity = {}
        }
        if (this.tick == 1) {
          type = "tick";
          bin = false;
          size = {};
          opacity = {
            "field": "Total lines changed",
            "type": "quantitative",
            "min": ".5"
          }
        }
        if (this.tick == 2) {
          type = "rect";
          bin = {"maxbins": 40};
          size = {};
          opacity = {
            "field": "Total lines changed",
            "type": "quantitative",
            "min": ".5"
          }
        }

        let config = {
          // "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
          "width": 1000,
          "height": 360,
          "padding": {"left": -10, "top": 35, "right": 5, "bottom": -18},
          "config": {
            "tick": {
              "thickness": 8,
              "bandSize": 23
            },
            "axis": {
              "grid": false,
              "title": null
            },
            "legend": {
              // "offset": -505,
              "titleFontSize": 10,
              "titlePadding": 10
            }, "scale": {"minSize": 100, "maxSize": 500}
          },

          "layer": [
            {
              "transform": [
                {
                  "calculate": "datetime((datum.year),(datum.month),1)",//month(datum.author_date)+1
                  "as": "Current month"
                },
                {
                  "calculate": "datetime((datum.year),(datum.month)+1,1)",//month(datum.author_date)+1
                  "as": "Next month"
                },
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

                "x": {
                  "field": "author_date",
                  "type": "temporal",
                  "bin": bin,
                  "axis": {"format": "%b %Y", "title": " "}
                },
                "y": {"field": "author_email", "type": "nominal"},
                "color": {
                  "field": "Net lines added",
                  "type": "quantitative",
                  "scale": {"range": ["#FF0000", "#00FF00"]}
                },

                "size": size,
                "opacity": opacity

              },

            },
            {
              "mark": "rect",
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
                  "calculate": "0",
                  "as": "zero"
                },
                {
                  "calculate": "1000",
                  "as": "thousand"
                },
                {
                  "calculate": "datetime((datum.year),(datum.month),1)",//month(datum.author_date)+1
                  "as": "Current month"
                },
                {
                  "calculate": "datetime((datum.year),(datum.month)+1,1)",//month(datum.author_date)+1
                  "as": "Next month"
                },
                {
                  "calculate": "(datum.additions + datum.deletions) < 50000 ? 50000 : ((datum.additions + datum.deletions) > 1000000 ? 1000000 : (datum.additions + datum.deletions))",
                  "as": "Total lines changed"
                },
              ],
              "selection": {
                "tooltip": {"type": "multi", "on": "mouseover", "nearest": false, "empty": "none"}
              },
              "encoding": {
                "opacity": {"value": 1.051},
                "x": {"field": "Current month", "type": "temporal"},
                "x2": {"field": "Next month", "type": "temporal"},
                "y": {"field": "zero", "type": "quantitative", "axis": {"title": "", "labels": false},},
                "y2": {"field": "thousand", "type": "quantitative", "axis": {"title": "", "labels": false},},

                "tooltip": [{"field": this.care[0], "type": "nominal"},
                  {"field": this.care[1], "type": "nominal"},
                  {"field": this.care[2], "type": "nominal"},
                  {"field": this.care[3], "type": "nominal"},
                  {"field": this.care[4], "type": "nominal"},
                  {"field": this.care[5], "type": "nominal"},
                  {"field": this.care[6], "type": "nominal"},
                  {"field": this.care[7], "type": "nominal"},
                  {"field": this.care[8], "type": "nominal"}, {
                    "field": "Total lines changed",
                    "type": "quantitative",
                  }, {
                    "field": "Net lines added",
                    "type": "quantitative",
                  }],
                "color": {
                  "condition": {
                    "selection": {"not": "tooltip"}, "value": "transparent"
                  }
                }
              }
            },
          ]
        };

        let repo = null;
        if (this.repo) {
          if (window.AugurRepos[this.repo]) {
            repo = window.AugurRepos[this.repo]
          } else {
            let repo = window.AugurAPI.Repo({"gitURL": this.gitRepo});
            window.AugurRepos[repo.toString] = repo
          }
        } else {
          repo = window.AugurAPI.Repo({gitURL: this.gitRepo});
          window.AugurRepos[repo.toString()] = repo
        }

        let contributors = {};
        let organizations = {};

        let addChanges = (dest, src) => {
          if (dest && src) {
            if (typeof dest !== 'object') {
              dest['additions'] = 0;
              dest['deletions'] = 0
            }
            dest['additions'] += (src['additions'] || 0);
            dest['deletions'] += (src['deletions'] || 0)
          }
        };

        let group = (obj, name, change, filter) => {
          if (filter(change)) {
            let year = (new Date(change.author_date)).getFullYear();
            let month = (new Date(change.author_date)).getMonth();
            obj[change[name]] = obj[change[name]] || {additions: 0, deletions: 0};
            addChanges(obj[change[name]], change);
            obj[change[name]][year] = obj[change[name]][year] || {additions: 0, deletions: 0};
            addChanges(obj[change[name]][year], change);
            obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || {
              additions: 0,
              deletions: 0
            };
            addChanges(obj[change[name]][year + '-' + month], change)
          }
        };

        let flattenAndSort = (obj, keyName, sortField) => {
          return Object.keys(obj)
            .map((key) => {
              let d = obj[key];
              d[keyName] = key;
              return d
            })
            .sort((a, b) => {
              return b[sortField] - a[sortField]
            })
        };

        let filterDates = (change) => {
          return (new Date(change.author_date)).getFullYear() > this.years[0]
        };

        let processData = (data) => {

          data.forEach((change) => {
            change.author_date = new Date(change.author_date)
          });

          data.forEach((change) => {
            if (isFinite(change.additions) && isFinite(change.deletions)) {
              group(contributors, 'author_email', change, filterDates);
              if (change.author_affiliation !== 'Unknown') {
                group(organizations, 'affiliation', change, filterDates)
              }
            }
          });
          this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
          let careAbout = [];
          this.contributors.slice(0, 10).forEach((obj) => {
            careAbout.push(obj["author_email"])
          });

          let findObjectByKey = (array, key, value) => {
            let ary = [];

            for (let i = 0; i < array.length; i++) {
              if (array[i][key] == value) {
                ary.push(array[i]);
              }
            }
            return ary;
          };

          let ary = [];
          careAbout.forEach((name) => {
            findObjectByKey(data, "author_email", name).forEach((obj) => {
              let found = ary.some(function (el) {
                return el.year == obj.author_date.getFullYear() && el.month == obj.author_date.getMonth()
              });
              if (!found) {
                ary.push({
                  year: obj.author_date.getFullYear(),
                  month: obj.author_date.getMonth(),
                  additions: 0,
                  whitespace: 0,
                  deletions: 0
                });
              } else {
                let el = ary.find(function (el) {
                  return el.year == obj.author_date.getFullYear() && el.month == obj.author_date.getMonth()
                });
                if (!Object.keys(el).includes(obj.author_email)) {
                  el[obj.author_email] = "additions: " + obj.additions;
                  if (!this.care.includes(obj.author_email)) {
                    this.care.push(obj.author_email)
                  }
                }
                el.additions += obj.additions;
                el.deletions += obj.deletions;
                el.whitespace += obj.whitespace
              }
              ary.push(obj)
            })
          });

          this.values = ary

        };

        if (this.data) {
          processData(this.data)
        } else {
          repo.changesByAuthor().then((changes) => {
            processData(changes)
          })
        }

        $(this.$el).find('.showme, .hidefirst').removeClass('invis');
        $(this.$el).find('.stackedbarchart').removeClass('loader');

        // Get the repos we need
        let repos = [];
        if (this.repo) {
          repos.push(window.AugurRepos[this.repo])
        }
        this.reloadImage(config);

        return config

      }
    },
    methods: {
      reloadImage(config) {
        config.data = {"values": this.values};
        let tooltipOptions = {
          theme: 'custom',
          offsetY: -110
        };
        vegaEmbed('#' + this.source, config, {tooltip: tooltipOptions, mode: 'vega-lite',})
      }
    }
  }

</script>
