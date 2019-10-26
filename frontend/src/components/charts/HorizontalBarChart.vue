<template>
  <div>
    <div :id="source"></div>
    <div class="horizontalBarChartDiv form-item form-checkboxes tickradios">
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
</template>


<script>
import { mapState } from 'vuex'
import AugurStats from '@/AugurStats.ts'
import vegaEmbed from 'vega-embed'

export default {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'measure'],
  data() {
    const years = [];
    for (let i = 9; i >= 0; i--) {
      years.push((new Date()).getFullYear() - i);
    }
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    return {
      values: [],
      contributors: [],
      organizations: [],
      view: 'year',
      monthNames,
      monthDecimals,
      years,
      setYear: 0,
      tick: 0,
      type: 1,
      x:0,
      y:0
    };
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
      return this.$store.state.baseRepo;
    },
    gitRepo() {
      return this.$store.state.gitRepo;
    },
    earliest() {
      return this.$store.state.startDate;
    },
    latest() {
      return this.$store.state.endDate;
    },
    spec() {

      let field = null;


      if (this.type == 0) {
        field = 'netratio';
      } else if (this.type == 1) {
        field = 'totalratio';
      } else if (this.type == 2) {
        field = 'addedratio';
      }

      const colors = ['#FF3647', '#4736FF', '#3cb44b', '#ffe119', '#f58231', '#911eb4', '#42d4f4', '#f032e6'];
      const config = {
        $schema: 'https://vega.github.io/schema/vega-lite/v2.json',
        width: this.x / 3.4,
        height: this.y / 4.3,
        padding: {left: 0, top: 0, right: 0, bottom: 0},
        config: {
          tick: {
            thickness: 8,
            bandSize: 23,
          },
          axis: {
            grid: false,
          },
        },
        layer: [
          {
            transform: [

              {
                calculate: '(datum.additions > datum.deletions) ? \'more deletions\' : \'more additions\'',
                as: 'Majority type of changes',
              },
              {
                calculate: '(datum.additions - datum.deletions)',
                as: 'Net lines added',
              },
              {
                calculate: '((datum.additions - datum.deletions) / datum.commits)',
                as: 'netratio',
              },
              {
                calculate: '(datum.additions / datum.commits)',
                as: 'addedratio',
              },
              {
                calculate: '(datum.lines / datum.commits)',
                as: 'totalratio',
              },
            ],
            mark: {
              type: 'bar',

            },
            encoding: {
              x: {field, type: 'quantitative'},
              y: {
                field: 'cmt_author_email',
                sort: {
                  field,
                  op: 'mean',
                  order: 'descending',
                },
                type: 'nominal',
                axis: null,
              },
              color: {
                field: 'cmt_author_email',
                type: 'nominal',
                scale: {scheme: 'category10'},
                legend: null,
              },
            },


          },
          {
            transform: [

              {
                calculate: '(datum.additions > datum.deletions) ? \'more deletions\' : \'more additions\'',
                as: 'Majority type of changes',
              },
              {
                calculate: '(datum.additions - datum.deletions)',
                as: 'Net lines added',
              },
              {
                calculate: '((datum.additions - datum.deletions) / datum.commits)',
                as: 'netratio',
              },
              {
                calculate: '(datum.additions / datum.commits)',
                as: 'addedratio',
              },
              {
                calculate: '(datum.lines / datum.commits)',
                as: 'totalratio',
              },
            ],
            mark: {
              type: 'rule',
              size: 20,
            },

            selection: {
              tooltip: {
                type: 'multi',
                on: 'mouseover',
                nearest: false,
                empty: 'none',
                fields: ['_vgsid_'],
                toggle: 'event.shiftKey',
                resolve: 'global',
              },
            },
            encoding: {

              y: {
                field: 'cmt_author_email',
                sort: {
                  field,
                  op: 'mean',
                  order: 'descending',
                },
                type: 'nominal',
                axis: null,
              },
              tooltip: [{field, type: 'quantitative'}, {
                field: 'cmt_author_email',

                type: 'nominal',
              }],
              color: {
                condition: {
                  selection: {not: 'tooltip'}, value: 'transparent',
                },
                value: 'black',
              },
              opacity: {
                value: 0.05,
              },
            },


          },
        ],

      };

      let repo = null;

      const contributors = {};
      const organizations = {};

      const addChanges = (dest, src) => {
        if (dest && src) {
          if (typeof dest !== 'object') {
            dest.additions = 0;
            dest.deletions = 0;
          }
          dest.additions += (src.additions || 0);
          dest.deletions += (src.deletions || 0);
        }
      };

      const group = (obj, name, change, filter) => {
        if (filter(change)) {
          const year = (new Date(change.cmt_author_date)).getFullYear();
          const month = (new Date(change.cmt_author_date)).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      const flattenAndSort = (obj, keyName, sortField) => {
        return Object.keys(obj)
            .map((key) => {
              const d = obj[key];
              d[keyName] = key;
              return d;
            })
            .sort((a, b) => {
              return b[sortField] - a[sortField];
            });
      };

      const filterDates = (change) => {
        return (new Date(change.cmt_author_date)).getFullYear() > this.years[0];
      };

      const authors = [];
      const track = {};
      let changes = null;


      if (this.data) {
        changes = this.data;
      }
      else { changes = repo.changesByAuthor(); }

      changes.forEach((change) => {
        // change.cmt_author_date = new Date(change.cmt_author_date)
        // change["commits"] = change["commits"] ? change["commits"] + 1 : 1
        track[change.cmt_author_email] = track[change.cmt_author_email] ? track[change.cmt_author_email] : {commits: 0, lines: 0, additions: 0, deletions: 0};
        track[change.cmt_author_email].commits = track[change.cmt_author_email].commits ? track[change.cmt_author_email].commits + 1 : 1;
        // track["total_commits"] += 1
        // change["lines"] = change["lines"] ? change["lines"] + change.additions : change.additions
        track[change.cmt_author_email].lines = track[change.cmt_author_email].lines ? track[change.cmt_author_email].lines + change.additions + change.deletions : change.additions + change.deletions;
        track[change.cmt_author_email].additions = track[change.cmt_author_email].additions ? track[change.cmt_author_email].additions + change.additions : change.additions;
        track[change.cmt_author_email].deletions = track[change.cmt_author_email].deletions ? track[change.cmt_author_email].deletions + change.deletions : change.deletions;
        // track["total_lines"] += change.additions
      });
      console.log(changes)
      changes.forEach((change) => {
        if (isFinite(change.additions) && isFinite(change.deletions)) {
          group(contributors, 'cmt_author_email', change, filterDates);
          if (change.author_affiliation !== 'Unknown') {
            group(organizations, 'affiliation', change, filterDates);
          }
        }
        if (!authors.includes(change.cmt_author_email)) {
          authors.push(change.cmt_author_email);
          change.flag = ((track[change.cmt_author_email] / track.total * 100).toFixed(4));
          // console.log(change, track)
        } // else change["flag"] = 100


      });
      console.log(contributors)
      this.contributors = flattenAndSort(contributors, 'cmt_author_email', 'additions');
      let careabout = [];
      this.contributors.slice(0, 10).forEach((obj) => {
        careabout.push(obj.cmt_author_email);
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

      for (let key in track) {
        if (careabout.includes(key)) {
          ary.push({cmt_author_email: key, commits: track[key].commits, lines: track[key].lines, additions: track[key].additions, deletions: track[key].deletions});
        }
      }

      this.values = ary;
      console.log('TRACK', ary, careabout);

      // Get the repos we need
      const repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      this.reloadImage(config);

      return config;

    },
  },
  methods: {
    reloadImage(config) {
      config.data = {values: this.values};
      vegaEmbed('#' + this.source, config, {tooltip: {offsetY: -100, offsetX: 40}, mode: 'vega-lite'});
    },
  },

};
</script>
