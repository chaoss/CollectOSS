<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card-body v-if="!error" :title="title">
    <div v-if="mount" :id="source"></div>
    <div v-if="!loaded">
      <spinner></spinner>
    </div>
    <div v-if="loaded" class="linechart">
      <vega-lite v-if="!mount" :spec="spec(values)" :data="values"></vega-lite>
      <p v-if="!mount">{{ chart }}</p>
    </div>
    <div v-if="smoothing">{{ getDescription }}</div>
  </d-card-body>
</template>

<script>
  import AugurStats from "@/AugurStats";
  import {mapActions, mapGetters} from "vuex";
  import vegaEmbed from "vega-embed";
  import Spinner from "../../components/Spinner.vue";

  export default {
    props: [
      "source",
      "citeUrl",
      "citeText",
      "title",
      "disableRollingAverage",
      "alwaysByDate",
      "domain",
      "data",
      "endpoints",
      "smoothing"
    ],
    components: {
      Spinner
    },
    data() {
      return {
        chartKey: 0,
        legendLabels: [],
        values: [],
        status: {},
        detail: this.$store.state.showDetail,
        compRepos: this.$store.state.comparedRepos,
        metricSource: null,
        timeperiod: "all",
        forceRecomputeCounter: 0,
        mount: true,
        loaded: false,
        error: false,
        x: 0,
        y: 0,
        loadedData: null
      };
    },

    watch: {
      '$store.state.common.startDate'() {
        if (this.data) {
          this.spec(this.data);
        } else if (this.loadedData) {
          this.spec(this.loadedData);
        }
      },
      '$store.state.common.endDate'() {
        if (this.data) {
          this.spec(this.data);
        } else if (this.loadedData) {
          this.spec(this.loadedData);
        }
      },
      compare: function () {
        this.spec;
      },
      earliest: function () {
        this.spec;
      },
      data: function (newVal, oldVal) {
        if (newVal.length != 0) this.spec;
      },
      compRepos: function () {
        let allFalse = true;
        for (let key in this.status)
          if (this.status[key])
            allFalse = false;
      }
    },
    computed: {
      getDescription() {
        if (this.values[0])
          return 'Each point on this line represents a trailing average of ' + this.values[0].name.split(' ')[1] + '. The aim is to reflect a general trend that is visually interpretable by smoothing common one day spikes.';
        else
          return ''
      },
      gitRepos() {
        return this.$store.getters.gitRepo;
      },
      period() {
        return this.$store.state.common.trailingAverage;
      },
      earliest() {
        return this.$store.state.common.startDate;
      },
      latest() {
        return this.$store.state.compare.endDate;
      },
      compare() {
        return this.$store.state.compare.compare;
      },
      comparedRepos() {
        return this.$store.state.compare.comparedRepos;
      },
      rawWeekly() {
        return this.$store.state.compare.rawWeekly;
      },
      showArea() {
        return this.$store.state.compare.showArea;
      },
      showTooltip() {
        return this.$store.state.common.showTooltip;
      },
      showDetail() {
        return this.$store.state.common.showDetail;
      },
      ...mapGetters("common", ["repoRelations", "apiRepos", "startDate", "endDate"]),
      ...mapGetters("compare", ["base", "comparedAPIRepos"])
    },
    methods: {
      ...mapActions("common", [
        "endpoint"
      ]),
      ...mapActions("compare", ["setComparedRepos"]),
      thisShouldTriggerRecompute() {
        this.forceRecomputeCounter++;
      },
      downloadSVG() {
        let svgSaver = new window.SvgSaver();
        let svg = window.$(this.$refs.holder).find("svg")[0];
        svgSaver.asSvg(svg, this.__download_file + ".svg");
      },
      downloadPNG() {
        let pngSaver = new window.SvgSaver();
        let svg = window.$(this.$refs.holder).find("svg")[0];
        pngSaver.asPng(svg, this.__download_file + ".png");
      },
      renderChart() {
        let allFalse = true;
        for (let key in this.status) if (this.status[key]) allFalse = false;
      },
      renderError() {
        console.log("DLC", "ERROR ERROR");
        this.error = true;
        this.loaded = true;
      },
      respec() {
        this.spec;
      },
      reloadImage(config) {
        if (config.data.values.length == 0) {
          console.log("DLC", "yo error");
          this.renderError();
          return;
        }
        vegaEmbed("#" + this.source, config, {
          tooltip: {offsetY: -110},
          mode: "vega-lite"
        });
      },
      convertKey(ary) {
        ary.forEach(el => {
          let keys = Object.keys(el);
          let field = null;
          keys.forEach(key => {
            if (
              el[key] != null &&
              key != "date" &&
              key != "repo_name" &&
              key != "repo_id" &&
              key != "field" &&
              key != "value"
            ) {
              field = key;
            }
          });
          el["value"] = el[field];
          el["field"] = field;
        });
        return ary;
      },
      spec(data) {
        let repos = this.repos;
        //COLORS TO PICK FOR EACH REPO
        let colors = ["black", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"];
        let brush = this.showDetail
          ? {filter: {selection: "brush"}}
          : {filter: "datum.date > 0"};
        let config = {
          data: {
            values: []
          },
          config: {
            axis: {
              grid: true
            },
            legend: {
              offset: -(this.x / 3.15),
              titleFontSize: 0,
              titlePadding: 10
            }
          },
          vconcat: [
            {
              width: this.x / 3,
              height: this.y / 3,

              layer: [
                {
                  transform: [brush],
                  mark: "rule",
                  encoding: {
                    x: {
                      field: "date",
                      type: "temporal",
                      axis: {
                        labels: true,
                        format: "%b %Y",
                        title: " "
                      }
                    },
                    color: {
                      field: "name",
                      type: "nominal",
                      scale: {range: colors},
                      sort: false
                    },
                    opacity: {
                      value: 0
                    }
                  }
                }
              ]
            }
          ]
        };
        let selectionAdded = false;
        let getStandardLine = (key, color, extension) => {
          return {
            encoding: {
              x: {
                field: "date" + extension,
                type: "temporal",
                axis: {
                  labels: !this.showDetail,
                  format: "%b %Y",
                  title: " "
                }
              },
              y: {
                field: key,
                type: "quantitative",
                axis: {
                  title: null
                }
              },
              color: {
                value: color
              }
            },
            mark: {
              type: "line",
              interpolate: "basis",
              clip: true
            }
          };
        };

        let getRawLine = (key, color) => {
          return {
            transform: [brush],
            encoding: {
              x: {
                field: "date",
                type: "temporal",
                axis: {
                  labels: !this.showDetail,
                  format: "%b %Y",
                  title: " "
                }
              },
              y: {
                field: key,
                type: "quantitative",
                axis: {
                  title: null
                }
              },
              color: {
                value: color
              },
              opacity: {value: 0.3}
            },
            mark: {type: "line", clip: true}
          };
        };

        let getToolPoint = key => {
          let size = 17;
          let timeDiff = Math.abs(this.latest.getTime() - this.earliest.getTime());
          let diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
          let field = "valueRolling" + this.repo;
          size = diffDays / 150;
          if (this.rawWeekly)
            size = 3;
          selectionAdded = true;
          return {
            transform: [brush],
            mark: "rule",
            selection: {
              tooltip: {
                type: "single",
                on: "mouseover",
                nearest: false,
                empty: "none"
              }
            },
            encoding: {
              size: {value: 20},
              opacity: {value: 0.001},
              x: {
                field: "date",
                type: "temporal",
                axis: null
              },
              tooltip: [{field: field, type: "quantitative"}]
            }
          };
        };

        let getStandardPoint = (key, color) => {
          let selection = !selectionAdded ? {
            tooltip: {
              type: "single",
              on: "mouseover",
              encodings: ["x"],
              empty: "none"
            }
          } : null;
          selectionAdded = true;
          return {
            transform: [brush],
            encoding: {
              x: {
                field: "date",
                type: "temporal",
                axis: {
                  title: " ",
                  format: "%b %Y"
                }
              },
              color: {
                value: "black"
              },
              opacity: {
                condition: {
                  selection: "tooltip",
                  value: 1
                },
                value: 0
              }
            },
            mark: {
              type: "rule"
            },
            selection: selection
          };
        };

        let getArea = function (extension) {
          return {
            transform: [brush],
            mark: {
              type: "area",
              interpolate: "basis",
              clip: true
            },
            encoding: {
              x: {
                field: "date" + extension,
                type: "temporal",
                axis: {format: "%b %Y", title: " "}
              },
              y: {
                field: "lower" + extension,
                type: "quantitative",
                axis: {
                  title: null
                }
              },
              y2: {
                field: "upper" + extension,
                type: "quantitative",
                axis: {
                  title: null
                }
              },
              color: {
                value: "gray"
              },
              opacity: {value: 0.14}
            }
          };
        };

        let rule = {
          transform: [
            {
              filter: {
                selection: "tooltip"
              }
            },
            brush
          ],
          mark: "rule",
          encoding: {
            x: {
              type: "temporal",
              field: "date",
              axis: {format: "%b %Y", title: " "}
            },
            color: {
              value: "black"
            }
          }
        };

        let getValueText = function (key) {
          return {
            transform: [{filter: {selection: "tooltip"}}, brush],
            mark: {type: "text", align: "left", dx: 5, dy: -5},
            encoding: {
              text: {type: "quantitative", field: key},
              x: {
                field: "date",
                type: "temporal",
                axis: {format: "%b %Y", title: " "}
              },
              y: {field: key, type: "quantitative", axis: {title: null}},
              color: {value: "green"}
            }
          };
        };

        let getDateText = function (key) {
          return {
            transform: [{filter: {selection: "tooltip"}}, brush],
            mark: {type: "text", align: "left", dx: 5, dy: -15},
            encoding: {
              text: {type: "temporal", field: "date"},
              x: {
                field: "date",
                type: "temporal",
                axis: {format: "%b %Y", title: " "}
              },
              y: {field: key, type: "quantitative", axis: {title: null}},
              color: {value: "black"}
            }
          };
        };

        let getDetail = key => {
          let color =
            this.comparedTo && this.status.compared ? "#FF3647" : "black";
          return {
            width: 520,
            height: 60,
            mark: "line",
            title: {
              text: " "
            },
            selection: {
              brush: {type: "interval", encodings: ["x"]}
            },
            encoding: {
              x: {
                field: "date",
                type: "temporal",
                axis: {format: "%b %Y", title: " "}
              },
              y: {
                field: key,
                type: "quantitative",
                axis: {
                  title: null
                }
              },
              opacity: {
                value: 0.5
              },
              color: {
                value: color
              }
            }
          };
        };

        let buildLines = function (key, color, extension) {
          config.vconcat[0].layer.push(getStandardLine(key, color, extension));
        };

        let buildMetric = () => {
          let color = 0;
          repos.forEach(repo => {
            if (!repo) return;
            buildLines(
              "valueRolling" + repo.replace(/\//g, "").replace(/\./g, ""),
              colors[color],
              repo.replace(/\//g, "").replace(/\./g, "")
            );

            if (this.rawWeekly)
              config.vconcat[0].layer.push(
                getRawLine("value" + repo, colors[color])
              );
            // if user doesn't want detail, then set vconcat to og
            if (this.showDetail)
              config.vconcat[1] = getDetail("valueRolling" + this.repo);
            else if (config.vconcat[1]) config.vconcat.pop();
            color++;
          });
        };

        /* push the area to general spec
        can change repo to whatever */
        if (this.showArea && repos.length < 3) {
          repos.forEach(repo => {
            config.vconcat[0].layer.push(
              getArea(repo.replace(/\//g, "").replace(/\./g, ""))
            );
          });
        } else {
          repos.forEach(repo => {
            console.log(repo);
            if (repo) {
              for (let x = 0; x < config.vconcat[0].layer.length; x++) {
                if (config.vconcat[0].layer[x] == getArea(repo.replace(/\//g, "").replace(/\./g, ""))) {
                  config.vconcat[0].layer[x] = {};
                  buildMetric();
                }
              }
            }
          });
        }

        let buildTooltip = function (key) {
          config.vconcat[0].layer.push(getToolPoint(key));
          if (repos.length < 3) {
            let col = -1;
            repos.forEach(repo => {
              config.vconcat[0].layer.push(getStandardPoint(key, colors[col]));
              col++;
            });
            config.vconcat[0].layer.push(getValueText(key));
            config.vconcat[0].layer.push(getDateText(key));
            if (repos.length > 1) {
              config.vconcat[0].layer.push(rule);
            }
          }
        };

        buildMetric();

        buildLines(
          "valueRolling" + repos[0].replace(/\//g, "").replace(/\./g, ""),
          colors[0]
        );
        if (repos[1])
          buildLines(
            "valueRolling" + repos[1].replace(/\//g, "").replace(/\./g, ""),
            colors[1]
          );
        let startDateFromVuex = this.$store.state.common.startDate;
        let startYear = startDateFromVuex.getFullYear();
        let startMonth = startDateFromVuex.getMonth();
        let startData = startDateFromVuex.getDate();
        let endDateFromVuex = this.$store.state.common.endDate;
        let endYear = endDateFromVuex.getFullYear();
        let endMonth = endDateFromVuex.getMonth();
        let endDate = endDateFromVuex.getDate();
        /** Takes a string like "commits,lines_changed:additions+deletions"
         * and makes it into an array of endpoints:
         * endpoints = ['commits','lines_changed']
         * and a map of the fields wanted from those endpoints:
         * fields = {
         *     'lines_changed': ['additions', 'deletions']
         *   }
         */
        let endpoints = [];
        let fields = {};
        this.source.split(",").forEach(endpointAndFields => {
          let split = endpointAndFields.split(":");
          endpoints.push(split[0]);
          if (split[1]) {
            fields[split[0]] = split[1].split("+");
          }
        });

        let processData = data => {
          // Make it so the user can save the data we are using
          this.__download_data = data;
          this.__download_file = this.title
            .replace(/ /g, "-")
            .replace("/", "by")
            .toLowerCase();
          // We usually want to limit dates and convert the key to being vega-lite friendly
          let defaultProcess = (obj, key, field, count) => {
            console.log("DLC begin default process: ", obj, key, field, count);
            let d = obj[key];
            if (typeof field == "string") {
              field = [field];
            }
            d = AugurStats.convertDates(d, this.earliest, this.latest, "date");
            return d;
          };

          // Normalize the data into [{ date, value },{ date, value }]
          // BuildLines iterates over the fields requested and runs onCreateData on each
          let normalized = [];
          let aggregates = [];
          let buildLines = (obj, onCreateData, repo) => {
            if (!obj) {
              return;
            }
            if (!onCreateData) {
              onCreateData = () => {
                normalized.push(d);
              };
            }
            let count = 0;

            for (let key in obj) {
              if (obj.hasOwnProperty(key)) {
                if (fields[key]) {
                  fields[key].forEach(field => {
                    onCreateData(obj, key, field, count);
                    count++;
                  });
                } else {
                  if (Array.isArray(obj[key]) && obj[key].length > 0) {
                    let field = Object.keys(obj[key][0]).splice(1);
                    onCreateData(obj, key, field, count);
                    count++;
                  } else {
                    this.status[repo] = false;
                    let noRepoWithData = true;
                    Object.keys(this.status).forEach(repo => {
                      if (this.status[repo]) noRepoWithData = false;
                    });
                    if (noRepoWithData) {
                      this.renderError();
                    }
                  }
                }
              }
            }
          };

          // Build the lines we need
          let legend = []; //repo + field strings for vega legend
          let values = [];
          let colors = [];
          let baselineVals = null;
          let baseDate = null;
          let x = 0;

          // TOGGLE SMOOTHING
          let smoothingValue = this.$store.state.common.trailingAverage;
          if (this.smoothing === false) {
            smoothingValue = 4;
            console.log(`smoothing disabled for ${this.title}`);
          }

          this.repos.forEach(repo => {
            if (!repo) return;
            let ref = repo;
            if (ref.includes('/')) {
              ref = ref.split('/')[ref.split('/').length - 1]
            }
            buildLines(data[ref], (obj, key, field, count) => {
                // Build basic chart using rolling averages
                let d = defaultProcess(obj, key, field, count);
                console.log("DLC", d);
                let rolling = null;
                if (ref == this.repo && d[0]) baseDate = d[0].date;
                else d = AugurStats.alignDates(d, baseDate, smoothingValue);
                if (this.compare == "zscore") {
                  // && this.comparedRepos.length > 0
                  rolling = AugurStats.rollingAverage(
                    AugurStats.zscores(d, "value"),
                    "value",
                    smoothingValue,
                    ref
                  );
                } //else if (this.rawWeekly || this.disableRollingAverage) rolling = AugurStats.convertKey(d, 'value', 'value' + repo)
                else if (this.compare == "baseline") {
                  if (repo.githubURL == this.repo) {
                    baselineVals = AugurStats.rollingAverage(
                      d,
                      "value",
                      smoothingValue,
                      ref
                    );
                  }
                  rolling = AugurStats.rollingAverage(
                    d,
                    "value",
                    smoothingValue,
                    ref
                  );
                  if (baselineVals) {
                    for (let i = 0; i < baselineVals.length; i++) {
                      if (rolling[i] && baselineVals[i])
                        rolling[i].valueRolling -= baselineVals[i].valueRolling;
                    }
                  }
                } else {
                  d = this.convertKey(d);
                  console.log("DLC prerolling", d, smoothingValue, ref);
                  rolling = AugurStats.rollingAverage(
                    d,
                    "value",
                    smoothingValue,
                    ref
                  );
                  console.log("DLC rolling:", rolling);
                  while (rolling[0].valueRolling == 0) rolling.shift();
                  rolling.forEach(tuple => {
                    tuple.date.setDate(tuple.date.getDate() + x);
                  });
                  console.log("DLC", rolling)
                }
                normalized.push(
                  AugurStats.standardDeviationLines(rolling, "valueRolling", ref)
                );
                aggregates.push(
                  AugurStats.convertKey(d, "value", "value" + ref)
                );
                legend.push(repo + " " + key);
              },
              ref
            );
            x++;
          });

          if (normalized.length == 0) {
          } else {
            values = [];
            for (let i = 0; i < legend.length; i++) {
              normalized[i].forEach(d => {
                if (d.date < new Date(startYear, startMonth, startData) || d.date > new Date(endYear, endMonth, endDate)) {
                  d = {};
                } else {
                  d.name = legend[i];
                  d.color = colors[i];
                  values.push(d);
                }
              });
              if (this.rawWeekly) {
                aggregates[i].forEach(d => {
                  if (d.date < new Date(startYear, startMonth, startData) || d.date > new Date(endYear, endMonth, endDate)) {
                    d = {};
                  } else {
                    d.name = legend[i];
                    d.color = colors[i];
                    values.push(d);
                  }
                });
              }
            }
            this.repos.forEach(repo => {
              console.log(repo);
              if (!this.status[repo]) {
                let temp = JSON.parse(JSON.stringify(values));
                console.log("setting name to ", repo + ": data n/a");
                temp = temp.map(datum => {
                  datum.name = repo + ": data n/a";
                  return datum;
                });
                values.push.apply(values, temp);
              }
            });

            this.legendLabels = legend;
            config.data = {values: values};
            this.values = values;

            if (values.length < 2) {
              console.log("less than 2 datapoints error");
              this.renderError();
            } else {
              this.renderChart();
              this.loaded = true;
            }
          }
        };

        processData(data);

        if (this.mount) this.reloadImage(config);

        return config;
      }
    },
    mounted() {
      var win = window,
      doc = document,
      docElem = doc.documentElement,
      body = doc.getElementsByTagName("body")[0];
      this.x = win.innerWidth || docElem.clientWidth || body.clientWidth;
      this.y = win.innerHeight || docElem.clientHeight || body.clientHeight;

      // Get the repos we need
      let repos = [];
      let apiRepos = [];
      let promises = [];

      let compares = null;

      if (this.base) {
        apiRepos.push(this.base);
        let ref = this.base.url || this.base.repo_name;
        if (ref.includes('/'))
          ref = ref.split('/')[ref.split('/').length - 1];
        repos = [ref];
      } else {
        console.log(this.$router.currentRoute.params)
      }

      if ("compares" in this.$router.currentRoute.params) {
        compares = this.$router.currentRoute.params.compares;
        if (compares in this.apiRepos) {
          console.log("DLC Api repos already loaded", this.apiRepos, compares);
          apiRepos.push(this.apiRepos[compares]);
          let ref = this.repoRelations[compares.split("/")[0]][compares.split("/")[1]].url ||
            this.repoRelations[compares.split("/")[0]][compares.split("/")[1]].repo_name;
          if (ref.includes('/'))
            ref = ref.split('/')[ref.split('/').length - 1];
          if (!repos.includes(ref))
            repos.push(ref);
        } else {
          let ids = !this.$router.currentRoute.params.comparedRepoIds ? [] : this.$router.currentRoute.params.comparedRepoIds.split(",");
          promises.push(this.setComparedRepos({names: compares.split(','), ids: ids}));
        }
      }
      Promise.all(promises).then(() => {
        if (compares) {
          compares.split(',').forEach((repo_idx) => {
            let repo = typeof repo_idx == 'string' ? repo_idx : compares.split(',')[repo_idx];
            apiRepos.push(this.apiRepos[repo]);
            let ref =
              this.repoRelations[repo.split("/")[0]][repo.split("/")[1]].url ||
              this.repoRelations[repo.split("/")[0]][repo.split("/")[1]].repo_name;
            if (ref.includes('/'))
              ref = ref.split('/')[ref.split('/').length - 1];
            if (!repos.includes(ref))
              repos.push(ref);
          })
        }

        repos.forEach(repo => {
          this.status[repo] = true;
        });
        this.repos = repos;

        if (this.data) {
          let dataFilled = true;
          Object.keys(this.data).forEach(key => {
            if (this.data[key].length < 1) dataFilled = false;
          });
          if (dataFilled) {
            this.spec(this.data);
            repos = Object.keys(this.data);
          }
        } else {
          this.endpoint({repos: apiRepos, endpoints: [this.source]})
            .then(data => {
              this.loadedData = data;
              if (Object.keys(this.loadedData).length > 0) {
                this.spec(this.loadedData);
              }
            })
            .catch(error => {
              this.renderError();
            });
        }
      });
    },
    created() {
      let query_string = "chart_mapping=" + this.source;
      this.$store.state.common.AugurAPI.getMetricsStatus(query_string).then(
        data => {
          this.metricSource = data[0].data_source;
        }
      );
    }
  };
</script>
