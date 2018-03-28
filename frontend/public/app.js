(function() {
  'use strict';

  var globals = typeof global === 'undefined' ? self : global;
  if (typeof globals.require === 'function') return;

  var modules = {};
  var cache = {};
  var aliases = {};
  var has = {}.hasOwnProperty;

  var expRe = /^\.\.?(\/|$)/;
  var expand = function(root, name) {
    var results = [], part;
    var parts = (expRe.test(name) ? root + '/' + name : name).split('/');
    for (var i = 0, length = parts.length; i < length; i++) {
      part = parts[i];
      if (part === '..') {
        results.pop();
      } else if (part !== '.' && part !== '') {
        results.push(part);
      }
    }
    return results.join('/');
  };

  var dirname = function(path) {
    return path.split('/').slice(0, -1).join('/');
  };

  var localRequire = function(path) {
    return function expanded(name) {
      var absolute = expand(dirname(path), name);
      return globals.require(absolute, path);
    };
  };

  var initModule = function(name, definition) {
    var hot = hmr && hmr.createHot(name);
    var module = {id: name, exports: {}, hot: hot};
    cache[name] = module;
    definition(module.exports, localRequire(name), module);
    return module.exports;
  };

  var expandAlias = function(name) {
    return aliases[name] ? expandAlias(aliases[name]) : name;
  };

  var _resolve = function(name, dep) {
    return expandAlias(expand(dirname(name), dep));
  };

  var require = function(name, loaderPath) {
    if (loaderPath == null) loaderPath = '/';
    var path = expandAlias(name);

    if (has.call(cache, path)) return cache[path].exports;
    if (has.call(modules, path)) return initModule(path, modules[path]);

    throw new Error("Cannot find module '" + name + "' from '" + loaderPath + "'");
  };

  require.alias = function(from, to) {
    aliases[to] = from;
  };

  var extRe = /\.[^.\/]+$/;
  var indexRe = /\/index(\.[^\/]+)?$/;
  var addExtensions = function(bundle) {
    if (extRe.test(bundle)) {
      var alias = bundle.replace(extRe, '');
      if (!has.call(aliases, alias) || aliases[alias].replace(extRe, '') === alias + '/index') {
        aliases[alias] = bundle;
      }
    }

    if (indexRe.test(bundle)) {
      var iAlias = bundle.replace(indexRe, '');
      if (!has.call(aliases, iAlias)) {
        aliases[iAlias] = bundle;
      }
    }
  };

  require.register = require.define = function(bundle, fn) {
    if (bundle && typeof bundle === 'object') {
      for (var key in bundle) {
        if (has.call(bundle, key)) {
          require.register(key, bundle[key]);
        }
      }
    } else {
      modules[bundle] = fn;
      delete cache[bundle];
      addExtensions(bundle);
    }
  };

  require.list = function() {
    var list = [];
    for (var item in modules) {
      if (has.call(modules, item)) {
        list.push(item);
      }
    }
    return list;
  };

  var hmr = globals._hmr && new globals._hmr(_resolve, require, modules, cache);
  require._cache = cache;
  require.hmr = hmr && hmr.wrap;
  require.brunch = true;
  globals.require = require;
})();

(function() {
var global = typeof window === 'undefined' ? this : window;require.register("child_process", function(exports, require, module) {
  module.exports = {};
});
require.register("fs", function(exports, require, module) {
  module.exports = {};
});
var process;
var __makeRelativeRequire = function(require, mappings, pref) {
  var none = {};
  var tryReq = function(name, pref) {
    var val;
    try {
      val = require(pref + '/node_modules/' + name);
      return val;
    } catch (e) {
      if (e.toString().indexOf('Cannot find module') === -1) {
        throw e;
      }

      if (pref.indexOf('node_modules') !== -1) {
        var s = pref.split('/');
        var i = s.lastIndexOf('node_modules');
        var newPref = s.slice(0, i).join('/');
        return tryReq(name, newPref);
      }
    }
    return none;
  };
  return function(name) {
    if (name in mappings) name = mappings[name];
    if (!name) return;
    if (name[0] !== '.' && pref) {
      var val = tryReq(name, pref);
      if (val !== none) return val;
    }
    return require(name);
  }
};
require.register("GHData.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = GHData;

var _vueVega = require('vue-vega');

var _vueVega2 = _interopRequireDefault(_vueVega);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var queryString = require('query-string');

function GHData() {
  window.jQuery = require('jquery');
  window.Vue = require('vue');
  window.Vuex = require('vuex');
  var GHDataAPI = require('GHDataAPI').default;
  window.GHDataAPI = new GHDataAPI();
  window.GHDataRepos = {};
  window.GHDataStats = require('GHDataStats').default;
  window.$ = window.jQuery;
  window._ = require('lodash');
  window.d3 = require('d3');
  window.VueVega = _vueVega2.default;
  window.SvgSaver = require('svgsaver');

  var GHDataApp = require('./components/GHDataApp');

  Vue.use(Vuex);
  Vue.use(_vueVega2.default);
  Vue.config.productionTip = false;

  window.ghdata = new Vuex.Store({
    state: {
      baseRepo: null,
      comparedRepos: [],
      trailingAverage: 180,
      startDate: new Date("1 January 2005"),
      endDate: new Date(),
      compare: "each",
      showBelowAverage: false,
      rawWeekly: false,
      byDate: false
    },
    mutations: {
      setBaseRepo: function setBaseRepo(state, payload) {
        var repo = window.GHDataAPI.Repo(payload.url);
        if (!window.GHDataRepos[repo.toString()]) {
          window.GHDataRepos[repo.toString()] = repo;
        }
        state.baseRepo = repo.toString();
        if (!payload.keepCompared) {
          state.comparedRepos = [];
        }
        var title = repo.owner + '/' + repo.name + '- GHData';
        var queryString = '?repo=' + repo.owner + '+' + repo.name;
        window.history.pushState(null, title, queryString);
      },
      addComparedRepo: function addComparedRepo(state, payload) {
        var repo = window.GHDataAPI.Repo(payload.url);
        if (!window.GHDataRepos[repo.toString()]) {
          window.GHDataRepos[repo.toString()] = repo;
        }
        state.comparedRepos.push(repo.toString());
        var title = 'GHData';
        var queryString = window.location.search + '&comparedTo[]=' + repo.owner + '+' + repo.name;
        window.history.pushState(null, title, queryString);
      },
      setDates: function setDates(state, payload) {
        if (payload.startDate) {
          state.startDate = new Date(payload.startDate);
        }
        if (payload.endDate) {
          state.endDate = new Date(payload.endDate);
        }
      },
      setCompare: function setCompare(state, payload) {
        state.compare = payload.compare;
      },
      setVizOptions: function setVizOptions(state, payload) {
        if (payload.trailingAverage) {
          state.trailingAverage = parseInt(payload.trailingAverage, 10);
        }
        if (typeof payload.rawWeekly !== 'undefined') {
          state.rawWeekly = payload.rawWeekly;
        }
        if (typeof payload.showBelowAverage !== 'undefined') {
          state.showBelowAverage = payload.showBelowAverage;
        }
      },
      reset: function reset(state) {
        state = {
          baseRepo: null,
          comparedRepos: [],
          trailingAverage: 180,
          startDate: new Date("1 January 2005"),
          endDate: new Date(),
          compare: "each",
          byDate: false
        };
        window.history.pushState(null, 'GHData', '/');
      } // end reset

    } // end mutations
  });

  GHDataApp.store = window.ghdata;
  window.GHDataApp = new Vue(GHDataApp).$mount('#app');

  // Load state from query string
  var parsed = queryString.parse(location.search, { arrayFormat: 'bracket' });
  if (parsed.repo) {
    window.GHDataApp.$store.commit('setBaseRepo', { url: parsed.repo.replace(' ', '/') });
  }
  if (parsed.comparedTo) {
    parsed.comparedTo.forEach(function (repo) {
      window.GHDataApp.$store.commit('addComparedRepo', { url: repo.replace(' ', '/') });
    });
  }
}
});

;require.register("GHDataAPI.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var $ = require('jquery');

var GHDataAPI = function () {
  function GHDataAPI(hostURL, version, autobatch) {
    _classCallCheck(this, GHDataAPI);

    this._version = version || 'unstable';
    this._host = hostURL || 'http://' + window.location.host + '/api/';
    this.__cache = {};
    this.__timeout = null;
    this.__pending = {};

    this.autobatch = typeof autobatch !== 'undefined' ? autobatch : true;
    this.openRequests = 0;
  }

  _createClass(GHDataAPI, [{
    key: '__autobatcher',
    value: function __autobatcher(url, params, fireTimeout) {
      var _this = this;

      if (this.__timeout !== null && !fireTimeout) {
        this.__timeout = setTimeout(function () {
          __autobatch(undefined, undefined, true);
        });
      }
      return new Promise(function (resolve, reject) {
        if (fireTimeout) {
          var batchURL = _this._host + _this._version + '/batch';
          var requestArray = [];
          Object.keys(_this.__pending).forEach(function (key) {
            requestArray.push({});
          });
          $.post(batchURL);
        }
      });
    }
  }, {
    key: 'Repo',
    value: function Repo(owner, repoName) {
      var _this2 = this;

      if (repoName) {
        var repo = { owner: owner, name: repoName };
      } else if (owner) {
        var splitURL = owner.split('/');
        if (splitURL.length < 3) {
          var repo = { owner: splitURL[0], name: splitURL[1] };
        } else {
          var repo = { owner: splitURL[3], name: splitURL[4] };
        }
      }

      repo.toString = function () {
        return repo.owner + '/' + repo.name;
      };

      var Endpoint = function Endpoint(endpoint) {
        _this2.openRequests++;
        var self = _this2;
        var url = _this2._host + _this2._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint;
        return function (params, callback) {
          var _this3 = this;

          if (self.__cache[btoa(url)]) {
            if (self.__cache[btoa(url)].created_at > Date.now() - 1000 * 60) {
              return new Promise(function (resolve, reject) {
                resolve(JSON.parse(self.__cache[btoa(url)].data));
              });
            }
          }
          if (this.autobatch) {
            return this.__autobatcher(url, params);
          }
          return $.get(url, params).then(function (data) {
            _this3.openRequests--;
            self.__cache[btoa(url)] = {
              created_at: Date.now(),
              data: JSON.stringify(data)
            };
            if (typeof callback === 'function') {
              callback(data);
            }
            return new Promise(function (resolve, reject) {
              if ((typeof data === 'undefined' ? 'undefined' : _typeof(data)) == undefined) {
                reject();
              } else {
                resolve(data);
              }
            });
          });
        };
      };

      var Timeseries = function Timeseries(endpoint) {
        var func = Endpoint('timeseries/' + endpoint);
        func.relativeTo = function (baselineRepo, params, callback) {
          var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name;
          return Endpoint(url)();
        };
        return func;
      };

      repo.commits = Timeseries('commits');
      repo.forks = Timeseries('forks');
      repo.issues = Timeseries('issues');
      repo.pulls = Timeseries('pulls');
      repo.stars = Timeseries('stargazers');
      repo.tags = Timeseries('tags');
      repo.downloads = Timeseries('downloads');
      repo.totalCommitters = Timeseries('total_committers');
      repo.issueComments = Timeseries('issue/comments');
      repo.commitComments = Timeseries('commits/comments');
      repo.pullReqComments = Timeseries('pulls/comments');
      repo.pullsAcceptanceRate = Timeseries('pulls/acceptance_rate');
      repo.issuesClosed = Timeseries('issues/closed');
      repo.issuesResponseTime = Timeseries('issues/response_time');
      repo.issueActivity = Timeseries('issues/activity');

      repo.contributors = Endpoint('contributors');
      repo.contributions = Endpoint('contributions');
      repo.committerLocations = Endpoint('committer_locations');
      repo.communityAge = Endpoint('community_age');
      repo.linkingWebsites = Endpoint('linking_websites');
      repo.busFactor = Endpoint('bus_factor');
      repo.dependents = Endpoint('dependents');
      repo.dependencies = Endpoint('dependencies');
      repo.dependencyStats = Endpoint('dependency_stats');
      repo.watchers = Endpoint('watchers');

      //testing


      return repo;
    }
  }]);

  return GHDataAPI;
}();

exports.default = GHDataAPI;
});

;require.register("GHDataStats.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var GHDataStats = function () {
  function GHDataStats() {
    _classCallCheck(this, GHDataStats);
  }

  _createClass(GHDataStats, null, [{
    key: 'convertDates',
    value: function convertDates(data, earliest, latest) {
      earliest = earliest || new Date('01-01-2005');
      latest = latest || new Date();
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return GHDataStats.convertDates(datum);
        });
      } else {

        data = data.map(function (d) {
          d.date = new Date(d.date);
          return d;
        }).filter(function (d) {
          return earliest < d.date && d.date < latest;
        });
      }
      return data;
    }
  }, {
    key: 'convertKey',
    value: function convertKey(data, key) {
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return GHDataStats.convertKey(datum, key);
        });
      } else {
        var EARLIEST = new Date('01-01-2005');
        data = data.map(function (d) {
          d.value = d[key];
          return d;
        });
      }
      return data;
    }
  }, {
    key: 'averageArray',
    value: function averageArray(ary) {
      return ary.reduce(function (a, e) {
        return a + e;
      }, 0) / ary.length;
    }
  }, {
    key: 'standardDeviation',
    value: function standardDeviation(ary, key, mean) {
      var flat = ary.map(function (e) {
        return e[key];
      });
      mean = mean || GHDataStats.averageArray(flat);
      var distances = flat.map(function (e) {
        return (e - mean) * (e - mean);
      });
      return Math.sqrt(GHDataStats.averageArray(distances));
    }
  }, {
    key: 'describe',
    value: function describe(ary, key) {
      var flat = ary.map(function (e) {
        return e[key];
      });
      var mean = GHDataStats.averageArray(flat);
      var stddev = GHDataStats.standardDeviation(ary, key, mean);
      var variance = stddev * stddev;
      return {
        'mean': mean,
        'stddev': stddev,
        'variance': variance
      };
    }
  }, {
    key: 'rollingAverage',
    value: function rollingAverage(data, key, windowSizeInDays) {
      key = key || 'value';
      windowSizeInDays = windowSizeInDays || 180;
      var rolling = [];
      var averageWindow = [];
      var i = 0;
      var lastFound = -1;

      var after = new Date();
      var before = new Date();

      for (var date = new Date(data[0].date); date <= data[data.length - 1].date; date.setDate(date.getDate() + 1)) {

        after.setDate(date.getDate() - windowSizeInDays);

        if (averageWindow.length < windowSizeInDays) {
          for (; i < data.length && averageWindow.length <= windowSizeInDays; i++) {
            if (lastFound > -1) {
              for (var iter = new Date(data[lastFound].date); iter <= data[i].date; iter.setDate(iter.getDate() + 1)) {
                averageWindow.push((data[i][key] + data[lastFound][key]) / 2);
              }
            }
            lastFound = i;
          }
        }

        var average = { date: new Date(date) };
        average[key] = GHDataStats.averageArray(averageWindow.slice(0, windowSizeInDays));
        averageWindow.shift();
        rolling.push(average);
      }
      return rolling;
    }
  }, {
    key: 'convertToPercentages',
    value: function convertToPercentages(data, key, baseline) {
      if (!data) {
        return [];
      }
      baseline = baseline || GHDataStats.averageArray(data.map(function (e) {
        return e[key];
      }));
      data = data.map(function (datum) {
        datum['value'] = datum[key] / baseline;
        return datum;
      });
      return data;
    }
  }, {
    key: 'makeRelative',
    value: function makeRelative(baseData, compareData, config) {

      config.byDate = config.byDate != undefined;
      config.earliest = config.earliest || new Date('01-01-2005');
      config.latest = config.latest || new Date();
      config.period = config.period || 180;

      var iter = {
        base: 0,
        compare: 0
      };
      var data = {};

      data['base'] = GHDataStats.rollingAverage(GHDataStats.convertDates(GHDataStats.convertKey(baseData, Object.keys(baseData[0])[1]), config.earliest, config.latest), undefined, config.period);

      data['compare'] = GHDataStats.rollingAverage(GHDataStats.convertDates(GHDataStats.convertKey(compareData, Object.keys(compareData[0])[1]), config.earliest, config.latest), undefined, config.period);

      var smaller = data['base'][0].date < data['compare'][0].date ? 'base' : 'compare';
      var larger = data['base'][0].date < data['compare'][0].date ? 'compare' : 'base';
      var result = [];

      if (config.byDate) {
        for (; iter[smaller] < data[smaller].length; iter[smaller]++) {
          if (data['base'].date == data['compare'].date) {
            break;
          }
        }
      }

      while (iter['base'] < data['base'].length && iter['compare'] < data['compare'].length) {
        var toPush = {
          value: data['compare'][iter.compare].value / data['base'][iter.base].value
        };
        if (config.byDate) {
          toPush.date = data['base'][iter.base].date;
        } else {
          toPush.x = iter.base;
        }
        result.push(toPush);
        iter['base']++;
        iter['compare']++;
      }

      console.log('relative', result);
      return result;
    }
  }, {
    key: 'zscores',
    value: function zscores(data, key) {
      key = key || 'value';
      var stats = GHDataStats.describe(data, key);
      return data.map(function (e) {
        var newObj = {};
        if (e.date) {
          newObj.date = new Date(e.date);
        }
        var zscore = (e[key] - stats['mean']) / stats['stddev'];
        newObj.value = zscore;
        return newObj;
      });
    }
  }, {
    key: 'combine',
    value: function combine() {
      return Array.from(arguments);
    }
  }]);

  return GHDataStats;
}();

exports.default = GHDataStats;
});

;require.register("components/BaseRepoActivityCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _LineChart = require('./charts/LineChart');

var _LineChart2 = _interopRequireDefault(_LineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    LineChart: _LineChart2.default,
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Activity")]),_vm._v(" "),_c('h2',[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"commits","title":"Commits / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"forks","title":"Forks / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issues","title":"Issues / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issueComments","title":"Issue Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"commitComments","title":"Commit Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pullReqComments","title":"Pull Request Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pullsAcceptanceRate","title":"Pull Acceptance Rate","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pulls","title":"Pulls Requests / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issuesClosed","title":"Issues Closed / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"totalCommitters","title":"Total Committers","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","disableRollingAverage":"1"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('bubble-chart',{attrs:{"source":"contributions","title":"Contributior Overview","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('StackedBarChart',{attrs:{"source":"issueActivity","title":"Stacked Bar Chart","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","disableRollingAverage":"1"}})],1)]),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('small',[_vm._v("Data provided by "),_c('a',{attrs:{"href":"http://ghtorrent.org/msr14.html"}},[_vm._v("GHTorrent")]),_vm._v(" "),_c('span',{staticClass:"ghtorrent-version"}),_vm._v(" and the "),_c('a',{attrs:{"href":"https://developer.github.com/"}},[_vm._v("GitHub API")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-7655e5a2", __vue__options__)
  } else {
    hotAPI.reload("data-v-7655e5a2", __vue__options__)
  }
})()}
});

;require.register("components/BaseRepoEcosystemCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _LineChart = require('./charts/LineChart');

var _LineChart2 = _interopRequireDefault(_LineChart);

var _DependencyOverview = require('./charts/DependencyOverview');

var _DependencyOverview2 = _interopRequireDefault(_DependencyOverview);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    LineChart: _LineChart2.default,
    DependencyOverview: _DependencyOverview2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Ecosystem")]),_vm._v(" "),_c('h2',[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"downloads","title":"Downloads / Day","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"stars","title":"Stars / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1)]),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-12"},[_c('dependency-overview')],1)])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-2a4aa320", __vue__options__)
  } else {
    hotAPI.reload("data-v-2a4aa320", __vue__options__)
  }
})()}
});

;require.register("components/ComparedRepoActivityCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _LineChart = require('./charts/LineChart');

var _LineChart2 = _interopRequireDefault(_LineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  props: ['comparedTo'],
  components: {
    LineChart: _LineChart2.default,
    BubbleChart: _BubbleChart2.default
  },
  computed: {
    repo: function repo() {
      return this.$store.state.repo;
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('div',{class:{ hidden: !this.repo },attrs:{"id":"base-template"}}),_vm._v(" "),_c('h1',[_vm._v("Activity Comparison")]),_vm._v(" "),_c('h2',[_vm._v(_vm._s(_vm.comparedTo)+" compared to "+_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"commits","title":"Commits / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"forks","title":"Forks / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issues","title":"Issues / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issueComments","title":"Issue Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"commitComments","title":"Commit Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pullReqComments","title":"Pull Request Comments / Week ","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pullsAcceptanceRate","title":"Pull Acceptance Rate","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"pulls","title":"Pulls Requests / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"issuesClosed","title":"Issues Closed / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('line-chart',{attrs:{"source":"totalCommitters","title":"Total Committers","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Contributors","disableRollingAverage":"1","compared-to":_vm.comparedTo}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('bubble-chart',{attrs:{"source":"contributions","title":"Contributior Overview","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty","compared-to":_vm.comparedTo}})],1)]),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('small',[_vm._v("Data provided by "),_c('a',{attrs:{"href":"http://ghtorrent.org/msr14.html"}},[_vm._v("GHTorrent")]),_vm._v(" "),_c('span',{staticClass:"ghtorrent-version"}),_vm._v(" and the "),_c('a',{attrs:{"href":"https://developer.github.com/"}},[_vm._v("GitHub API")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-7c1c00fd", __vue__options__)
  } else {
    hotAPI.reload("data-v-7c1c00fd", __vue__options__)
  }
})()}
});

;require.register("components/GHDataApp.vue", function(exports, require, module) {
;(function(){
'use strict';

var _GHDataHeader = require('./GHDataHeader.vue');

var _GHDataHeader2 = _interopRequireDefault(_GHDataHeader);

var _MainControls = require('./MainControls.vue');

var _MainControls2 = _interopRequireDefault(_MainControls);

var _GHDataCards = require('./GHDataCards.vue');

var _GHDataCards2 = _interopRequireDefault(_GHDataCards);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    'ghdata-header': _GHDataHeader2.default,
    MainControls: _MainControls2.default,
    'ghdata-cards': _GHDataCards2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('ghdata-header'),_vm._v(" "),_c('div',{staticClass:"content"},[_c('main-controls'),_vm._v(" "),_c('ghdata-cards')],1)],1)}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-f1292d0e", __vue__options__)
  } else {
    hotAPI.reload("data-v-f1292d0e", __vue__options__)
  }
})()}
});

;require.register("components/GHDataCards.vue", function(exports, require, module) {
;(function(){
'use strict';

var _BaseRepoActivityCard = require('./BaseRepoActivityCard');

var _BaseRepoActivityCard2 = _interopRequireDefault(_BaseRepoActivityCard);

var _BaseRepoEcosystemCard = require('./BaseRepoEcosystemCard');

var _BaseRepoEcosystemCard2 = _interopRequireDefault(_BaseRepoEcosystemCard);

var _ComparedRepoActivityCard = require('./ComparedRepoActivityCard');

var _ComparedRepoActivityCard2 = _interopRequireDefault(_ComparedRepoActivityCard);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    BaseRepoActivityCard: _BaseRepoActivityCard2.default,
    BaseRepoEcosystemCard: _BaseRepoEcosystemCard2.default,
    ComparedRepoActivityCard: _ComparedRepoActivityCard2.default
  },
  computed: {
    baseRepo: function baseRepo() {
      return this.$store.state.baseRepo;
    },
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    }
  },
  methods: {
    onRepo: function onRepo(e) {
      this.$store.commit('setBaseRepo', {
        url: e.target.value
      });
    },
    onCompare: function onCompare(e) {
      this.$store.commit('addComparedRepo', {
        url: e.target.value
      });
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"cards"},[_c('section',{class:{ hidden: _vm.baseRepo, unmaterialized: true }},[_c('h3',[_vm._v("Enter a GitHub URL to get started")]),_vm._v(" "),_c('input',{staticClass:"search reposearch",attrs:{"type":"text","placeholder":"GitHub URL"},on:{"change":_vm.onRepo}})]),_vm._v(" "),_c('div',{class:{ hidden: !_vm.baseRepo }},[_c('base-repo-activity-card'),_vm._v(" "),_c('base-repo-ecosystem-card')],1),_vm._v(" "),_vm._l((_vm.comparedRepos),function(repo){return _c('div',{class:{ hidden: !_vm.comparedRepos.length },attrs:{"id":"comparisonCards"}},[_c('compared-repo-activity-card',{attrs:{"comparedTo":repo}})],1)}),_vm._v(" "),_c('section',{class:{ hidden: !_vm.baseRepo, unmaterialized: true }},[_c('h3',[_vm._v("Compare repository")]),_vm._v(" "),_c('input',{staticClass:"search reposearch",attrs:{"type":"text","placeholder":"GitHub URL"},on:{"change":_vm.onCompare}})])],2)}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-323615bb", __vue__options__)
  } else {
    hotAPI.reload("data-v-323615bb", __vue__options__)
  }
})()}
});

;require.register("components/GHDataHeader.vue", function(exports, require, module) {
;(function(){
'use strict';

module.exports = {
  methods: {
    onRepo: function onRepo(e) {
      this.$store.commit('setBaseRepo', {
        url: e.target.value
      });
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('header',{staticClass:"hide-print"},[_c('div',{staticClass:"content"},[_c('div',{staticClass:"row"},[_vm._m(0),_vm._v(" "),_c('div',{staticClass:"col col-5 push-right"},[_c('div',{staticClass:"form-item"},[_c('input',{staticClass:"search reposearch",attrs:{"type":"text","name":"headersearch","placeholder":"GitHub URL"},on:{"change":_vm.onRepo}})])])])])])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"col col-4"},[_c('img',{attrs:{"src":"static/logo.png","id":"logo","alt":"CHAOSS: Community Health Analytics for Open Source Software"}})])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-30d34965", __vue__options__)
  } else {
    hotAPI.reload("data-v-30d34965", __vue__options__)
  }
})()}
});

;require.register("components/MainControls.vue", function(exports, require, module) {
;(function(){
"use strict";

module.exports = {
  methods: {
    onStartDateChange: function onStartDateChange(e) {
      var _this = this;

      var date = Date.parse(document.getElementById("start-month").value + "/01/" + document.getElementById("start-year").value);
      if (this.startDateTimeout) {
        clearTimeout(this.startDateTimeout);
      }
      this.startDateTimeout = setTimeout(function () {
        _this.$store.commit('setDates', {
          startDate: date
        });
      }, 500);
    },
    onEndDateChange: function onEndDateChange(e) {
      var _this2 = this;

      var date = Date.parse(document.getElementById("end-month").value + "/01/" + document.getElementById("end-year").value);
      if (this.endDateTimeout) {
        clearTimeout(this.endDateTimeout);
        delete this.endDateTimeout;
      }
      this.endDateTimeout = setTimeout(function () {
        _this2.$store.commit('setDates', {
          endDate: date
        });
      }, 500);
    },
    onTrailingAverageChange: function onTrailingAverageChange(e) {
      this.$store.commit('setVizOptions', {
        trailingAverage: e.target.value
      });
    },
    onRawWeeklyChange: function onRawWeeklyChange(e) {
      this.$store.commit('setVizOptions', {
        rawWeekly: e.target.checked
      });
    },
    onShowBelowAverageChange: function onShowBelowAverageChange(e) {
      this.$store.commit('setVizOptions', {
        showBelowAverage: e.target.checked
      });
    },
    onCompareChange: function onCompareChange(e) {
      this.$store.commit('setCompare', {
        compare: e.target.value
      });
    }
  },
  computed: {
    months: function months() {
      return [{ name: 'January', value: 0 }, { name: 'February', value: 1 }, { name: 'March', value: 2 }, { name: 'April', value: 3 }, { name: 'May', value: 4 }, { name: 'June', value: 5 }, { name: 'July', value: 6 }, { name: 'August', value: 7 }, { name: 'September', value: 8 }, { name: 'October', value: 9 }, { name: 'November', value: 10 }, { name: 'December', value: 11 }];
    },
    thisMonth: function thisMonth() {
      return new Date().getMonth();
    },
    thisYear: function thisYear() {
      return new Date().getUTCFullYear();
    },
    years: function years() {
      var yearArray = [];
      for (var i = 2005; i <= new Date().getUTCFullYear(); i++) {
        yearArray.push(i);
      }
      return yearArray;
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"row",attrs:{"id":"controls"}},[_c('div',{staticClass:"col col-12"},[_c('div',{staticClass:"form"},[_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-7"},[_c('h4',[_vm._v("Configuration")]),_vm._v(" "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-6"},[_c('div',{staticClass:"form-item"},[_c('label',[_vm._v("Start Date\n                    "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-7"},[_c('div',{staticClass:"form-item"},[_c('select',{attrs:{"id":"start-month"},on:{"change":_vm.onStartDateChange}},_vm._l((_vm.months),function(month){return _c('option',{domProps:{"value":month.value,"selected":month.value == 0}},[_vm._v(_vm._s(month.name))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Month")])])]),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('div',{staticClass:"form-item"},[_c('select',{attrs:{"id":"start-year"},on:{"change":_vm.onStartDateChange}},_vm._l((_vm.years),function(year){return _c('option',{domProps:{"value":year,"selected":year == 2005}},[_vm._v(_vm._s(year))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Year")])])])])])])]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('div',{staticClass:"form-item"},[_c('label',[_vm._v("End Date\n                  "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-7"},[_c('div',{staticClass:"form-item"},[_c('select',{attrs:{"id":"end-month"},on:{"change":_vm.onEndDateChange}},_vm._l((_vm.months),function(month){return _c('option',{domProps:{"value":month.value,"selected":month.value == _vm.thisMonth}},[_vm._v(_vm._s(month.name))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Month")])])]),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('div',{staticClass:"form-item"},[_c('select',{attrs:{"id":"end-year"},on:{"change":_vm.onEndDateChange}},_vm._l((_vm.years),function(year){return _c('option',{domProps:{"value":year,"selected":year == _vm.thisYear}},[_vm._v(_vm._s(year))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Year")])])])])])])])]),_vm._v(" "),_c('br'),_vm._v(" "),_c('h5',[_vm._v("Comparison Options")]),_vm._v(" "),_c('label',[_vm._v("Type\n            "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","checked":"","type":"radio"},on:{"change":_vm.onCompareChange}}),_vm._v("Z-score")]),_c('br'),_vm._v(" "),_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"percentage","type":"radio"},on:{"change":_vm.onCompareChange}}),_vm._v("Baseline is compared")])])])]),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('h4',[_vm._v("Rendering")]),_vm._v(" "),_c('label',[_vm._v("Line Charts\n        "),_c('div',{staticClass:"append"},[_c('input',{attrs:{"type":"number","min":"2","id":"averagetimespan","value":"180"},on:{"change":_vm.onTrailingAverageChange}}),_c('span',[_vm._v("day average")])]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox"},on:{"change":_vm.onRawWeeklyChange}}),_vm._v("Show raw weekly values"),_c('sup',{staticClass:"warn"})]),_c('br')])]),_vm._v(" "),_c('br'),_vm._v(" "),_c('label',[_vm._v("Bubble Charts\n          "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox"},on:{"change":_vm.onShowBelowAverageChange}}),_vm._v("Show users with below-average total contributions"),_c('sup',{staticClass:"warn"})]),_c('br')])]),_vm._v(" "),_c('small',{staticClass:"warn"},[_vm._v(" - These options affect performance")])])])])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-4eb76a08", __vue__options__)
  } else {
    hotAPI.reload("data-v-4eb76a08", __vue__options__)
  }
})()}
});

;require.register("components/charts/BubbleChart.vue", function(exports, require, module) {
;(function(){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require("vuex");

var spec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
  "spec": {
    "hconcat": [{
      "title": "Code Engagement",
      "width": 375,
      "height": 300,
      "mark": "circle",
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover"
        }
      },
      "encoding": {
        "x": {
          "field": "commit_comments",
          "type": "quantitative"
        },
        "y": {
          "field": "commits",
          "type": "quantitative",
          "scale": {
            "type": "sqrt"
          }
        },
        "color": {
          "condition": {
            "selection": "paintbrush",
            "field": "repo",
            "type": "nominal",
            "scale": { "range": ['#FF3647', '#4736FF'] }
          },
          "value": "grey"
        },
        "size": {
          "field": "total",
          "type": "quantitative",
          "legend": {
            "title": "all contributions"
          },
          "scale": {
            "type": "sqrt"
          }
        }
      }
    }, {
      "title": "Community Engagement",
      "width": 375,
      "height": 300,
      "mark": "circle",
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover"
        }
      },
      "encoding": {
        "x": {
          "field": "issue_comments",
          "type": "quantitative",
          "scale": {
            "type": "sqrt",
            "bandPaddingInner": 3
          },
          "axis": {
            "tickCount": 10
          }
        },
        "y": {
          "field": "issues",
          "type": "quantitative",
          "scale": {
            "type": "sqrt"
          }
        },
        "size": {
          "field": "total",
          "type": "quantitative",
          "legend": {
            "title": "all contributions"
          },
          "scale": {
            "type": "sqrt"
          }
        },
        "color": {
          "condition": {
            "selection": "paintbrush",
            "field": "repo",
            "type": "nominal",
            "scale": { "range": ['#FF3647', '#4736FF'] }
          },
          "value": "grey"
        }
      }
    }]
  }
};

exports.default = {
  props: ['citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'comparedTo'],
  data: function data() {
    return {
      values: []
    };
  },

  components: {
    'vega-interactive': VueVega.mapVegaLiteSpec(spec)
  },
  computed: {
    repo: function repo() {
      console.log('chart', this.$refs.vega);
      return this.$store.state.baseRepo;
    },
    chart: function chart() {
      var _this = this;

      $(this.$el).find('.showme').addClass('invis');
      $(this.$el).find('.bubblechart').addClass('loader');
      var shared = {};
      if (this.repo) {
        window.GHDataRepos[this.repo].contributors().then(function (data) {
          shared.baseData = data.map(function (e) {
            e.repo = _this.repo.toString();return e;
          });
          shared.baseData = data;
          if (_this.comparedTo) {
            return window.GHDataRepos[_this.comparedTo].contributors();
          } else {
            return new Promise(function (resolve, reject) {
              resolve();
            });
          }
        }).then(function (compareData) {
          if (compareData) {
            compareData = compareData.map(function (e) {
              e.repo = _this.comparedTo;return e;
            });
            _this.values = _.concat(shared.baseData, compareData);
          } else {
            _this.values = shared.baseData;
          }
          console.log('final chart', _this.$refs.vega);
          $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
          $(_this.$el).find('.bubblechart').removeClass('loader');
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"bubblechart hidefirst invis"},[_c('vega-interactive',{ref:"vega",attrs:{"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-273cda36", __vue__options__)
  } else {
    hotAPI.reload("data-v-273cda36", __vue__options__)
  }
})()}
});

;require.register("components/charts/DependencyOverview.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _GHDataStats = require('../../GHDataStats');

var _GHDataStats2 = _interopRequireDefault(_GHDataStats);

var _d = require('d3');

var d3 = _interopRequireWildcard(_d);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: [],
  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    dependencies: function dependencies() {
      var _this = this;

      if (this.repo) {
        window.GHDataRepos[this.repo].dependents().then(function (dependents) {
          _this.$refs['dependents'].innerHTML = '';
          for (var i = 0; i < dependents.length && i < 10; i++) {
            _this.$refs['dependents'].innerHTML += dependents[i].name + '<br>';
          }
        });
        window.GHDataRepos[this.repo].dependencies().then(function (dependencies) {
          _this.$refs['dependencies'].innerHTML = '';
          for (var i = 0; i < dependencies.dependencies.length && i < 10; i++) {
            _this.$refs['dependents'].innerHTML += dependencies.dependencies[i].name + '<br>';
          }
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('h3',[_vm._v("Top Dependents")]),_vm._v(" "),_c('div',{ref:"dependents",staticClass:"deps"},[_vm._v("\n        Loading...\n      ")])]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('h3',[_vm._v("Top Dependencies")]),_vm._v(" "),_c('div',{ref:"dependencies",staticClass:"deps",domProps:{"innerHTML":_vm._s(_vm.dependencies)}},[_vm._v("\n        Loading...\n      ")])])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-210450fe", __vue__options__)
  } else {
    hotAPI.reload("data-v-210450fe", __vue__options__)
  }
})()}
});

;require.register("components/charts/EmptyChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _GHDataStats = require('../../GHDataStats');

var _GHDataStats2 = _interopRequireDefault(_GHDataStats);

var _d = require('d3');

var d3 = _interopRequireWildcard(_d);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  computed: {
    chart: function chart() {
      MG.data_graphic({
        title: "Missing Data",
        error: 'Data unavaliable',
        chart_type: 'missing-data',
        missing_text: 'Data could not be loaded',
        target: this.$refs.chart,
        full_width: true,
        height: 200
      });
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"chart",staticClass:"linechart"})}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-ebdae2a4", __vue__options__)
  } else {
    hotAPI.reload("data-v-ebdae2a4", __vue__options__)
  }
})()}
});

;require.register("components/charts/LineChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _GHDataStats = require('GHDataStats');

var _GHDataStats2 = _interopRequireDefault(_GHDataStats);

var _vuex = require('vuex');

var _EmptyChart = require('./EmptyChart');

var _EmptyChart2 = _interopRequireDefault(_EmptyChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'percentage', 'comparedTo', 'disableRollingAverage', 'alwaysByDate'],
  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    period: function period() {
      return this.$store.state.trailingAverage;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    compare: function compare() {
      return this.$store.state.compare;
    },
    chart: function chart() {
      var _this = this;

      var config = {};

      config.earliest = this.earliest || new Date('01-01-2005');
      config.latest = this.latest || new Date();
      config.title = this.title || "Activity";
      config.full_width = true;
      config.height = 200;
      config.x_accessor = 'date';
      config.format = this.percentage ? 'percentage' : undefined;
      config.compare = this.compare;
      config.byDate = true;
      config.time_series = true;


      this.__download_data = {};
      this.__download_file = config.title.replace(/ /g, '-').replace('/', 'by').toLowerCase();

      var renderChart = function renderChart() {
        $(_this.$refs.holder).find('.showme').removeClass('invis');
        _this.$refs.chartholder.innerHTML = '';
        _this.$refs.chartholder.appendChild(config.target);
        _this.$refs.chart.className = 'linechart';
        MG.data_graphic(config);
      };

      if (this.repo) {
        if (this.$refs.chart) {
          this.$refs.chart.className = 'linechart loader';
          $(this.$refs.holder).find('.hideme').addClass('invis');
          $(this.$refs.holder).find('.showme').removeClass('invis');
        }

        config.target = document.createElement('div');
        window.GHDataRepos[this.repo][this.source]().then(function (baseData) {
          _this.__download_data.base = baseData;
          _this.$refs.chartStatus.innerHTML = '';
          if (baseData && baseData.length) {
            config.data = _GHDataStats2.default.convertDates(baseData, _this.earliest, _this.latest);
          } else {
            config.data = [];
          }
          if (_this.comparedTo) {
            return window.GHDataRepos[_this.comparedTo][_this.source]();
          }
          return new Promise(function (resolve, reject) {
            resolve();
          });
        }).then(function (compareData) {
          _this.__download_data.compare = compareData;
          _this.$refs.downloadJSON.href = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(_this.__download_data));
          _this.$refs.downloadJSON.setAttribute('download', _this.__download_file + '.json');
          var keys = Object.keys(config.data[0]).splice(1);
          if (config.data && compareData && compareData.length) {
            if (config.compare == 'each') {
              compareData = _GHDataStats2.default.convertDates(compareData, _this.earliest, _this.latest);
              var key = Object.keys(compareData[0])[1];
              var compare = _GHDataStats2.default.rollingAverage(_GHDataStats2.default.zscores(compareData, key), 'value', _this.period);
              var base = _GHDataStats2.default.rollingAverage(_GHDataStats2.default.zscores(config.data, key), 'value', _this.period);
              config.data = [base, compare];
              config.legend = [window.GHDataRepos[_this.repo].toString(), window.GHDataRepos[_this.comparedTo].toString()];
              config.colors = config.colors || ['#FF3647', '#999'];
            } else {
              config.format = 'percentage';
              config.baselines = [{ value: 1, label: config.baseline }];
              config.data = _GHDataStats2.default.makeRelative(config.data, compareData, {
                earliest: config.earliest,
                latest: config.latest,
                byDate: config.byDate,
                period: _this.period
              });
              config.x_accessor = config.byDate ? 'date' : 'x';
            }
          } else {
            if (!_this.disableRollingAverage) {
              config.legend = config.legend || [config.title.toLowerCase(), _this.period + ' day average'];
              var rolling = _GHDataStats2.default.rollingAverage(config.data, keys[0], _this.period);
              config.data = _GHDataStats2.default.combine(config.data, rolling);
              config.colors = config.colors || ['#CCC', '#FF3647'];
              config.y_accessor = 'value';
            } else {
              config.legend = config.legend || [config.title.toLowerCase()];
              config.colors = config.colors || ['#CCC', '#FF3647'];
              config.y_accessor = 'value';
            }
            config.data = _GHDataStats2.default.convertKey(config.data, keys[0]);
          }

          config.y_mouseover = '%d';

          config.legend_target = _this.$refs.legend;

          _this.$refs.chart.className = 'linechart intro';
          $(_this.$refs.holder).find('.hideme').removeClass('invis');

          $(config.target).hover(function (onEnterEvent) {
            $(_this.$refs.legend).hide();
          }, function (onLeaveEvent) {
            $(_this.$refs.legend).show();
          });
          renderChart();
        }).catch(function (reject) {
          config = {
            error: config.title + 'is missing data',
            chart_type: 'missing-data',
            missing_text: config.title + ' is missing data',
            target: config.target,
            full_width: true,
            height: 200
          };
          renderChart();
        });
        return '<div class="loader">' + this.title + '...</div>';
      }
    }
  },
  methods: {
    downloadSVG: function downloadSVG(e) {
      var svgsaver = new SvgSaver();
      var svg = $(this.$refs.chartholder).find("svg")[0];
      svgsaver.asSvg(svg, this.__download_file + '.svg');
    },
    downloadPNG: function downloadPNG(e) {
      var svgsaver = new SvgSaver();
      var svg = $(this.$refs.chartholder).find("svg")[0];
      svgsaver.asPng(svg, this.__download_file + '.png');
    }
  } };
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{ref:"chart",staticClass:"linechart"},[_c('div',{ref:"legend",staticClass:"legend hideme invis"}),_vm._v(" "),_c('div',{ref:"chartholder"}),_vm._v(" "),_c('span',{ref:"chartStatus",staticClass:"showme",domProps:{"innerHTML":_vm._s(_vm.chart)}})]),_vm._v(" "),_c('div',{staticClass:"row below-chart hideme invis"},[_c('div',{staticClass:"col col-6"},[_c('cite',{staticClass:"metric"},[_vm._v("Metric: "),_c('a',{attrs:{"href":_vm.citeUrl,"target":"_blank"}},[_vm._v(_vm._s(_vm.citeText))])])]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('button',{staticClass:"button download graph-download",on:{"click":_vm.downloadSVG}},[_vm._v("⬇ SVG")]),_c('button',{staticClass:"button graph-download download",on:{"click":_vm.downloadPNG}},[_vm._v("⬇ PNG")]),_c('a',{ref:"downloadJSON",staticClass:"button graph-download download",attrs:{"role":"button"}},[_vm._v("⬇ JSON")])])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-4035d73d", __vue__options__)
  } else {
    hotAPI.reload("data-v-4035d73d", __vue__options__)
  }
})()}
});

;require.register("components/charts/StackedBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

exports.default = {
  props: ['citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate'],
  data: function data() {
    return {
      values: []
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    spec: function spec() {
      return {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": { "values": [] },
        "title": "Issue Activity",
        "width": this.$el ? this.$el.offestWidth : 800,
        "height": 400,
        "autosize": "fit",
        "mark": "bar",
        "encoding": {
          "y": { "aggregate": "sum",
            "field": "count",
            "type": "quantitative" },
          "x": { "field": "date",
            "type": "temporal" },
          "color": { "field": "action",
            "type": "nominal" }
        }
      };
    },
    chart: function chart() {
      var _this = this;

      $(this.$el).find('.showme').addClass('invis');
      $(this.$el).find('.stackedbarchart').addClass('loader');
      console.log('called chart()', this.repo);
      if (this.repo) {
        window.GHDataRepos[this.repo].issueActivity().then(function (data) {
          $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
          $(_this.$el).find('.stackedbarchart').removeClass('loader');
          _this.values = data;
          console.log(_this.values);
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"stackedbarchart hidefirst invis"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-6c07ac85", __vue__options__)
  } else {
    hotAPI.reload("data-v-6c07ac85", __vue__options__)
  }
})()}
});

;require.register("include/kube/kube.js", function(exports, require, module) {
'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

/*
	Kube. CSS & JS Framework
	Version 6.5.2
	Updated: February 2, 2017

	http://imperavi.com/kube/

	Copyright (c) 2009-2017, Imperavi LLC.
	License: MIT
*/
if (typeof jQuery === 'undefined') {
	throw new Error('Kube\'s requires jQuery');
};
;(function ($) {
	var version = $.fn.jquery.split('.');if (version[0] == 1 && version[1] < 8) {
		throw new Error('Kube\'s requires at least jQuery v1.8');
	}
})(jQuery);

;(function () {
	// Inherits
	Function.prototype.inherits = function (parent) {
		var F = function F() {};
		F.prototype = parent.prototype;
		var f = new F();

		for (var prop in this.prototype) {
			f[prop] = this.prototype[prop];
		}this.prototype = f;
		this.prototype.super = parent.prototype;
	};

	// Core Class
	var Kube = function Kube(element, options) {
		options = (typeof options === 'undefined' ? 'undefined' : _typeof(options)) === 'object' ? options : {};

		this.$element = $(element);
		this.opts = $.extend(true, this.defaults, $.fn[this.namespace].options, this.$element.data(), options);
		this.$target = typeof this.opts.target === 'string' ? $(this.opts.target) : null;
	};

	// Core Functionality
	Kube.prototype = {
		getInstance: function getInstance() {
			return this.$element.data('fn.' + this.namespace);
		},
		hasTarget: function hasTarget() {
			return !(this.$target === null);
		},
		callback: function callback(type) {
			var args = [].slice.call(arguments).splice(1);

			// on element callback
			if (this.$element) {
				args = this._fireCallback($._data(this.$element[0], 'events'), type, this.namespace, args);
			}

			// on target callback
			if (this.$target) {
				args = this._fireCallback($._data(this.$target[0], 'events'), type, this.namespace, args);
			}

			// opts callback
			if (this.opts && this.opts.callbacks && $.isFunction(this.opts.callbacks[type])) {
				return this.opts.callbacks[type].apply(this, args);
			}

			return args;
		},
		_fireCallback: function _fireCallback(events, type, eventNamespace, args) {
			if (events && typeof events[type] !== 'undefined') {
				var len = events[type].length;
				for (var i = 0; i < len; i++) {
					var namespace = events[type][i].namespace;
					if (namespace === eventNamespace) {
						var value = events[type][i].handler.apply(this, args);
					}
				}
			}

			return typeof value === 'undefined' ? args : value;
		}
	};

	// Scope
	window.Kube = Kube;
})();
/**
 * @library Kube Plugin
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Plugin = {
		create: function create(classname, pluginname) {
			pluginname = typeof pluginname === 'undefined' ? classname.toLowerCase() : pluginname;

			$.fn[pluginname] = function (method, options) {
				var args = Array.prototype.slice.call(arguments, 1);
				var name = 'fn.' + pluginname;
				var val = [];

				this.each(function () {
					var $this = $(this),
					    data = $this.data(name);
					options = (typeof method === 'undefined' ? 'undefined' : _typeof(method)) === 'object' ? method : options;

					if (!data) {
						// Initialization
						$this.data(name, {});
						$this.data(name, data = new Kube[classname](this, options));
					}

					// Call methods
					if (typeof method === 'string') {
						if ($.isFunction(data[method])) {
							var methodVal = data[method].apply(data, args);
							if (methodVal !== undefined) {
								val.push(methodVal);
							}
						} else {
							$.error('No such method "' + method + '" for ' + classname);
						}
					}
				});

				return val.length === 0 || val.length === 1 ? val.length === 0 ? this : val[0] : val;
			};

			$.fn[pluginname].options = {};

			return this;
		},
		autoload: function autoload(pluginname) {
			var arr = pluginname.split(',');
			var len = arr.length;

			for (var i = 0; i < len; i++) {
				var name = arr[i].toLowerCase().split(',').map(function (s) {
					return s.trim();
				}).join(',');
				this.autoloadQueue.push(name);
			}

			return this;
		},
		autoloadQueue: [],
		startAutoload: function startAutoload() {
			if (!window.MutationObserver || this.autoloadQueue.length === 0) {
				return;
			}

			var self = this;
			var observer = new MutationObserver(function (mutations) {
				mutations.forEach(function (mutation) {
					var newNodes = mutation.addedNodes;
					if (newNodes.length === 0 || newNodes.length === 1 && newNodes.nodeType === 3) {
						return;
					}

					self.startAutoloadOnce();
				});
			});

			// pass in the target node, as well as the observer options
			observer.observe(document, {
				subtree: true,
				childList: true
			});
		},
		startAutoloadOnce: function startAutoloadOnce() {
			var self = this;
			var $nodes = $('[data-component]').not('[data-loaded]');
			$nodes.each(function () {
				var $el = $(this);
				var pluginname = $el.data('component');

				if (self.autoloadQueue.indexOf(pluginname) !== -1) {
					$el.attr('data-loaded', true);
					$el[pluginname]();
				}
			});
		},
		watch: function watch() {
			Kube.Plugin.startAutoloadOnce();
			Kube.Plugin.startAutoload();
		}
	};

	$(window).on('load', function () {
		Kube.Plugin.watch();
	});
})(Kube);
/**
 * @library Kube Animation
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Animation = function (element, effect, callback) {
		this.namespace = 'animation';
		this.defaults = {};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.effect = effect;
		this.completeCallback = typeof callback === 'undefined' ? false : callback;
		this.prefixes = ['', '-moz-', '-o-animation-', '-webkit-'];
		this.queue = [];

		this.start();
	};

	Kube.Animation.prototype = {
		start: function start() {
			if (this.isSlideEffect()) this.setElementHeight();

			this.addToQueue();
			this.clean();
			this.animate();
		},
		addToQueue: function addToQueue() {
			this.queue.push(this.effect);
		},
		setElementHeight: function setElementHeight() {
			this.$element.height(this.$element.height());
		},
		removeElementHeight: function removeElementHeight() {
			this.$element.css('height', '');
		},
		isSlideEffect: function isSlideEffect() {
			return this.effect === 'slideDown' || this.effect === 'slideUp';
		},
		isHideableEffect: function isHideableEffect() {
			var effects = ['fadeOut', 'slideUp', 'flipOut', 'zoomOut', 'slideOutUp', 'slideOutRight', 'slideOutLeft'];

			return $.inArray(this.effect, effects) !== -1;
		},
		isToggleEffect: function isToggleEffect() {
			return this.effect === 'show' || this.effect === 'hide';
		},
		storeHideClasses: function storeHideClasses() {
			if (this.$element.hasClass('hide-sm')) this.$element.data('hide-sm-class', true);else if (this.$element.hasClass('hide-md')) this.$element.data('hide-md-class', true);
		},
		revertHideClasses: function revertHideClasses() {
			if (this.$element.data('hide-sm-class')) this.$element.addClass('hide-sm').removeData('hide-sm-class');else if (this.$element.data('hide-md-class')) this.$element.addClass('hide-md').removeData('hide-md-class');else this.$element.addClass('hide');
		},
		removeHideClass: function removeHideClass() {
			if (this.$element.data('hide-sm-class')) this.$element.removeClass('hide-sm');else if (this.$element.data('hide-md-class')) this.$element.removeClass('hide-md');else this.$element.removeClass('hide');
		},
		animate: function animate() {
			this.storeHideClasses();
			if (this.isToggleEffect()) {
				return this.makeSimpleEffects();
			}

			this.$element.addClass('kubeanimated');
			this.$element.addClass(this.queue[0]);
			this.removeHideClass();

			var _callback = this.queue.length > 1 ? null : this.completeCallback;
			this.complete('AnimationEnd', $.proxy(this.makeComplete, this), _callback);
		},
		makeSimpleEffects: function makeSimpleEffects() {
			if (this.effect === 'show') this.removeHideClass();else if (this.effect === 'hide') this.revertHideClasses();

			if (typeof this.completeCallback === 'function') this.completeCallback(this);
		},
		makeComplete: function makeComplete() {
			if (this.$element.hasClass(this.queue[0])) {
				this.clean();
				this.queue.shift();

				if (this.queue.length) this.animate();
			}
		},
		complete: function complete(type, make, callback) {
			var event = type.toLowerCase() + ' webkit' + type + ' o' + type + ' MS' + type;

			this.$element.one(event, $.proxy(function () {
				if (typeof make === 'function') make();
				if (this.isHideableEffect()) this.revertHideClasses();
				if (this.isSlideEffect()) this.removeElementHeight();
				if (typeof callback === 'function') callback(this);

				this.$element.off(event);
			}, this));
		},
		clean: function clean() {
			this.$element.removeClass('kubeanimated').removeClass(this.queue[0]);
		}
	};

	// Inheritance
	Kube.Animation.inherits(Kube);
})(Kube);

// Plugin
(function ($) {
	$.fn.animation = function (effect, callback) {
		var name = 'fn.animation';

		return this.each(function () {
			var $this = $(this),
			    data = $this.data(name);

			$this.data(name, {});
			$this.data(name, data = new Kube.Animation(this, effect, callback));
		});
	};

	$.fn.animation.options = {};
})(jQuery);
/**
 * @library Kube Detect
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Detect = function () {};

	Kube.Detect.prototype = {
		isMobile: function isMobile() {
			return (/(iPhone|iPod|BlackBerry|Android)/.test(navigator.userAgent)
			);
		},
		isDesktop: function isDesktop() {
			return !/(iPhone|iPod|iPad|BlackBerry|Android)/.test(navigator.userAgent);
		},
		isMobileScreen: function isMobileScreen() {
			return $(window).width() <= 768;
		},
		isTabletScreen: function isTabletScreen() {
			return $(window).width() >= 768 && $(window).width() <= 1024;
		},
		isDesktopScreen: function isDesktopScreen() {
			return $(window).width() > 1024;
		}
	};
})(Kube);
/**
 * @library Kube FormData
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.FormData = function (app) {
		this.opts = app.opts;
	};

	Kube.FormData.prototype = {
		set: function set(data) {
			this.data = data;
		},
		get: function get(formdata) {
			this.formdata = formdata;

			if (this.opts.appendForms) this.appendForms();
			if (this.opts.appendFields) this.appendFields();

			return this.data;
		},
		appendFields: function appendFields() {
			var $fields = $(this.opts.appendFields);
			if ($fields.length === 0) {
				return;
			}

			var self = this;
			var str = '';

			if (this.formdata) {
				$fields.each(function () {
					self.data.append($(this).attr('name'), $(this).val());
				});
			} else {
				$fields.each(function () {
					str += '&' + $(this).attr('name') + '=' + $(this).val();
				});

				this.data = this.data === '' ? str.replace(/^&/, '') : this.data + str;
			}
		},
		appendForms: function appendForms() {
			var $forms = $(this.opts.appendForms);
			if ($forms.length === 0) {
				return;
			}

			if (this.formdata) {
				var self = this;
				var formsData = $(this.opts.appendForms).serializeArray();
				$.each(formsData, function (i, s) {
					self.data.append(s.name, s.value);
				});
			} else {
				var str = $forms.serialize();

				this.data = this.data === '' ? str : this.data + '&' + str;
			}
		}
	};
})(Kube);
/**
 * @library Kube Response
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Response = function (app) {};

	Kube.Response.prototype = {
		parse: function parse(str) {
			if (str === '') return false;

			var obj = {};

			try {
				obj = JSON.parse(str);
			} catch (e) {
				return false;
			}

			if (obj[0] !== undefined) {
				for (var item in obj) {
					this.parseItem(obj[item]);
				}
			} else {
				this.parseItem(obj);
			}

			return obj;
		},
		parseItem: function parseItem(item) {
			if (item.type === 'value') {
				$.each(item.data, $.proxy(function (key, val) {
					val = val === null || val === false ? 0 : val;
					val = val === true ? 1 : val;

					$(key).val(val);
				}, this));
			} else if (item.type === 'html') {
				$.each(item.data, $.proxy(function (key, val) {
					val = val === null || val === false ? '' : val;

					$(key).html(this.stripslashes(val));
				}, this));
			} else if (item.type === 'addClass') {
				$.each(item.data, function (key, val) {
					$(key).addClass(val);
				});
			} else if (item.type === 'removeClass') {
				$.each(item.data, function (key, val) {
					$(key).removeClass(val);
				});
			} else if (item.type === 'command') {
				$.each(item.data, function (key, val) {
					$(val)[key]();
				});
			} else if (item.type === 'animation') {
				$.each(item.data, function (key, data) {
					data.opts = typeof data.opts === 'undefined' ? {} : data.opts;

					$(key).animation(data.name, data.opts);
				});
			} else if (item.type === 'location') {
				top.location.href = item.data;
			} else if (item.type === 'notify') {
				$.notify(item.data);
			}

			return item;
		},
		stripslashes: function stripslashes(str) {
			return (str + '').replace(/\0/g, '0').replace(/\\([\\'"])/g, '$1');
		}
	};
})(Kube);
/**
 * @library Kube Utils
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Utils = function () {};

	Kube.Utils.prototype = {
		disableBodyScroll: function disableBodyScroll() {
			var $body = $('html');
			var windowWidth = window.innerWidth;

			if (!windowWidth) {
				var documentElementRect = document.documentElement.getBoundingClientRect();
				windowWidth = documentElementRect.right - Math.abs(documentElementRect.left);
			}

			var isOverflowing = document.body.clientWidth < windowWidth;
			var scrollbarWidth = this.measureScrollbar();

			$body.css('overflow', 'hidden');
			if (isOverflowing) $body.css('padding-right', scrollbarWidth);
		},
		measureScrollbar: function measureScrollbar() {
			var $body = $('body');
			var scrollDiv = document.createElement('div');
			scrollDiv.className = 'scrollbar-measure';

			$body.append(scrollDiv);
			var scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
			$body[0].removeChild(scrollDiv);
			return scrollbarWidth;
		},
		enableBodyScroll: function enableBodyScroll() {
			$('html').css({ 'overflow': '', 'padding-right': '' });
		}
	};
})(Kube);
/**
 * @library Kube Message
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Message = function (element, options) {
		this.namespace = 'message';
		this.defaults = {
			closeSelector: '.close',
			closeEvent: 'click',
			animationOpen: 'fadeIn',
			animationClose: 'fadeOut',
			callbacks: ['open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Message.prototype = {
		start: function start() {
			this.$close = this.$element.find(this.opts.closeSelector);
			this.$close.on(this.opts.closeEvent + '.' + this.namespace, $.proxy(this.close, this));
			this.$element.addClass('open');
		},
		stop: function stop() {
			this.$close.off('.' + this.namespace);
			this.$element.removeClass('open');
		},
		open: function open(e) {
			if (e) e.preventDefault();

			if (!this.isOpened()) {
				this.callback('open');
				this.$element.animation(this.opts.animationOpen, $.proxy(this.onOpened, this));
			}
		},
		isOpened: function isOpened() {
			return this.$element.hasClass('open');
		},
		onOpened: function onOpened() {
			this.callback('opened');
			this.$element.addClass('open');
		},
		close: function close(e) {
			if (e) e.preventDefault();

			if (this.isOpened()) {
				this.callback('close');
				this.$element.animation(this.opts.animationClose, $.proxy(this.onClosed, this));
			}
		},
		onClosed: function onClosed() {
			this.callback('closed');
			this.$element.removeClass('open');
		}
	};

	// Inheritance
	Kube.Message.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Message');
	Kube.Plugin.autoload('Message');
})(Kube);
/**
 * @library Kube Sticky
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Sticky = function (element, options) {
		this.namespace = 'sticky';
		this.defaults = {
			classname: 'fixed',
			offset: 0, // pixels
			callbacks: ['fixed', 'unfixed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Sticky.prototype = {
		start: function start() {
			this.offsetTop = this.getOffsetTop();

			this.load();
			$(window).scroll($.proxy(this.load, this));
		},
		getOffsetTop: function getOffsetTop() {
			return this.$element.offset().top;
		},
		load: function load() {
			return this.isFix() ? this.fixed() : this.unfixed();
		},
		isFix: function isFix() {
			return $(window).scrollTop() > this.offsetTop + this.opts.offset;
		},
		fixed: function fixed() {
			this.$element.addClass(this.opts.classname).css('top', this.opts.offset + 'px');
			this.callback('fixed');
		},
		unfixed: function unfixed() {
			this.$element.removeClass(this.opts.classname).css('top', '');
			this.callback('unfixed');
		}
	};

	// Inheritance
	Kube.Sticky.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Sticky');
	Kube.Plugin.autoload('Sticky');
})(Kube);
/**
 * @library Kube Toggleme
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Toggleme = function (element, options) {
		this.namespace = 'toggleme';
		this.defaults = {
			toggleEvent: 'click',
			target: null,
			text: '',
			animationOpen: 'slideDown',
			animationClose: 'slideUp',
			callbacks: ['open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Toggleme.prototype = {
		start: function start() {
			if (!this.hasTarget()) return;

			this.$element.on(this.opts.toggleEvent + '.' + this.namespace, $.proxy(this.toggle, this));
		},
		stop: function stop() {
			this.$element.off('.' + this.namespace);
			this.revertText();
		},
		toggle: function toggle(e) {
			if (this.isOpened()) this.close(e);else this.open(e);
		},
		open: function open(e) {
			if (e) e.preventDefault();

			if (!this.isOpened()) {
				this.storeText();
				this.callback('open');
				this.$target.animation('slideDown', $.proxy(this.onOpened, this));

				// changes the text of $element with a less delay to smooth
				setTimeout($.proxy(this.replaceText, this), 100);
			}
		},
		close: function close(e) {
			if (e) e.preventDefault();

			if (this.isOpened()) {
				this.callback('close');
				this.$target.animation('slideUp', $.proxy(this.onClosed, this));
			}
		},
		isOpened: function isOpened() {
			return this.$target.hasClass('open');
		},
		onOpened: function onOpened() {
			this.$target.addClass('open');
			this.callback('opened');
		},
		onClosed: function onClosed() {
			this.$target.removeClass('open');
			this.revertText();
			this.callback('closed');
		},
		storeText: function storeText() {
			this.$element.data('replacement-text', this.$element.html());
		},
		revertText: function revertText() {
			var text = this.$element.data('replacement-text');
			if (text) this.$element.html(text);

			this.$element.removeData('replacement-text');
		},
		replaceText: function replaceText() {
			if (this.opts.text !== '') {
				this.$element.html(this.opts.text);
			}
		}
	};

	// Inheritance
	Kube.Toggleme.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Toggleme');
	Kube.Plugin.autoload('Toggleme');
})(Kube);
/**
 * @library Kube Offcanvas
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Offcanvas = function (element, options) {
		this.namespace = 'offcanvas';
		this.defaults = {
			target: null, // selector
			push: true, // boolean
			width: '250px', // string
			direction: 'left', // string: left or right
			toggleEvent: 'click',
			clickOutside: true, // boolean
			animationOpen: 'slideInLeft',
			animationClose: 'slideOutLeft',
			callbacks: ['open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Services
		this.utils = new Kube.Utils();
		this.detect = new Kube.Detect();

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Offcanvas.prototype = {
		start: function start() {
			if (!this.hasTarget()) return;

			this.buildTargetWidth();
			this.buildAnimationDirection();

			this.$close = this.getCloseLink();
			this.$element.on(this.opts.toggleEvent + '.' + this.namespace, $.proxy(this.toggle, this));
			this.$target.addClass('offcanvas');
		},
		stop: function stop() {
			this.closeAll();

			this.$element.off('.' + this.namespace);
			this.$close.off('.' + this.namespace);
			$(document).off('.' + this.namespace);
		},
		toggle: function toggle(e) {
			if (this.isOpened()) this.close(e);else this.open(e);
		},
		buildTargetWidth: function buildTargetWidth() {
			this.opts.width = $(window).width() < parseInt(this.opts.width) ? '100%' : this.opts.width;
		},
		buildAnimationDirection: function buildAnimationDirection() {
			if (this.opts.direction === 'right') {
				this.opts.animationOpen = 'slideInRight';
				this.opts.animationClose = 'slideOutRight';
			}
		},
		getCloseLink: function getCloseLink() {
			return this.$target.find('.close');
		},
		open: function open(e) {
			if (e) e.preventDefault();

			if (!this.isOpened()) {
				this.closeAll();
				this.callback('open');

				this.$target.addClass('offcanvas-' + this.opts.direction);
				this.$target.css('width', this.opts.width);

				this.pushBody();

				this.$target.animation(this.opts.animationOpen, $.proxy(this.onOpened, this));
			}
		},
		closeAll: function closeAll() {
			var $elms = $(document).find('.offcanvas');
			if ($elms.length !== 0) {
				$elms.each(function () {
					var $el = $(this);

					if ($el.hasClass('open')) {
						$el.css('width', '').animation('hide');
						$el.removeClass('open offcanvas-left offcanvas-right');
					}
				});

				$(document).off('.' + this.namespace);
				$('body').css('left', '');
			}
		},
		close: function close(e) {
			if (e) {
				var $el = $(e.target);
				var isTag = $el[0].tagName === 'A' || $el[0].tagName === 'BUTTON';
				if (isTag && $el.closest('.offcanvas').length !== 0 && !$el.hasClass('close')) {
					return;
				}

				e.preventDefault();
			}

			if (this.isOpened()) {
				this.utils.enableBodyScroll();
				this.callback('close');
				this.pullBody();
				this.$target.animation(this.opts.animationClose, $.proxy(this.onClosed, this));
			}
		},
		isOpened: function isOpened() {
			return this.$target.hasClass('open');
		},
		onOpened: function onOpened() {
			if (this.opts.clickOutside) $(document).on('click.' + this.namespace, $.proxy(this.close, this));
			if (this.detect.isMobileScreen()) $('html').addClass('no-scroll');

			$(document).on('keyup.' + this.namespace, $.proxy(this.handleKeyboard, this));
			this.$close.on('click.' + this.namespace, $.proxy(this.close, this));

			this.utils.disableBodyScroll();
			this.$target.addClass('open');
			this.callback('opened');
		},
		onClosed: function onClosed() {
			if (this.detect.isMobileScreen()) $('html').removeClass('no-scroll');

			this.$target.css('width', '').removeClass('offcanvas-' + this.opts.direction);

			this.$close.off('.' + this.namespace);
			$(document).off('.' + this.namespace);

			this.$target.removeClass('open');
			this.callback('closed');
		},
		handleKeyboard: function handleKeyboard(e) {
			if (e.which === 27) this.close();
		},
		pullBody: function pullBody() {
			if (this.opts.push) {
				$('body').animate({ left: 0 }, 350, function () {
					$(this).removeClass('offcanvas-push-body');
				});
			}
		},
		pushBody: function pushBody() {
			if (this.opts.push) {
				var properties = this.opts.direction === 'left' ? { 'left': this.opts.width } : { 'left': '-' + this.opts.width };
				$('body').addClass('offcanvas-push-body').animate(properties, 200);
			}
		}
	};

	// Inheritance
	Kube.Offcanvas.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Offcanvas');
	Kube.Plugin.autoload('Offcanvas');
})(Kube);
/**
 * @library Kube Collapse
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Collapse = function (element, options) {
		this.namespace = 'collapse';
		this.defaults = {
			target: null,
			toggle: true,
			active: false, // string (hash = tab id selector)
			toggleClass: 'collapse-toggle',
			boxClass: 'collapse-box',
			callbacks: ['open', 'opened', 'close', 'closed'],

			// private
			hashes: [],
			currentHash: false,
			currentItem: false
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Collapse.prototype = {
		start: function start() {
			// items
			this.$items = this.getItems();
			this.$items.each($.proxy(this.loadItems, this));

			// boxes
			this.$boxes = this.getBoxes();

			// active
			this.setActiveItem();
		},
		getItems: function getItems() {
			return this.$element.find('.' + this.opts.toggleClass);
		},
		getBoxes: function getBoxes() {
			return this.$element.find('.' + this.opts.boxClass);
		},
		loadItems: function loadItems(i, el) {
			var item = this.getItem(el);

			// set item identificator
			item.$el.attr('rel', item.hash);

			// active
			if (!$(item.hash).hasClass('hide')) {
				this.opts.currentItem = item;
				this.opts.active = item.hash;

				item.$el.addClass('active');
			}

			// event
			item.$el.on('click.collapse', $.proxy(this.toggle, this));
		},
		setActiveItem: function setActiveItem() {
			if (this.opts.active !== false) {
				this.opts.currentItem = this.getItemBy(this.opts.active);
				this.opts.active = this.opts.currentItem.hash;
			}

			if (this.opts.currentItem !== false) {
				this.addActive(this.opts.currentItem);
				this.opts.currentItem.$box.removeClass('hide');
			}
		},
		addActive: function addActive(item) {
			item.$box.removeClass('hide').addClass('open');
			item.$el.addClass('active');

			if (item.$caret !== false) item.$caret.removeClass('down').addClass('up');
			if (item.$parent !== false) item.$parent.addClass('active');

			this.opts.currentItem = item;
		},
		removeActive: function removeActive(item) {
			item.$box.removeClass('open');
			item.$el.removeClass('active');

			if (item.$caret !== false) item.$caret.addClass('down').removeClass('up');
			if (item.$parent !== false) item.$parent.removeClass('active');

			this.opts.currentItem = false;
		},
		toggle: function toggle(e) {
			if (e) e.preventDefault();

			var target = $(e.target).closest('.' + this.opts.toggleClass).get(0) || e.target;
			var item = this.getItem(target);

			if (this.isOpened(item.hash)) this.close(item.hash);else this.open(e);
		},
		openAll: function openAll() {
			this.$items.addClass('active');
			this.$boxes.addClass('open').removeClass('hide');
		},
		open: function open(e, push) {
			if (typeof e === 'undefined') return;
			if ((typeof e === 'undefined' ? 'undefined' : _typeof(e)) === 'object') e.preventDefault();

			var target = $(e.target).closest('.' + this.opts.toggleClass).get(0) || e.target;
			var item = (typeof e === 'undefined' ? 'undefined' : _typeof(e)) === 'object' ? this.getItem(target) : this.getItemBy(e);

			if (item.$box.hasClass('open')) {
				return;
			}

			if (this.opts.toggle) this.closeAll();

			this.callback('open', item);
			this.addActive(item);

			item.$box.animation('slideDown', $.proxy(this.onOpened, this));
		},
		onOpened: function onOpened() {
			this.callback('opened', this.opts.currentItem);
		},
		closeAll: function closeAll() {
			this.$items.removeClass('active').closest('li').removeClass('active');
			this.$boxes.removeClass('open').addClass('hide');
		},
		close: function close(num) {
			var item = this.getItemBy(num);

			this.callback('close', item);

			this.opts.currentItem = item;

			item.$box.animation('slideUp', $.proxy(this.onClosed, this));
		},
		onClosed: function onClosed() {
			var item = this.opts.currentItem;

			this.removeActive(item);
			this.callback('closed', item);
		},
		isOpened: function isOpened(hash) {
			return $(hash).hasClass('open');
		},
		getItem: function getItem(element) {
			var item = {};

			item.$el = $(element);
			item.hash = item.$el.attr('href');
			item.$box = $(item.hash);

			var $parent = item.$el.parent();
			item.$parent = $parent[0].tagName === 'LI' ? $parent : false;

			var $caret = item.$el.find('.caret');
			item.$caret = $caret.length !== 0 ? $caret : false;

			return item;
		},
		getItemBy: function getItemBy(num) {
			var element = typeof num === 'number' ? this.$items.eq(num - 1) : this.$element.find('[rel="' + num + '"]');

			return this.getItem(element);
		}
	};

	// Inheritance
	Kube.Collapse.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Collapse');
	Kube.Plugin.autoload('Collapse');
})(Kube);
/**
 * @library Kube Dropdown
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Dropdown = function (element, options) {
		this.namespace = 'dropdown';
		this.defaults = {
			target: null,
			toggleEvent: 'click',
			height: false, // integer
			width: false, // integer
			animationOpen: 'slideDown',
			animationClose: 'slideUp',
			caretUp: false,
			callbacks: ['open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Services
		this.utils = new Kube.Utils();
		this.detect = new Kube.Detect();

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Dropdown.prototype = {
		start: function start() {
			this.buildClose();
			this.buildCaret();

			if (this.detect.isMobile()) this.buildMobileAnimation();

			this.$target.addClass('hide');
			this.$element.on(this.opts.toggleEvent + '.' + this.namespace, $.proxy(this.toggle, this));
		},
		stop: function stop() {
			this.$element.off('.' + this.namespace);
			this.$target.removeClass('open').addClass('hide');
			this.disableEvents();
		},
		buildMobileAnimation: function buildMobileAnimation() {
			this.opts.animationOpen = 'fadeIn';
			this.opts.animationClose = 'fadeOut';
		},
		buildClose: function buildClose() {
			this.$close = this.$target.find('.close');
		},
		buildCaret: function buildCaret() {
			this.$caret = this.getCaret();
			this.buildCaretPosition();
		},
		buildCaretPosition: function buildCaretPosition() {
			var height = this.$element.offset().top + this.$element.innerHeight() + this.$target.innerHeight();

			if ($(document).height() > height) {
				return;
			}

			this.opts.caretUp = true;
			this.$caret.addClass('up');
		},
		getCaret: function getCaret() {
			return this.$element.find('.caret');
		},
		toggleCaretOpen: function toggleCaretOpen() {
			if (this.opts.caretUp) this.$caret.removeClass('up').addClass('down');else this.$caret.removeClass('down').addClass('up');
		},
		toggleCaretClose: function toggleCaretClose() {
			if (this.opts.caretUp) this.$caret.removeClass('down').addClass('up');else this.$caret.removeClass('up').addClass('down');
		},
		toggle: function toggle(e) {
			if (this.isOpened()) this.close(e);else this.open(e);
		},
		open: function open(e) {
			if (e) e.preventDefault();

			this.callback('open');
			$('.dropdown').removeClass('open').addClass('hide');

			if (this.opts.height) this.$target.css('min-height', this.opts.height + 'px');
			if (this.opts.width) this.$target.width(this.opts.width);

			this.setPosition();
			this.toggleCaretOpen();

			this.$target.animation(this.opts.animationOpen, $.proxy(this.onOpened, this));
		},
		close: function close(e) {
			if (!this.isOpened()) {
				return;
			}

			if (e) {
				if (this.shouldNotBeClosed(e.target)) {
					return;
				}

				e.preventDefault();
			}

			this.utils.enableBodyScroll();
			this.callback('close');
			this.toggleCaretClose();

			this.$target.animation(this.opts.animationClose, $.proxy(this.onClosed, this));
		},
		onClosed: function onClosed() {
			this.$target.removeClass('open');
			this.disableEvents();
			this.callback('closed');
		},
		onOpened: function onOpened() {
			this.$target.addClass('open');
			this.enableEvents();
			this.callback('opened');
		},
		isOpened: function isOpened() {
			return this.$target.hasClass('open');
		},
		enableEvents: function enableEvents() {
			if (this.detect.isDesktop()) {
				this.$target.on('mouseover.' + this.namespace, $.proxy(this.utils.disableBodyScroll, this.utils)).on('mouseout.' + this.namespace, $.proxy(this.utils.enableBodyScroll, this.utils));
			}

			$(document).on('scroll.' + this.namespace, $.proxy(this.setPosition, this));
			$(window).on('resize.' + this.namespace, $.proxy(this.setPosition, this));
			$(document).on('click.' + this.namespace + ' touchstart.' + this.namespace, $.proxy(this.close, this));
			$(document).on('keydown.' + this.namespace, $.proxy(this.handleKeyboard, this));
			this.$target.find('[data-action="dropdown-close"]').on('click.' + this.namespace, $.proxy(this.close, this));
		},
		disableEvents: function disableEvents() {
			this.$target.off('.' + this.namespace);
			$(document).off('.' + this.namespace);
			$(window).off('.' + this.namespace);
		},
		handleKeyboard: function handleKeyboard(e) {
			if (e.which === 27) this.close(e);
		},
		shouldNotBeClosed: function shouldNotBeClosed(el) {
			if ($(el).attr('data-action') === 'dropdown-close' || el === this.$close[0]) {
				return false;
			} else if ($(el).closest('.dropdown').length === 0) {
				return false;
			}

			return true;
		},
		isNavigationFixed: function isNavigationFixed() {
			return this.$element.closest('.fixed').length !== 0;
		},
		getPlacement: function getPlacement(height) {
			return $(document).height() < height ? 'top' : 'bottom';
		},
		getOffset: function getOffset(position) {
			return this.isNavigationFixed() ? this.$element.position() : this.$element.offset();
		},
		getPosition: function getPosition() {
			return this.isNavigationFixed() ? 'fixed' : 'absolute';
		},
		setPosition: function setPosition() {
			if (this.detect.isMobile()) {
				this.$target.addClass('dropdown-mobile');
				return;
			}

			var position = this.getPosition();
			var coords = this.getOffset(position);
			var height = this.$target.innerHeight();
			var width = this.$target.innerWidth();
			var placement = this.getPlacement(coords.top + height + this.$element.innerHeight());
			var leftFix = $(window).width() < coords.left + width ? width - this.$element.innerWidth() : 0;
			var top,
			    left = coords.left - leftFix;

			if (placement === 'bottom') {
				if (!this.isOpened()) this.$caret.removeClass('up').addClass('down');

				this.opts.caretUp = false;
				top = coords.top + this.$element.outerHeight() + 1;
			} else {
				this.opts.animationOpen = 'show';
				this.opts.animationClose = 'hide';

				if (!this.isOpened()) this.$caret.addClass('up').removeClass('down');

				this.opts.caretUp = true;
				top = coords.top - height - 1;
			}

			this.$target.css({ position: position, top: top + 'px', left: left + 'px' });
		}
	};

	// Inheritance
	Kube.Dropdown.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Dropdown');
	Kube.Plugin.autoload('Dropdown');
})(Kube);
/**
 * @library Kube Tabs
 * @author Imperavi LLC
 * @license MIT
 */
(function (Kube) {
	Kube.Tabs = function (element, options) {
		this.namespace = 'tabs';
		this.defaults = {
			equals: false,
			active: false, // string (hash = tab id selector)
			live: false, // class selector
			hash: true, //boolean
			callbacks: ['init', 'next', 'prev', 'open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Tabs.prototype = {
		start: function start() {
			if (this.opts.live !== false) this.buildLiveTabs();

			this.tabsCollection = [];
			this.hashesCollection = [];
			this.currentHash = [];
			this.currentItem = false;

			// items
			this.$items = this.getItems();
			this.$items.each($.proxy(this.loadItems, this));

			// tabs
			this.$tabs = this.getTabs();

			// location hash
			this.currentHash = this.getLocationHash();

			// close all
			this.closeAll();

			// active & height
			this.setActiveItem();
			this.setItemHeight();

			// callback
			this.callback('init');
		},
		getTabs: function getTabs() {
			return $(this.tabsCollection).map(function () {
				return this.toArray();
			});
		},
		getItems: function getItems() {
			return this.$element.find('a');
		},
		loadItems: function loadItems(i, el) {
			var item = this.getItem(el);

			// set item identificator
			item.$el.attr('rel', item.hash);

			// collect item
			this.collectItem(item);

			// active
			if (item.$parent.hasClass('active')) {
				this.currentItem = item;
				this.opts.active = item.hash;
			}

			// event
			item.$el.on('click.tabs', $.proxy(this.open, this));
		},
		collectItem: function collectItem(item) {
			this.tabsCollection.push(item.$tab);
			this.hashesCollection.push(item.hash);
		},
		buildLiveTabs: function buildLiveTabs() {
			var $layers = $(this.opts.live);

			if ($layers.length === 0) {
				return;
			}

			this.$liveTabsList = $('<ul />');
			$layers.each($.proxy(this.buildLiveItem, this));

			this.$element.html('').append(this.$liveTabsList);
		},
		buildLiveItem: function buildLiveItem(i, tab) {
			var $tab = $(tab);
			var $li = $('<li />');
			var $a = $('<a />');
			var index = i + 1;

			$tab.attr('id', this.getLiveItemId($tab, index));

			var hash = '#' + $tab.attr('id');
			var title = this.getLiveItemTitle($tab);

			$a.attr('href', hash).attr('rel', hash).text(title);
			$li.append($a);

			this.$liveTabsList.append($li);
		},
		getLiveItemId: function getLiveItemId($tab, index) {
			return typeof $tab.attr('id') === 'undefined' ? this.opts.live.replace('.', '') + index : $tab.attr('id');
		},
		getLiveItemTitle: function getLiveItemTitle($tab) {
			return typeof $tab.attr('data-title') === 'undefined' ? $tab.attr('id') : $tab.attr('data-title');
		},
		setActiveItem: function setActiveItem() {
			if (this.currentHash) {
				this.currentItem = this.getItemBy(this.currentHash);
				this.opts.active = this.currentHash;
			} else if (this.opts.active === false) {
				this.currentItem = this.getItem(this.$items.first());
				this.opts.active = this.currentItem.hash;
			}

			this.addActive(this.currentItem);
		},
		addActive: function addActive(item) {
			item.$parent.addClass('active');
			item.$tab.removeClass('hide').addClass('open');

			this.currentItem = item;
		},
		removeActive: function removeActive(item) {
			item.$parent.removeClass('active');
			item.$tab.addClass('hide').removeClass('open');

			this.currentItem = false;
		},
		next: function next(e) {
			if (e) e.preventDefault();

			var item = this.getItem(this.fetchElement('next'));

			this.open(item.hash);
			this.callback('next', item);
		},
		prev: function prev(e) {
			if (e) e.preventDefault();

			var item = this.getItem(this.fetchElement('prev'));

			this.open(item.hash);
			this.callback('prev', item);
		},
		fetchElement: function fetchElement(type) {
			var element;
			if (this.currentItem !== false) {
				// prev or next
				element = this.currentItem.$parent[type]().find('a');

				if (element.length === 0) {
					return;
				}
			} else {
				// first
				element = this.$items[0];
			}

			return element;
		},
		open: function open(e, push) {
			if (typeof e === 'undefined') return;
			if ((typeof e === 'undefined' ? 'undefined' : _typeof(e)) === 'object') e.preventDefault();

			var item = (typeof e === 'undefined' ? 'undefined' : _typeof(e)) === 'object' ? this.getItem(e.target) : this.getItemBy(e);
			this.closeAll();

			this.callback('open', item);
			this.addActive(item);

			// push state (doesn't need to push at the start)
			this.pushStateOpen(push, item);
			this.callback('opened', item);
		},
		pushStateOpen: function pushStateOpen(push, item) {
			if (push !== false && this.opts.hash !== false) {
				history.pushState(false, false, item.hash);
			}
		},
		close: function close(num) {
			var item = this.getItemBy(num);

			if (!item.$parent.hasClass('active')) {
				return;
			}

			this.callback('close', item);
			this.removeActive(item);
			this.pushStateClose();
			this.callback('closed', item);
		},
		pushStateClose: function pushStateClose() {
			if (this.opts.hash !== false) {
				history.pushState(false, false, ' ');
			}
		},
		closeAll: function closeAll() {
			this.$tabs.removeClass('open').addClass('hide');
			this.$items.parent().removeClass('active');
		},
		getItem: function getItem(element) {
			var item = {};

			item.$el = $(element);
			item.hash = item.$el.attr('href');
			item.$parent = item.$el.parent();
			item.$tab = $(item.hash);

			return item;
		},
		getItemBy: function getItemBy(num) {
			var element = typeof num === 'number' ? this.$items.eq(num - 1) : this.$element.find('[rel="' + num + '"]');

			return this.getItem(element);
		},
		getLocationHash: function getLocationHash() {
			if (this.opts.hash === false) {
				return false;
			}

			return this.isHash() ? top.location.hash : false;
		},
		isHash: function isHash() {
			return !(top.location.hash === '' || $.inArray(top.location.hash, this.hashesCollection) === -1);
		},
		setItemHeight: function setItemHeight() {
			if (this.opts.equals) {
				var minHeight = this.getItemMaxHeight() + 'px';
				this.$tabs.css('min-height', minHeight);
			}
		},
		getItemMaxHeight: function getItemMaxHeight() {
			var max = 0;
			this.$tabs.each(function () {
				var h = $(this).height();
				max = h > max ? h : max;
			});

			return max;
		}
	};

	// Inheritance
	Kube.Tabs.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Tabs');
	Kube.Plugin.autoload('Tabs');
})(Kube);
/**
 * @library Kube Modal
 * @author Imperavi LLC
 * @license MIT
 */
(function ($) {
	$.modalcurrent = null;
	$.modalwindow = function (options) {
		var opts = $.extend({}, options, { show: true });
		var $element = $('<span />');

		$element.modal(opts);
	};
})(jQuery);

(function (Kube) {
	Kube.Modal = function (element, options) {
		this.namespace = 'modal';
		this.defaults = {
			target: null,
			show: false,
			url: false,
			header: false,
			width: '600px', // string
			height: false, // or string
			maxHeight: false,
			position: 'center', // top or center
			overlay: true,
			appendForms: false,
			appendFields: false,
			animationOpen: 'show',
			animationClose: 'hide',
			callbacks: ['open', 'opened', 'close', 'closed']
		};

		// Parent Constructor
		Kube.apply(this, arguments);

		// Services
		this.utils = new Kube.Utils();
		this.detect = new Kube.Detect();

		// Initialization
		this.start();
	};

	// Functionality
	Kube.Modal.prototype = {
		start: function start() {
			if (!this.hasTarget()) {
				return;
			}

			if (this.opts.show) this.load();else this.$element.on('click.' + this.namespace, $.proxy(this.load, this));
		},
		buildModal: function buildModal() {
			this.$modal = this.$target.find('.modal');
			this.$header = this.$target.find('.modal-header');
			this.$close = this.$target.find('.close');
			this.$body = this.$target.find('.modal-body');
		},
		buildOverlay: function buildOverlay() {
			if (this.opts.overlay === false) {
				return;
			}

			if ($('#modal-overlay').length !== 0) {
				this.$overlay = $('#modal-overlay');
			} else {
				this.$overlay = $('<div id="modal-overlay">').addClass('hide');
				$('body').prepend(this.$overlay);
			}

			this.$overlay.addClass('overlay');
		},
		buildHeader: function buildHeader() {
			if (this.opts.header) this.$header.html(this.opts.header);
		},
		load: function load(e) {
			this.buildModal();
			this.buildOverlay();
			this.buildHeader();

			if (this.opts.url) this.buildContent();else this.open(e);
		},
		open: function open(e) {
			if (e) e.preventDefault();

			if (this.isOpened()) {
				return;
			}

			if (this.detect.isMobile()) this.opts.width = '96%';
			if (this.opts.overlay) this.$overlay.removeClass('hide');

			this.$target.removeClass('hide');
			this.$modal.removeClass('hide');

			this.enableEvents();
			this.findActions();

			this.resize();
			$(window).on('resize.' + this.namespace, $.proxy(this.resize, this));

			if (this.detect.isDesktop()) this.utils.disableBodyScroll();

			// enter
			this.$modal.find('input[type=text],input[type=url],input[type=email]').on('keydown.' + this.namespace, $.proxy(this.handleEnter, this));

			this.callback('open');
			this.$modal.animation(this.opts.animationOpen, $.proxy(this.onOpened, this));
		},
		close: function close(e) {
			if (!this.$modal || !this.isOpened()) {
				return;
			}

			if (e) {
				if (this.shouldNotBeClosed(e.target)) {
					return;
				}

				e.preventDefault();
			}

			this.callback('close');
			this.disableEvents();

			this.$modal.animation(this.opts.animationClose, $.proxy(this.onClosed, this));

			if (this.opts.overlay) this.$overlay.animation(this.opts.animationClose);
		},
		onOpened: function onOpened() {
			this.$modal.addClass('open');
			this.callback('opened');

			$.modalcurrent = this;
		},
		onClosed: function onClosed() {
			this.callback('closed');

			this.$target.addClass('hide');
			this.$modal.removeClass('open');

			if (this.detect.isDesktop()) this.utils.enableBodyScroll();

			this.$body.css('height', '');
			$.modalcurrent = null;
		},
		isOpened: function isOpened() {
			return this.$modal.hasClass('open');
		},
		getData: function getData() {
			var formdata = new Kube.FormData(this);
			formdata.set('');

			return formdata.get();
		},
		buildContent: function buildContent() {
			$.ajax({
				url: this.opts.url + '?' + new Date().getTime(),
				cache: false,
				type: 'post',
				data: this.getData(),
				success: $.proxy(function (data) {
					this.$body.html(data);
					this.open();
				}, this)
			});
		},
		buildWidth: function buildWidth() {
			var width = this.opts.width;
			var top = '2%';
			var bottom = '2%';
			var percent = width.match(/%$/);

			if (parseInt(this.opts.width) > $(window).width() && !percent) {
				width = '96%';
			} else if (!percent) {
				top = '16px';
				bottom = '16px';
			}

			this.$modal.css({ 'width': width, 'margin-top': top, 'margin-bottom': bottom });
		},
		buildPosition: function buildPosition() {
			if (this.opts.position !== 'center') {
				return;
			}

			var windowHeight = $(window).height();
			var height = this.$modal.outerHeight();
			var top = windowHeight / 2 - height / 2 + 'px';

			if (this.detect.isMobile()) top = '2%';else if (height > windowHeight) top = '16px';

			this.$modal.css('margin-top', top);
		},
		buildHeight: function buildHeight() {
			var windowHeight = $(window).height();

			if (this.opts.maxHeight) {
				var padding = parseInt(this.$body.css('padding-top')) + parseInt(this.$body.css('padding-bottom'));
				var margin = parseInt(this.$modal.css('margin-top')) + parseInt(this.$modal.css('margin-bottom'));
				var height = windowHeight - this.$header.innerHeight() - padding - margin;

				this.$body.height(height);
			} else if (this.opts.height !== false) {
				this.$body.css('height', this.opts.height);
			}

			var modalHeight = this.$modal.outerHeight();
			if (modalHeight > windowHeight) {
				this.opts.animationOpen = 'show';
				this.opts.animationClose = 'hide';
			}
		},
		resize: function resize() {
			this.buildWidth();
			this.buildPosition();
			this.buildHeight();
		},
		enableEvents: function enableEvents() {
			this.$close.on('click.' + this.namespace, $.proxy(this.close, this));
			$(document).on('keyup.' + this.namespace, $.proxy(this.handleEscape, this));
			this.$target.on('click.' + this.namespace, $.proxy(this.close, this));
		},
		disableEvents: function disableEvents() {
			this.$close.off('.' + this.namespace);
			$(document).off('.' + this.namespace);
			this.$target.off('.' + this.namespace);
			$(window).off('.' + this.namespace);
		},
		findActions: function findActions() {
			this.$body.find('[data-action="modal-close"]').on('mousedown.' + this.namespace, $.proxy(this.close, this));
		},
		setHeader: function setHeader(header) {
			this.$header.html(header);
		},
		setContent: function setContent(content) {
			this.$body.html(content);
		},
		setWidth: function setWidth(width) {
			this.opts.width = width;
			this.resize();
		},
		getModal: function getModal() {
			return this.$modal;
		},
		getBody: function getBody() {
			return this.$body;
		},
		getHeader: function getHeader() {
			return this.$header;
		},
		handleEnter: function handleEnter(e) {
			if (e.which === 13) {
				e.preventDefault();
				this.close(false);
			}
		},
		handleEscape: function handleEscape(e) {
			return e.which === 27 ? this.close(false) : true;
		},
		shouldNotBeClosed: function shouldNotBeClosed(el) {
			if ($(el).attr('data-action') === 'modal-close' || el === this.$close[0]) {
				return false;
			} else if ($(el).closest('.modal').length === 0) {
				return false;
			}

			return true;
		}
	};

	// Inheritance
	Kube.Modal.inherits(Kube);

	// Plugin
	Kube.Plugin.create('Modal');
	Kube.Plugin.autoload('Modal');
})(Kube);
});

require.register("include/svgsaver.js", function(exports, require, module) {
'use strict';

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

Object.defineProperty(exports, '__esModule', {
  value: true
});

var _createClass = function () {
  function defineProperties(target, props) {
    for (var i = 0; i < props.length; i++) {
      var descriptor = props[i];descriptor.enumerable = descriptor.enumerable || false;descriptor.configurable = true;if ('value' in descriptor) descriptor.writable = true;Object.defineProperty(target, descriptor.key, descriptor);
    }
  }return function (Constructor, protoProps, staticProps) {
    if (protoProps) defineProperties(Constructor.prototype, protoProps);if (staticProps) defineProperties(Constructor, staticProps);return Constructor;
  };
}();

function _interopRequireDefault(obj) {
  return obj && obj.__esModule ? obj : { 'default': obj };
}

function _classCallCheck(instance, Constructor) {
  if (!(instance instanceof Constructor)) {
    throw new TypeError('Cannot call a class as a function');
  }
}

var _computedStyles = require('computed-styles');

var _computedStyles2 = _interopRequireDefault(_computedStyles);

var _fileSaver = require('file-saver');

var _fileSaver2 = _interopRequireDefault(_fileSaver);

var svgStyles = { // Whitelist of CSS styles and default values
  'alignment-baseline': 'auto',
  'baseline-shift': 'baseline',
  'clip': 'auto',
  'clip-path': 'none',
  'clip-rule': 'nonzero',
  'color': 'rgb(51, 51, 51)',
  'color-interpolation': 'srgb',
  'color-interpolation-filters': 'linearrgb',
  'color-profile': 'auto',
  'color-rendering': 'auto',
  'cursor': 'auto',
  'direction': 'ltr',
  'display': 'inline',
  'dominant-baseline': 'auto',
  'enable-background': '',
  'fill': 'rgb(0, 0, 0)',
  'fill-opacity': '1',
  'fill-rule': 'nonzero',
  'filter': 'none',
  'flood-color': 'rgb(0, 0, 0)',
  'flood-opacity': '1',
  'font': '',
  'font-family': 'normal',
  'font-size': 'medium',
  'font-size-adjust': 'auto',
  'font-stretch': 'normal',
  'font-style': 'normal',
  'font-variant': 'normal',
  'font-weight': '400',
  'glyph-orientation-horizontal': '0deg',
  'glyph-orientation-vertical': 'auto',
  'image-rendering': 'auto',
  'kerning': 'auto',
  'letter-spacing': '0',
  'lighting-color': 'rgb(255, 255, 255)',
  'marker': '',
  'marker-end': 'none',
  'marker-mid': 'none',
  'marker-start': 'none',
  'mask': 'none',
  'opacity': '1',
  'overflow': 'visible',
  'paint-order': 'fill',
  'pointer-events': 'auto',
  'shape-rendering': 'auto',
  'stop-color': 'rgb(0, 0, 0)',
  'stop-opacity': '1',
  'stroke': 'none',
  'stroke-dasharray': 'none',
  'stroke-dashoffset': '0',
  'stroke-linecap': 'butt',
  'stroke-linejoin': 'miter',
  'stroke-miterlimit': '4',
  'stroke-opacity': '1',
  'stroke-width': '1',
  'text-anchor': 'start',
  'text-decoration': 'none',
  'text-rendering': 'auto',
  'unicode-bidi': 'normal',
  'visibility': 'visible',
  'word-spacing': '0px',
  'writing-mode': 'lr-tb'
};

var svgAttrs = [// white list of attributes
'id', 'xml: base', 'xml: lang', 'xml: space', // Core
'height', 'result', 'width', 'x', 'y', // Primitive
'xlink: href', // Xlink attribute
'href', 'style', 'class', 'd', 'pathLength', // Path
'x', 'y', 'dx', 'dy', 'glyphRef', 'format', 'x1', 'y1', 'x2', 'y2', 'rotate', 'textLength', 'cx', 'cy', 'r', 'rx', 'ry', 'fx', 'fy', 'width', 'height', 'refX', 'refY', 'orient', 'markerUnits', 'markerWidth', 'markerHeight', 'maskUnits', 'transform', 'viewBox', 'version', // Container
'preserveAspectRatio', 'xmlns', 'points', // Polygons
'offset', 'xlink:href'];

// http://www.w3.org/TR/SVG/propidx.html
// via https://github.com/svg/svgo/blob/master/plugins/_collections.js
var inheritableAttrs = ['clip-rule', 'color', 'color-interpolation', 'color-interpolation-filters', 'color-profile', 'color-rendering', 'cursor', 'direction', 'fill', 'fill-opacity', 'fill-rule', 'font', 'font-family', 'font-size', 'font-size-adjust', 'font-stretch', 'font-style', 'font-variant', 'font-weight', 'glyph-orientation-horizontal', 'glyph-orientation-vertical', 'image-rendering', 'kerning', 'letter-spacing', 'marker', 'marker-end', 'marker-mid', 'marker-start', 'pointer-events', 'shape-rendering', 'stroke', 'stroke-dasharray', 'stroke-dashoffset', 'stroke-linecap', 'stroke-linejoin', 'stroke-miterlimit', 'stroke-opacity', 'stroke-width', 'text-anchor', 'text-rendering', 'transform', 'visibility', 'white-space', 'word-spacing', 'writing-mode'];

/* Some simple utilities */

var isFunction = function isFunction(a) {
  return typeof a === 'function';
};
var isDefined = function isDefined(a) {
  return typeof a !== 'undefined';
};
var isUndefined = function isUndefined(a) {
  return typeof a === 'undefined';
};
var isObject = function isObject(a) {
  return a !== null && (typeof a === 'undefined' ? 'undefined' : _typeof(a)) === 'object';
};

// from https://github.com/npm-dom/is-dom/blob/master/index.js
function isNode(val) {
  if (!isObject(val)) {
    return false;
  }
  if (isDefined(window) && isObject(window.Node)) {
    return val instanceof window.Node;
  }
  return typeof val.nodeType === 'number' && typeof val.nodeName === 'string';
}

/* Some utilities for cloning SVGs with inline styles */
// Removes attributes that are not valid for SVGs
function cleanAttrs(el, attrs, styles) {
  // attrs === false - remove all, attrs === true - allow all
  if (attrs === true) {
    return;
  }

  Array.prototype.slice.call(el.attributes).forEach(function (attr) {
    // remove if it is not style nor on attrs  whitelist
    // keeping attributes that are also styles because attributes override
    if (attr.specified) {
      if (attrs === '' || attrs === false || isUndefined(styles[attr.name]) && attrs.indexOf(attr.name) < 0) {
        el.removeAttribute(attr.name);
      }
    }
  });
}

function cleanStyle(tgt, parentStyles) {
  parentStyles = parentStyles || tgt.parentNode.style;
  inheritableAttrs.forEach(function (key) {
    if (tgt.style[key] === parentStyles[key]) {
      tgt.style.removeProperty(key);
    }
  });
}

function domWalk(src, tgt, down, up) {
  down(src, tgt);
  var children = src.childNodes;
  for (var i = 0; i < children.length; i++) {
    domWalk(children[i], tgt.childNodes[i], down, up);
  }
  up(src, tgt);
}

// Clones an SVGElement, copies approprate atttributes and styles.
function cloneSvg(src, attrs, styles) {
  var clonedSvg = src.cloneNode(true);

  domWalk(src, clonedSvg, function (src, tgt) {
    if (tgt.style) {
      (0, _computedStyles2['default'])(src, tgt.style, styles);
    }
  }, function (src, tgt) {
    if (tgt.style && tgt.parentNode) {
      cleanStyle(tgt);
    }
    if (tgt.attributes) {
      cleanAttrs(tgt, attrs, styles);
    }
  });

  return clonedSvg;
}

/* global Image, MouseEvent */

/* Some simple utilities for saving SVGs, including an alternative to saveAs */

// detection
var DownloadAttributeSupport = typeof document !== 'undefined' && 'download' in document.createElement('a') && typeof MouseEvent === 'function';

function saveUri(uri, name) {
  if (DownloadAttributeSupport) {
    var dl = document.createElement('a');
    dl.setAttribute('href', uri);
    dl.setAttribute('download', name);
    // firefox doesn't support `.click()`...
    // from https://github.com/sindresorhus/multi-download/blob/gh-pages/index.js
    dl.dispatchEvent(new MouseEvent('click'));
    return true;
  } else if (typeof window !== 'undefined') {
    window.open(uri, '_blank', '');
    return true;
  }

  return false;
}

function createCanvas(uri, name, cb) {
  var canvas = document.createElement('canvas');
  var context = canvas.getContext('2d');

  var image = new Image();
  image.onload = function () {
    canvas.width = image.width;
    canvas.height = image.height;
    context.drawImage(image, 0, 0);

    cb(canvas);
  };
  image.src = uri;
  return true;
}

function savePng(uri, name) {
  return createCanvas(uri, name, function (canvas) {
    if (isDefined(canvas.toBlob)) {
      canvas.toBlob(function (blob) {
        _fileSaver2['default'].saveAs(blob, name);
      });
    } else {
      saveUri(canvas.toDataURL('image/png'), name);
    }
  });
}

/* global Blob */

var isIE11 = !!window.MSInputMethodContext && !!document.documentMode;

// inheritable styles may be overridden by parent, always copy for now
inheritableAttrs.forEach(function (k) {
  if (k in svgStyles) {
    svgStyles[k] = true;
  }
});

var SvgSaver = function () {
  _createClass(SvgSaver, null, [{
    key: 'getSvg',
    value: function getSvg(el) {
      if (isUndefined(el) || el === '') {
        el = document.body.querySelector('svg');
      } else if (typeof el === 'string') {
        el = document.body.querySelector(el);
      }
      if (el && el.tagName !== 'svg') {
        el = el.querySelector('svg');
      }
      if (!isNode(el)) {
        throw new Error('svgsaver: Can\'t find an svg element');
      }
      return el;
    }
  }, {
    key: 'getFilename',
    value: function getFilename(el, filename, ext) {
      if (!filename || filename === '') {
        filename = (el.getAttribute('title') || 'untitled') + '.' + ext;
      }
      return encodeURI(filename);
    }

    /**
    * SvgSaver constructor.
    * @constructs SvgSaver
    * @api public
    *
    * @example
    * var svgsaver = new SvgSaver();                      // creates a new instance
    * var svg = document.querySelector('#mysvg');         // find the SVG element
    * svgsaver.asSvg(svg);                                // save as SVG
    */
  }]);

  function SvgSaver() {
    var _ref = arguments.length <= 0 || arguments[0] === undefined ? {} : arguments[0];

    var attrs = _ref.attrs;
    var styles = _ref.styles;

    _classCallCheck(this, SvgSaver);

    this.attrs = attrs === undefined ? svgAttrs : attrs;
    this.styles = styles === undefined ? svgStyles : styles;
  }

  /**
  * Return the cloned SVG after cleaning
  *
  * @param {SVGElement} el The element to copy.
  * @returns {SVGElement} SVG text after cleaning
  * @api public
  */

  _createClass(SvgSaver, [{
    key: 'cloneSVG',
    value: function cloneSVG(el) {
      el = SvgSaver.getSvg(el);
      var svg = cloneSvg(el, this.attrs, this.styles);

      svg.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
      svg.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
      svg.setAttribute('version', 1.1);

      // height and width needed to download in FireFox
      svg.setAttribute('width', svg.getAttribute('width') || '500');
      svg.setAttribute('height', svg.getAttribute('height') || '900');

      return svg;
    }

    /**
    * Return the SVG HTML text after cleaning
    *
    * @param {SVGElement} el The element to copy.
    * @returns {String} SVG text after cleaning
    * @api public
    */
  }, {
    key: 'getHTML',
    value: function getHTML(el) {
      var svg = this.cloneSVG(el);

      var html = svg.outerHTML;
      if (html) {
        return html;
      }

      // see http://stackoverflow.com/questions/19610089/unwanted-namespaces-on-svg-markup-when-using-xmlserializer-in-javascript-with-ie
      svg.removeAttribute('xmlns');
      svg.removeAttribute('xmlns:xlink');

      svg.setAttributeNS('http://www.w3.org/2000/xmlns/', 'xmlns', 'http://www.w3.org/2000/svg');
      svg.setAttributeNS('http://www.w3.org/2000/xmlns/', 'xmlns:xlink', 'http://www.w3.org/1999/xlink');

      return new window.XMLSerializer().serializeToString(svg);
    }

    /**
    * Return the SVG, after cleaning, as a text/xml Blob
    *
    * @param {SVGElement} el The element to copy.
    * @returns {Blog} SVG as a text/xml Blob
    * @api public
    */
  }, {
    key: 'getBlob',
    value: function getBlob(el) {
      var html = this.getHTML(el);
      return new Blob([html], { type: 'text/xml' });
    }

    /**
    * Return the SVG, after cleaning, as a image/svg+xml;base64 URI encoded string
    *
    * @param {SVGElement} el The element to copy.
    * @returns {String} SVG as image/svg+xml;base64 URI encoded string
    * @api public
    */
  }, {
    key: 'getUri',
    value: function getUri(el) {
      var html = encodeURIComponent(this.getHTML(el));
      if (isDefined(window.btoa)) {
        // see http://stackoverflow.com/questions/23223718/failed-to-execute-btoa-on-window-the-string-to-be-encoded-contains-characte
        return 'data:image/svg+xml;base64,' + window.btoa(unescape(html));
      }
      return 'data:image/svg+xml,' + html;
    }

    /**
    * Saves the SVG as a SVG file using method compatible with the browser
    *
    * @param {SVGElement} el The element to copy.
    * @param {string} [filename] The filename to save, defaults to the SVG title or 'untitled.svg'
    * @returns {SvgSaver} The SvgSaver instance
    * @api public
    */
  }, {
    key: 'asSvg',
    value: function asSvg(el, filename) {
      el = SvgSaver.getSvg(el);
      filename = SvgSaver.getFilename(el, filename, 'svg');
      if (isFunction(Blob)) {
        return _fileSaver2['default'].saveAs(this.getBlob(el), filename);
      }
      return saveUri(this.getUri(el), filename);
    }

    /**
    * Gets the SVG as a PNG data URI.
    *
    * @param {SVGElement} el The element to copy.
    * @param {Function} cb Call back called with the PNG data uri.
    * @api public
    */
  }, {
    key: 'getPngUri',
    value: function getPngUri(el, cb) {
      if (isIE11) {
        console.error('svgsaver: getPngUri not supported on IE11');
      }
      el = SvgSaver.getSvg(el);
      var filename = SvgSaver.getFilename(el, null, 'png');
      return createCanvas(this.getUri(el), filename, function (canvas) {
        cb(canvas.toDataURL('image/png'));
      });
    }

    /**
    * Saves the SVG as a PNG file using method compatible with the browser
    *
    * @param {SVGElement} el The element to copy.
    * @param {string} [filename] The filename to save, defaults to the SVG title or 'untitled.png'
    * @returns {SvgSaver} The SvgSaver instance
    * @api public
    */
  }, {
    key: 'asPng',
    value: function asPng(el, filename) {
      if (isIE11) {
        console.error('svgsaver: asPng not supported on IE11');
      }
      el = SvgSaver.getSvg(el);
      filename = SvgSaver.getFilename(el, filename, 'png');
      return savePng(this.getUri(el), filename);
    }
  }]);

  return SvgSaver;
}();

exports['default'] = SvgSaver;
module.exports = exports['default'];
});

require.alias("buffer/index.js", "buffer");
require.alias("events/events.js", "events");
require.alias("stream-http/index.js", "http");
require.alias("https-browserify/index.js", "https");
require.alias("process/browser.js", "process");
require.alias("punycode/punycode.js", "punycode");
require.alias("querystring-es3/index.js", "querystring");
require.alias("stream-browserify/index.js", "stream");
require.alias("url/url.js", "url");
require.alias("vue/dist/vue.common.js", "vue");process = require('process');require.register("___globals___", function(exports, require, module) {
  
});})();require('___globals___');


//# sourceMappingURL=app.js.map