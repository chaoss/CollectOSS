<!-- #SPDX-License-Identifier: MIT -->
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
  export default {
    props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
    data() {
      const MONTHNAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const MONTHDECIMALS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
      let years = [];
      for (let i = 9; i >= 0; i--) {
        years.push((new Date()).getFullYear() - i)
      }
      return {
        values: [],
        contributors: [],
        organizations: [],
        view: 'year',
        monthNames: MONTHNAMES,
        monthDecimals: MONTHDECIMALS,
        years: years,
        setYear: 0,
        tick: 0
      }
    },
    created() {
      this.tick = 0
    },
    computed: {
      repo() {
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
          "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
          "width": 800,
          "height": 300,
          "config": {
            "tick": {
              "thickness": 8,
              "bandSize": 23
            },
            "axis": {
              "grid": false,
              "title": null,
              "domainWidth": 1
            },
            "legend": {
              "titleFontSize": 10,
              "titlePadding": 10
            },
            "scale": {"minSize": 100, "maxSize": 500},
            "view": {"stroke": "transparent"},
          },
          "layer": [
            {
              "transform": [],
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
              "transform": [],
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
        };

        let repo = window.AugurAPI.Repo({gitURL: this.repo});
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
            const YEAR = (new Date(change.author_date)).getFullYear();
            const MONTH = (new Date(change.author_date)).getMonth();

            obj[change[name]] = obj[change[name]] || {additions: 0, deletions: 0};
            addChanges(obj[change[name]], change);
            obj[change[name]][YEAR] = obj[change[name]][YEAR] || {additions: 0, deletions: 0};
            addChanges(obj[change[name]][YEAR], change);
            obj[change[name]][YEAR + '-' + MONTH] = obj[change[name]][YEAR + '-' + MONTH] || {
              additions: 0,
              deletions: 0
            };
            addChanges(obj[change[name]][YEAR + '-' + MONTH], change)
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

        repo.cdRepTpIntervalLocCommits().then((changes) => {
          console.log("CHANGE", changes);
          this.values = changes
        });


        $(this.$el).find('.showme, .hidefirst').removeClass('invis');
        $(this.$el).find('.stackedbarchart').removeClass('loader');

        let repos = [];
        if (this.repo) {
          repos.push(window.AugurRepos[this.repo])
        }

        return config
      }
    }

  }

</script>
