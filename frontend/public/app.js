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
var global = typeof window === 'undefined' ? this : window;
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
require.register("Augur.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = Augur;
var queryString = require('query-string');

// import AugurApp from './components/AugurApp.vue'
// import router from './router/router'
// import AugurCards from './components/AugurCards.vue'


function Augur() {
  window.jQuery = require('jquery');
  window.Vue = require('vue');
  window.Vuex = require('vuex');
  window.VueVega = require('vue-vega').default;
  var AugurAPI = require('AugurAPI').default;
  window.AugurAPI = new AugurAPI();
  window.AugurRepos = {};
  window.AugurStats = require('AugurStats').default;
  window.$ = window.jQuery;
  window._ = require('lodash');
  window.d3 = require('d3');
  window.SvgSaver = require('svgsaver');
  window.VueRouter = require('vue-router');
  var router = require('./router/router').default;

  window.AUGUR_CHART_STYLE = {
    brightColors: ['#FF3647', '#007BFF', '#DAFF4D', '#B775FF'],
    dullColors: ['#CCCCCC', '#CCE7F2', '#D4F0B0', '#D8C3E3']
  };

  var AugurApp = require('./components/AugurApp');

  window.Vue.use(window.Vuex);
  window.Vue.use(window.VueVega);
  window.Vue.use(window.VueRouter);
  window.Vue.config.productionTip = false;

  window.augur = new window.Vuex.Store({
    state: {
      hasState: null,
      tab: 'gmd',
      baseRepo: null,
      gitRepo: null,
      comparedRepos: [],
      trailingAverage: 180,
      startDate: new Date('1 February 2011'),
      endDate: new Date(),
      compare: 'rolling',
      showBelowAverage: false,
      rawWeekly: false,
      showArea: true,
      showDetail: true,
      showTooltip: true,
      byDate: false
    },
    mutations: {
      setGitRepo: function setGitRepo(state, payload) {
        state.gitRepo = payload.gitURL;
        state.baseRepo = payload.gitURL;
        state.hasState = true;
        var repo = window.AugurAPI.Repo(payload);
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo;
        } else {
          repo = window.AugurRepos[repo.toString()];
        }
      },
      setRepo: function setRepo(state, payload) {
        var repo = window.AugurAPI.Repo(payload);
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo;
        } else {
          repo = window.AugurRepos[repo.toString()];
        }
        state.queryObject = {};
        state.hasState = true;
        if (repo.owner && repo.name && !state.gitRepo) {
          state.baseRepo = repo.toString();
          var title = repo.owner + '/' + repo.name + '- Augur';
          // state.tab = 'gmd'
          // state.queryObject['repo'] = repo.owner + '+' + repo.name
        }
        if (payload.gitURL) {
          // state.queryObject['git'] = window.btoa(repo.gitURL)
          // state.tab = 'git'
          state.gitRepo = repo.gitURL;
          state.tab = state.tab ? state.tab : 'git';
        }
      },

      // removeComparedRepo (state, payload) {
      //   state.comparedRepos
      // },
      addComparedRepo: function addComparedRepo(state, payload) {
        state.compare = 'zscore';
        state.hasState = true;
        var repo = window.AugurAPI.Repo(payload);
        if (!state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString()) {
          if (!window.AugurRepos[repo.toString()]) {
            window.AugurRepos[repo.toString()] = repo;
          } else {
            repo = window.AugurRepos[repo.toString()];
          }
          state.hasState = true;
          if (repo.owner && repo.name) {
            state.comparedRepos.push(repo.toString());
            var title = repo.owner + '/' + repo.name + '- Augur';
          }
          if (payload.gitURL) {
            state.gitRepo = repo.gitURL;
          }
          if (state.comparedRepos.length == 1) {
            if (!router.currentRoute.params.comparedrepo) {

              var owner = state.gitRepo ? null : state.baseRepo.substring(0, state.baseRepo.indexOf('/'));
              var _repo = state.gitRepo ? state.gitRepo : state.baseRepo.slice(state.baseRepo.indexOf('/') + 1);
              var name = state.tab + "compare";
              router.push({
                name: name,
                params: { owner: owner, repo: _repo, comparedowner: payload.owner, comparedrepo: payload.name }
              });
            }
          } else {
            var groupid = state.gitRepo ? String(state.gitRepo) + '+' : String(state.baseRepo) + "+";
            state.comparedRepos.forEach(function (repo) {
              groupid += String(repo) + '+';
            });
            var _name = state.tab + "group";
            router.push({
              name: _name,
              params: {
                groupid: groupid
              }
            });
          }
        }
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
      setTab: function setTab(state, payload) {
        state.tab = payload.tab;
        state.hasState = true;
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
        if (typeof payload.showArea !== 'undefined') {
          state.showArea = payload.showArea;
        }
        if (typeof payload.showTooltip !== 'undefined') {
          state.showTooltip = payload.showTooltip;
        }
        if (typeof payload.showDetail !== 'undefined') {
          state.showDetail = payload.showDetail;
        }
      },
      resetComparedRepos: function resetComparedRepos(state) {
        state.comparedRepos = [];
        router.push({
          name: state.tab,
          params: { owner: state.baseRepo.substring(0, state.baseRepo.indexOf('/')), repo: state.baseRepo.slice(state.baseRepo.indexOf('/') + 1) } });
      },
      resetBaseRepo: function resetBaseRepo(state) {
        state.baseRepo = null;
      },
      resetTab: function resetTab(state) {
        state.tab = null;
      },
      reset: function reset(state) {
        state = {
          baseRepo: null,
          comparedRepo: null,
          trailingAverage: 180,
          startDate: new Date('1 January 2005'),
          endDate: new Date(),
          compare: 'each',
          byDate: false
        };
        window.history.pushState(null, 'Augur', '/');
      } // end reset

    } // end mutations
  });

  AugurApp.store = window.augur;

  router.beforeEach(function (to, from, next) {
    if (to.params.repo || to.params.groupid) {
      if (!to.params.groupid && !to.params.comparedrepo) {
        AugurApp.store.commit("resetTab");
        AugurApp.store.commit('setTab', {
          tab: to.name
        });
        if (to.params.repo.includes('github') || to.params.repo.split(".").length > 2) {
          AugurApp.store.commit('setRepo', {
            gitURL: to.params.repo
          });
        } else {
          AugurApp.store.commit('setRepo', {
            githubURL: to.params.owner + '/' + to.params.repo
          });
        }
      } else if (to.params.comparedrepo && augur.state.comparedRepos.length == 0) {
        var tab = to.name;
        tab = tab.substring(0, tab.length - 7);
        AugurApp.store.commit("resetTab");
        AugurApp.store.commit('setTab', {
          tab: tab
        });
        AugurApp.store.commit('setRepo', {
          githubURL: to.params.owner + '/' + to.params.repo
        });
        AugurApp.store.commit('addComparedRepo', {
          githubURL: to.params.comparedowner + '/' + to.params.comparedrepo
        });
      } else if (to.params.groupid && augur.state.comparedRepos.length == 0) {
        AugurApp.store.commit("resetTab");
        var _tab = to.name;
        _tab = _tab.substring(0, _tab.length - 5);
        AugurApp.store.commit('setTab', {
          tab: _tab
        });
        var repos = to.params.groupid.split('+');
        if (repos[0].includes('github')) {
          AugurApp.store.commit('setRepo', {
            gitURL: repos[0]
          });
        } else {
          AugurApp.store.commit('setRepo', {
            githubURL: repos[0]
          });
        }
        repos.shift();
        // repos.pop()
        repos.forEach(function (cmprepo) {
          AugurApp.store.commit('addComparedRepo', {
            githubURL: cmprepo
          });
        });
      }
    }

    next();
  });

  window.AugurApp = new window.Vue({
    // components: { AugurApp },
    // store: window.augur,
    router: router,
    render: function render(h) {
      return h(AugurApp);
    }

  }).$mount('#app');

  // Load state from query string

  // let parsed = queryString.parse(window.location.search, { arrayFormat: 'bracket' })
  // let payload = { fromURL: true }
  // let hasState = 0
  // if (parsed.repo) {
  //   payload.githubURL = parsed.repo.replace(' ', '/')
  //   hasState = 1
  // }
  // if (parsed.git) {
  //   payload.gitURL = window.atob(parsed.git)
  //   hasState = 1
  // }
  // if (hasState) {
  //   window.AugurApp.$store.commit('setRepo', payload)
  // }
  // if (parsed.comparedTo) {
  //   parsed.comparedTo.forEach((repo) => {
  //     window.AugurApp.$store.commit('addComparedRepo', { githubURL: repo.replace(' ', '/') })
  //   })
  // }
}
});

;require.register("AugurAPI.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var $ = require('jquery');
var _ = require('lodash');

var AugurAPI = function () {
  function AugurAPI(hostURL, version, autobatch) {
    _classCallCheck(this, AugurAPI);

    this.__downloadedGitRepos = [];

    this._version = version || '/api/unstable';
    this._host = hostURL || 'http://' + window.location.host;
    this.__cache = {};
    this.__timeout = null;
    this.__pending = {};

    this.getDownloadedGitRepos = this.__EndpointFactory('git/repos');
    this.openRequests = 0;
    this.getMetricsStatus = this.__EndpointFactory('metrics/status/filter');
    this.getMetricsStatusMetadata = this.__EndpointFactory('metrics/status/metadata');
  }

  // __autobatcher (url, params, fireTimeout) {
  //   if (this.__timeout !== null && !fireTimeout) {
  //     this.__timeout = setTimeout(() => {
  //       __autobatch(undefined, undefined, true)
  //     })
  //   }
  //   return new Promise((resolve, reject) => {
  //     if (fireTimeout) {
  //       let batchURL = this._host + this._version + '/batch'
  //       let requestArray = []
  //       Object.keys(this.__pending).forEach((key) => {
  //         requestArray.push({})
  //       })
  //       $.post(batchURL)
  //     }
  //   })
  // }

  _createClass(AugurAPI, [{
    key: '__endpointURL',
    value: function __endpointURL(endpoint) {
      return '' + this._host + this._version + '/' + endpoint;
    }
  }, {
    key: '__URLFunctionFactory',
    value: function __URLFunctionFactory(url) {
      var self = this;
      return function (params, callback) {
        var _this = this;

        var cacheKey = window.btoa(url + JSON.stringify(params));
        this.openRequests++;
        if (self.__cache[cacheKey]) {
          if (self.__cache[cacheKey].created_at > Date.now() - 1000 * 60) {
            return new Promise(function (resolve, reject) {
              resolve(self.__cache[cacheKey].data);
            });
          }
        }
        return $.get(url, params).then(function (data) {
          _this.openRequests--;
          self.__cache[cacheKey] = {
            created_at: Date.now(),
            data: data
          };
          return data;
        });
      };
    }
  }, {
    key: '__EndpointFactory',
    value: function __EndpointFactory(endpoint) {
      return this.__URLFunctionFactory(this.__endpointURL(endpoint));
    }
  }, {
    key: 'batch',
    value: function batch(endpoints) {
      var _this2 = this;

      var str = '[{"method": "GET", "path": "' + endpoints.join('"},{"method": "GET", "path": "') + '"}]';
      this.openRequests++;
      var url = this.__endpointURL('batch');
      // Check cached
      if (this.__cache[window.btoa(url + endpoints.join(','))]) {
        if (this.__cache[window.btoa(url + endpoints.join(','))].created_at > Date.now() - 1000 * 60) {
          return new Promise(function (resolve, reject) {
            resolve(_this2.__cache[window.btoa(url + endpoints.join(','))].data);
          });
        }
      }
      return $.ajax(url, {
        type: 'post',
        data: str,
        dataType: 'json',
        contentType: 'application/json'
      }).then(function (data) {
        _this2.openRequests--;
        // Save to cache
        _this2.__cache[window.btoa(url + endpoints.join(','))] = {
          created_at: Date.now(),
          data: data
        };
        return data;
      });
    }
  }, {
    key: 'batchMapped',
    value: function batchMapped(repos, fields) {
      var endpoints = [];
      var reverseMap = {};
      var processedData = {};
      repos.forEach(function (repo) {
        Array.prototype.push.apply(endpoints, repo.batch(fields, true));
        _.assign(reverseMap, repo.__reverseEndpointMap);
        processedData[repo.toString()] = {};
      });
      return this.batch(endpoints).then(function (data) {

        return new Promise(function (resolve, reject) {
          if (Array.isArray(data)) {
            data.forEach(function (response) {
              if (response.status === 200) {
                processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = JSON.parse(response.response);
              } else {
                processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = null;
              }
            });
            resolve(processedData);
          } else {
            reject(new Error('data-not-array'));
          }
        });
      });
    }
  }, {
    key: 'Repo',
    value: function Repo(repo) {
      var _this3 = this;

      if (repo.githubURL) {
        var splitURL = repo.githubURL.split('/');
        if (splitURL.length < 3) {
          repo.owner = splitURL[0];
          repo.name = splitURL[1];
        } else {
          repo.owner = splitURL[3];
          repo.name = splitURL[4];
        }
      }

      if (repo.gitURL) {
        if (repo.gitURL.includes('github.com')) {
          var _splitURL = repo.gitURL.split('/');
          repo.owner = _splitURL[1];
          repo.name = _splitURL[2].split('.')[0];
        } else {
          var _splitURL2 = repo.gitURL.split('/');
          repo.owner = _splitURL2[0];
          repo.name = _splitURL2[1];
        }
      }

      repo.toString = function () {
        if (repo.owner && repo.name) {
          return repo.owner + '/' + repo.name;
        } else {
          return JSON.stringify(repo);
        }
      };
      repo.__endpointMap = {};
      repo.__reverseEndpointMap = {};

      repo.getDownloadedStatus = function () {
        _this3.getDownloadedGitRepos().then(function (data) {
          var rs = false;
          data.forEach(function (gitURL) {
            if (gitURL.includes('github.com')) {
              var _splitURL3 = gitURL.split('/');
              var owner = _splitURL3[3];
              var name = _splitURL3[4].split('.')[0];
              if (repo.toString() === owner + '/' + name) {
                rs = true;
              }
            }
          });
          return rs;
        });
      };

      var __Endpoint = function __Endpoint(r, name, url) {
        r[name] = _this3.__URLFunctionFactory(url);
        return r[name];
      };

      var Endpoint = function Endpoint(r, name, endpoint) {
        var fullEndpoint = _this3._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint;
        var url = _this3._host + fullEndpoint;
        r.__endpointMap[name] = fullEndpoint;
        r.__reverseEndpointMap[fullEndpoint] = { name: name, owner: repo.toString() };
        return __Endpoint(r, name, url);
      };

      var Timeseries = function Timeseries(r, jsName, endpoint) {
        var func = Endpoint(r, jsName, 'timeseries/' + endpoint);
        func.relativeTo = function (baselineRepo, params, callback) {
          var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name;
          return Endpoint(url)();
        };
        return func;
      };

      var GitEndpoint = function GitEndpoint(r, jsName, endpoint) {
        var url = _this3.__endpointURL('git/' + endpoint + '/?repo_url_base=' + window.btoa(r.gitURL));
        return __Endpoint(r, jsName, url);
      };

      repo.batch = function (jsNameArray, noExecute) {
        var routes = jsNameArray.map(function (e) {
          return repo.__endpointMap[e];
        });
        if (noExecute) {
          return routes;
        }
        return _this3.batch(routes).then(function (data) {
          return new Promise(function (resolve, reject) {
            if (Array.isArray(data)) {
              var mapped = {};
              data.forEach(function (response) {
                if (response.status === 200) {
                  mapped[repo.__reverseEndpointMap[response.path].name] = JSON.parse(response.response);
                } else {
                  mapped[repo.__reverseEndpointMap[response.path].name] = null;
                }
              });
              resolve(mapped);
            } else {
              reject(new Error('data-not-array'));
            }
          });
        });
      };

      if (repo.owner && repo.name) {
        // DIVERSITY AND INCLUSION

        // GROWTH, MATURITY, AND DECLINE
        Timeseries(repo, 'closedIssues', 'issues/closed');
        Timeseries(repo, 'closedIssueResolutionDuration', 'issues/time_to_close');
        Timeseries(repo, 'codeCommits', 'commits');
        // Timeseries(repo, 'codeReviews', 'code_reviews')
        Timeseries(repo, 'codeReviewIteration', 'code_review_iteration');
        Timeseries(repo, 'contributionAcceptance', 'contribution_acceptance');
        Endpoint(repo, 'contributingGithubOrganizations', 'contributing_github_organizations');
        Timeseries(repo, 'firstResponseToIssueDuration', 'issues/response_time');
        Timeseries(repo, 'forks', 'forks');
        Timeseries(repo, 'linesOfCodeChanged', 'lines_changed');
        Timeseries(repo, 'maintainerResponseToMergeRequestDuration', 'pulls/maintainer_response_time');
        Timeseries(repo, 'newContributingGithubOrganizations', 'new_contributing_github_organizations');
        Timeseries(repo, 'openIssues', 'issues');
        Timeseries(repo, 'pullRequestComments', 'pulls/comments');
        Timeseries(repo, 'pullRequestsOpen', 'pulls');

        // RISK

        // VALUE

        // ACTIVITY
        Timeseries(repo, 'issueComments', 'issue_comments');
        Timeseries(repo, 'pullRequestsMadeClosed', 'pulls/made_closed');
        Timeseries(repo, 'watchers', 'watchers');

        // EXPERIMENTAL

        // Commit Related
        Timeseries(repo, 'commits100', 'commits100');
        Timeseries(repo, 'commitComments', 'commits/comments');
        Endpoint(repo, 'committerLocations', 'committer_locations');
        Timeseries(repo, 'totalCommitters', 'total_committers');

        // Issue Related
        Timeseries(repo, 'issueActivity', 'issues/activity');

        // Community / Contributions
        Endpoint(repo, 'communityAge', 'community_age');
        Timeseries(repo, 'communityEngagement', 'community_engagement');
        Endpoint(repo, 'contributors', 'contributors');
        Endpoint(repo, 'contributions', 'contributions');
        Endpoint(repo, 'projectAge', 'project_age');

        // Dependency Related
        Endpoint(repo, 'dependencies', 'dependencies');
        Endpoint(repo, 'dependencyStats', 'dependency_stats');
        Endpoint(repo, 'dependents', 'dependents');

        // Other
        Endpoint(repo, 'busFactor', 'bus_factor');
        Timeseries(repo, 'downloads', 'downloads');
        Timeseries(repo, 'fakes', 'fakes');
        Endpoint(repo, 'linkingWebsites', 'linking_websites');
        Timeseries(repo, 'majorTags', 'tags/major');
        Timeseries(repo, 'newWatchers', 'new_watchers');
        Timeseries(repo, 'tags', 'tags');
      }

      if (repo.gitURL) {
        // Other
        GitEndpoint(repo, 'changesByAuthor', 'changes_by_author'), GitEndpoint(repo, 'cdRepTpIntervalLocCommits', 'cd_rep_tp_interval_loc_commits'), GitEndpoint(repo, 'cdRgTpRankedLoc', 'cd_rg_tp_ranked_loc'), GitEndpoint(repo, 'cdRgTpRankedCommits', 'cd_rg_tp_ranked_commits'), GitEndpoint(repo, 'cdRgNewrepRankedLoc', 'cd_rg_newrep_ranked_loc'), GitEndpoint(repo, 'cdRgNewrepRankedCommits', 'cd_rg_newrep_ranked_commits');
      }

      return repo;
    }
  }]);

  return AugurAPI;
}();

exports.default = AugurAPI;
});

;require.register("AugurStats.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var AugurStats = function () {
  function AugurStats() {
    _classCallCheck(this, AugurStats);
  }

  _createClass(AugurStats, null, [{
    key: 'convertDates',
    value: function convertDates(data, earliest, latest, key) {
      key = key || 'date';
      earliest = earliest || new Date('01-01-2005');
      latest = latest || new Date();
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return AugurStats.convertDates(datum);
        });
      } else {
        data = data.map(function (d) {
          d.date = new Date(d[key]);
          return d;
        }).filter(function (d) {
          return earliest < d.date && d.date < latest;
        }).sort(function (a, b) {
          return a.date - b.date;
        });
      }
      return data;
    }
  }, {
    key: 'convertKey',
    value: function convertKey(data, key, newName) {
      newName = newName || "value";
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return AugurStats.convertKey(datum, key);
        });
      } else if (key.length > 1) {
        return data.map(function (d) {
          var obj = {
            date: d.date,
            field: d[key[1]]
          };
          obj[newName] = d[key];
          return obj;
        });
      } else {
        return data.map(function (d) {
          var obj = {
            date: d.date
          };
          obj[newName] = d[key] || 0;
          return obj;
        });
      }
      return data;
    }
  }, {
    key: 'convertComparedKey',
    value: function convertComparedKey(data, key) {
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return AugurStats.convertKey(datum, key);
        });
      } else {
        return data.map(function (d) {
          return {
            date: d.date,
            comparedValue: d[key]
          };
        });
      }
      return data;
    }
  }, {
    key: 'averageArray',
    value: function averageArray(ary) {
      var len = ary.length;
      var sum = ary.reduce(function (a, e) {
        if (isFinite(e)) {
          return a + e;
        } else {
          len--;
          return a;
        }
      }, 0);
      return sum / len || 0;
    }
  }, {
    key: 'aboveAverage',
    value: function aboveAverage(data, key) {
      var flat = data.map(function (e) {
        return e[key];
      });
      var mean = AugurStats.averageArray(flat);
      return data.filter(function (e) {
        return e[key] > mean;
      });
    }
  }, {
    key: 'standardDeviationLines',
    value: function standardDeviationLines(data, key, extension, mean) {
      var flat = data.map(function (e) {
        return e[key];
      });
      mean = mean || AugurStats.averageArray(flat);
      var distances = flat.map(function (e) {
        return (e - mean) * (e - mean);
      });
      return data.map(function (e) {
        var newObj = {};
        if (e.date) {
          newObj.date = new Date(e.date);
          newObj[key + extension] = e[key];
        }
        newObj['upper' + extension] = e[key] + Math.sqrt(AugurStats.averageArray(distances));
        newObj['lower' + extension] = e[key] - Math.sqrt(AugurStats.averageArray(distances));
        return newObj;
      });
    }
  }, {
    key: 'standardDeviation',
    value: function standardDeviation(data, key, mean) {
      var flat = data.map(function (e) {
        return e[key] ? e[key] : 0;
      });

      mean = mean || AugurStats.averageArray(flat);
      var distances = flat.map(function (e) {
        return (e - mean) * (e - mean);
      });
      return Math.sqrt(AugurStats.averageArray(distances));
    }
  }, {
    key: 'describe',
    value: function describe(ary, key) {
      var flat = AugurStats.flatten(ary, key);
      var mean = AugurStats.averageArray(flat);
      var stddev = AugurStats.standardDeviation(ary, key, mean);
      var variance = stddev * stddev;
      return {
        'mean': mean,
        'stddev': stddev,
        'variance': variance
      };
    }
  }, {
    key: 'flatten',
    value: function flatten(array, key) {
      return array.map(function (e) {
        return e[key];
      });
    }
  }, {
    key: 'rollingAverage',
    value: function rollingAverage(data, key, windowSizeInDays) {
      //key = key || 'value'
      var period = windowSizeInDays / 2;
      data = data.filter(function (datum) {
        return isFinite(datum[key]);
      });
      // if (data[0].date != startDate) {
      //   let test = startDate
      //   while (data[0].date - test > period) {
      //     test += period
      //   }
      //   var offset = data[0].date - test
      // }
      // let before = offset ? offset : period
      // let after = offset ? period - offset : period
      return AugurStats.dateAggregate(data, period, period, period / 2, function (filteredData, date) {
        var flat = AugurStats.flatten(filteredData, key);
        var datum = { date: date };
        datum[key + "Rolling"] = Math.round(AugurStats.averageArray(flat) * 100) / 100;
        return datum;
      });
    }
  }, {
    key: 'dateAggregate',
    value: function dateAggregate(data, daysBefore, daysAfter, interval, func) {
      daysBefore = daysBefore || 30;
      interval = interval || (daysAfter + daysBefore) / 4;
      var rolling = [];
      var averageWindow = [];
      var i = 0;

      var earliest = new Date();
      var latest = new Date();

      for (var date = new Date(data[0].date); date <= data[data.length - 1].date; date.setDate(date.getDate() + interval)) {
        earliest = new Date(date).setDate(date.getDate() - daysBefore);
        latest = new Date(date).setDate(date.getDate() + daysAfter);
        averageWindow = data.filter(function (d) {
          return earliest <= d.date && d.date <= latest;
        });
        rolling.push(func(averageWindow, new Date(date), i));
        i++;
      }
      return rolling;
    }
  }, {
    key: 'alignDates',
    value: function alignDates(data, baseDate, windowSizeInDays) {
      //key = key || 'value'
      var period = windowSizeInDays / 2;
      data.unshift({ date: baseDate, value: null });
      return data;
    }
  }, {
    key: 'convertToPercentages',
    value: function convertToPercentages(data, key, baseline) {
      if (!data) {
        return [];
      }
      baseline = baseline || AugurStats.averageArray(data.map(function (e) {
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
    value: function makeRelative(baseData, compareData, key, config) {
      config.byDate = config.byDate === true;
      config.earliest = config.earliest || new Date('01-01-2005');
      config.latest = config.latest || new Date();
      config.period = config.period || 180;
      key = key || Object.keys(baseData[0])[1];

      var iter = {
        base: 0,
        compare: 0
      };
      var data = {};

      data['base'] = AugurStats.rollingAverage(AugurStats.convertDates(AugurStats.convertKey(baseData, key), config.earliest, config.latest), undefined, config.period);

      data['compare'] = AugurStats.rollingAverage(AugurStats.convertDates(AugurStats.convertKey(compareData, key), config.earliest, config.latest), undefined, config.period);

      var result = [];

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
      return result;
    }
  }, {
    key: 'zscores',
    value: function zscores(data, key) {
      // key = key || 'value'
      var stats = AugurStats.describe(data, key);
      return data.map(function (e) {
        var newObj = {};
        // if (e.date) {
        newObj.date = new Date(e.date);
        // } else {
        //   newObj.date = 
        // }
        var zscore = stats['stddev'] == 0 ? 0 : (e[key] - stats['mean']) / stats['stddev'];
        newObj[key] = zscore;
        return newObj;
      });
    }
  }, {
    key: 'combine',
    value: function combine() {
      return Array.from(arguments);
    }
  }]);

  return AugurStats;
}();

exports.default = AugurStats;
});

;require.register("components/AugurApp.vue", function(exports, require, module) {
;(function(){
'use strict';

var _AugurHeader = require('./AugurHeader.vue');

var _AugurHeader2 = _interopRequireDefault(_AugurHeader);

var _AugurCards = require('./AugurCards.vue');

var _AugurCards2 = _interopRequireDefault(_AugurCards);

var _vueRouter = require('vue-router');

var _vueRouter2 = _interopRequireDefault(_vueRouter);

var _GrowthMaturityDeclineCard = require('./GrowthMaturityDeclineCard');

var _GrowthMaturityDeclineCard2 = _interopRequireDefault(_GrowthMaturityDeclineCard);

var _ExperimentalCard = require('./ExperimentalCard');

var _ExperimentalCard2 = _interopRequireDefault(_ExperimentalCard);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  name: "app",
  components: {
    'augur-header': _AugurHeader2.default,
    'augur-cards': _AugurCards2.default

  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('div',{staticClass:"content",attrs:{"id":"app"}},[_c('router-view')],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-4cb2e45e", __vue__options__)
  } else {
    hotAPI.reload("data-v-4cb2e45e", __vue__options__)
  }
})()}
});

;require.register("components/AugurCards.vue", function(exports, require, module) {
;(function(){
"use strict";
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('div',{staticClass:"fullwidth"},[_c('router-view',{attrs:{"name":"header"}})],1),_vm._v(" "),_c('div',{ref:"cards",staticClass:"content"},[_c('router-view',{attrs:{"name":"tabs"}}),_vm._v(" "),_c('router-view',{attrs:{"name":"controls"}}),_vm._v(" "),_c('router-view',{attrs:{"name":"content"}})],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-78eb2940", __vue__options__)
  } else {
    hotAPI.reload("data-v-78eb2940", __vue__options__)
  }
})()}
});

;require.register("components/AugurHeader.vue", function(exports, require, module) {
;(function(){
"use strict";

module.exports = {
  methods: {
    onRepo: function onRepo(e) {
      var repo = window.AugurAPI.Repo({
        githubURL: e.target.value
      });
      if (!repo.batch(['codeCommits'], true)[0]) {
        alert("The repo " + repo.githubURL + " could not be found. Please try again.");
      } else {
        this.$store.commit('resetBaseRepo');
        this.$store.commit('setRepo', {
          githubURL: e.target.value
        });
        this.$router.push({
          name: 'gmd',
          params: { owner: repo.owner, repo: repo.name }
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('header',{staticClass:"hide-print"},[_c('div',{staticClass:"content"},[_c('div',{staticClass:"row auto"},[_vm._m(0),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('div',{staticClass:"form-item"},[_c('input',{staticClass:"search reposearch",attrs:{"type":"text","name":"headersearch","placeholder":"GitHub URL"},on:{"change":_vm.onRepo}})])]),_vm._v(" "),_c('nav',{staticClass:"col col-4 header-nav"},[_c('a',{staticClass:"header-nav-item",attrs:{"href":"https://github.com/chaoss/augur"}},[_vm._v("GitHub")]),_vm._v(" "),_c('a',{staticClass:"header-nav-item",attrs:{"href":"/static/docs/"}},[_vm._v("Python Docs")]),_vm._v(" "),_c('a',{staticClass:"header-nav-item",attrs:{"href":"/static/api_docs/"}},[_vm._v("API Docs")]),_vm._v(" "),_c('router-link',{staticClass:"header-nav-item",attrs:{"to":"/metrics_status"}},[_vm._v("Metrics Status")])],1)])])])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"col col-3"},[_c('a',{attrs:{"href":"/"}},[_c('img',{attrs:{"src":"/static/logo.png","id":"logo","alt":"CHAOSS: Community Health Analytics for Open Source Software"}})])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-6becaf40", __vue__options__)
  } else {
    hotAPI.reload("data-v-6becaf40", __vue__options__)
  }
})()}
});

;require.register("components/BaseRepoActivityCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    DynamicLineChart: _DynamicLineChart2.default,
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Activity")]),_vm._v(" "),_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"issueComments","title":"Issue Comments / Week ","cite-url":"https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/issue-comments.md","cite-text":"Issue Comments"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"pullRequestsMadeClosed","title":"Pull Requests Made/ Closed per Week ","cite-url":"https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/pull-requests-made-closed.md","cite-text":"Pull Requests Made/Closed"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"watchers","title":"Watchers / Week ","cite-url":"https://github.com/augurlabs/wg-gmd/tree/master/activity-metrics/watchers.md","cite-text":"Watchers"}})],1)]),_vm._v(" "),_vm._m(0)])}
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

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

var _DependencyOverview = require('./charts/DependencyOverview');

var _DependencyOverview2 = _interopRequireDefault(_DependencyOverview);

var _BusFactor = require('./charts/BusFactor');

var _BusFactor2 = _interopRequireDefault(_BusFactor);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    DynamicLineChart: _DynamicLineChart2.default,
    DependencyOverview: _DependencyOverview2.default,
    BusFactor: _BusFactor2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Ecosystem")]),_vm._v(" "),_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"downloads","title":"Downloads / Day","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"stars","title":"Stars / Week","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md","cite-text":"Community Activty"}})],1)]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('bus-factor',{attrs:{"source":"busFactor","title":"Bus Factor","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics-list.md","cite-text":"Pony Factor"}})],1),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-12"},[_c('dependency-overview')],1)])])}
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

;require.register("components/DiversityInclusionCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    DynamicLineChart: _DynamicLineChart2.default,
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"row"},[_c('p',[_vm._v("We currently do not have any metrics developed for this group.")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-3ae426c0", __vue__options__)
  } else {
    hotAPI.reload("data-v-3ae426c0", __vue__options__)
  }
})()}
});

;require.register("components/DownloadedReposCard.vue", function(exports, require, module) {
;(function(){
"use strict";

module.exports = {
  data: function data() {
    return {
      repos: {},
      projects: []
    };
  },

  methods: {
    onRepo: function onRepo(e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      });
    },
    onGitRepo: function onGitRepo(e) {
      var first = e.url.indexOf(".");
      var last = e.url.lastIndexOf(".");
      var domain = null;
      var owner = null;
      var repo = null;
      var extension = false;

      if (first == last) {
        domain = e.url.substring(0, first);
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'));
        repo = e.url.slice(e.url.lastIndexOf('/') + 1);
      } else if (e.url.slice(last) == '.git') {
        domain = e.url.substring(0, first);
        extension = true;
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'));
        repo = e.url.substring(e.url.lastIndexOf('/') + 1, e.url.length - 4);
      } else {
        domain = e.url.substring(first + 1, last);
        owner = null;
        repo = e.url.slice(e.url.lastIndexOf('/') + 1);
      }
      this.$store.commit('setRepo', {
        gitURL: e.url
      });

      this.$store.commit('setTab', {
        tab: 'git'
      });

      this.$router.push({
        name: 'git',
        params: { repo: e.url }
      });
    },
    getDownloadedRepos: function getDownloadedRepos() {
      var _this = this;

      this.downloadedRepos = [];
      window.AugurAPI.getDownloadedGitRepos().then(function (data) {
        $(_this.$el).find('.spinner').removeClass('loader');
        $(_this.$el).find('.spinner').removeClass('relative');
        _this.repos = window._.groupBy(data, 'project_name');
        _this.projects = Object.keys(_this.repos);
      });
    },
    btoa: function btoa(s) {
      return window.btoa(s);
    }
  },
  mounted: function mounted() {
    this.getDownloadedRepos();
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',{staticClass:"unmaterialized"},[_c('h3',[_vm._v("Downloaded Git Repos by Project")]),_vm._v(" "),_c('div',{staticClass:"row section"},[_c('hr'),_vm._v(" "),_c('div',{staticClass:"col col-12 relative spinner loader",staticStyle:{"margin-left":"42.4%"}}),_vm._v(" "),_vm._l((_vm.projects),function(project){return _c('div',{staticClass:"col-6"},[_c('h4',[_vm._v(_vm._s(project))]),_vm._v(" "),_c('div',{staticClass:"repo-link-holder"},[_c('table',{staticClass:"is-responsive"},[_vm._m(0,true),_vm._v(" "),_c('tbody',{staticClass:"repo-link-table repo-link-table-body"},_vm._l((_vm.repos[project]),function(repo){return _c('tr',[_c('td',[_c('a',{attrs:{"href":"#"},on:{"click":function($event){_vm.onGitRepo(repo)}}},[_vm._v(_vm._s(repo.url))])]),_vm._v(" "),_c('td',[_vm._v(_vm._s(repo.status))])])}))])])])})],2)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('thead',{staticClass:"repo-link-table repo-link-table-body"},[_c('tr',[_c('th',[_vm._v("URL")]),_vm._v(" "),_c('th',[_vm._v("Status")])])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-1825962d", __vue__options__)
  } else {
    hotAPI.reload("data-v-1825962d", __vue__options__)
  }
})()}
});

;require.register("components/ExperimentalCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

var _DualAxisContributions = require('./charts/DualAxisContributions');

var _DualAxisContributions2 = _interopRequireDefault(_DualAxisContributions);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    DynamicLineChart: _DynamicLineChart2.default,
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default,
    DualAxisContributions: _DualAxisContributions2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Experimental")]),_vm._v(" "),_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"commitComments","title":"Commit Comments / Week ","cite-url":"","cite-text":"Commit Comments"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"totalCommitters","title":"Committers","cite-url":"","cite-text":"Total Commiters","disable-rolling-average":"1"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"contributionAcceptance","title":"Contribution Acceptance Rate","cite-url":"","cite-text":"Contribution Acceptance"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"communityEngagement:issues_open","title":"Community Engagement: Open Issues","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md","cite-text":"Open Issues","disable-rolling-average":"1"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"communityEngagement:issues_closed_total","title":"Community Engagement: Closed Issues","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md","cite-text":"Closed Issues","disable-rolling-average":"1"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"fakes","title":"Fakes","cite-url":"","cite-text":"Fakes","disable-rolling-average":"1"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"newWatchers","title":"New Watchers / Week","cite-url":"","cite-text":"New Watchers"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('stacked-bar-chart',{attrs:{"source":"issueActivity","title":"Issue Activity","cite-url":"","cite-text":"Issue Activity"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('bubble-chart',{attrs:{"source":"contributors","title":"Contributor Overview","size":"total","cite-url":"","cite-text":"Contributors"}})],1)])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-b05646f6", __vue__options__)
  } else {
    hotAPI.reload("data-v-b05646f6", __vue__options__)
  }
})()}
});

;require.register("components/GitCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _AugurHeader = require('./AugurHeader');

var _AugurHeader2 = _interopRequireDefault(_AugurHeader);

var _TickChart = require('./charts/TickChart');

var _TickChart2 = _interopRequireDefault(_TickChart);

var _LinesOfCodeChart = require('./charts/LinesOfCodeChart');

var _LinesOfCodeChart2 = _interopRequireDefault(_LinesOfCodeChart);

var _NormalizedStackedBarChart = require('./charts/NormalizedStackedBarChart');

var _NormalizedStackedBarChart2 = _interopRequireDefault(_NormalizedStackedBarChart);

var _OneDimensionalStackedBarChart = require('./charts/OneDimensionalStackedBarChart');

var _OneDimensionalStackedBarChart2 = _interopRequireDefault(_OneDimensionalStackedBarChart);

var _HorizontalBarChart = require('./charts/HorizontalBarChart');

var _HorizontalBarChart2 = _interopRequireDefault(_HorizontalBarChart);

var _GroupedBarChart = require('./charts/GroupedBarChart');

var _GroupedBarChart2 = _interopRequireDefault(_GroupedBarChart);

var _DirectionalTimeChart = require('./charts/DirectionalTimeChart');

var _DirectionalTimeChart2 = _interopRequireDefault(_DirectionalTimeChart);

var _TimeIntervalBarChart = require('./charts/TimeIntervalBarChart');

var _TimeIntervalBarChart2 = _interopRequireDefault(_TimeIntervalBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    AugurHeader: _AugurHeader2.default,
    TickChart: _TickChart2.default,
    LinesOfCodeChart: _LinesOfCodeChart2.default,
    NormalizedStackedBarChart: _NormalizedStackedBarChart2.default,
    OneDimensionalStackedBarChart: _OneDimensionalStackedBarChart2.default,
    HorizontalBarChart: _HorizontalBarChart2.default,
    GroupedBarChart: _GroupedBarChart2.default,
    DirectionalTimeChart: _DirectionalTimeChart2.default,
    TimeIntervalBarChart: _TimeIntervalBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important","margin-bottom":"20px"}},[_vm._v(_vm._s(_vm.$store.state.gitRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block","margin-bottom":"20px"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block","margin-bottom":"20px"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgTpRankedCommits","title":"Top Repos in 2018 by Commits with Baseline Averages - Sorted","field":"commit"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgTpRankedLoc","title":"Top Repos in 2018 by Net LoC with Baseline Averages - Sorted","field":"loc"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12",staticStyle:{"padding-right":"35px"}},[_c('time-interval-bar-chart',{attrs:{"source":"cdRepTpIntervalLocCommits","title":"Contributions in 2018 by Monthly Intervals with Baseline Averages","field":"loc"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgNewrepRankedCommits","title":"Top New Repos in 2018 by Commits with Baseline Averages - Sorted","field":"commit"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgNewrepRankedLoc","title":"Top New Repos in 2018 by Net LoC with Baseline Averages - Sorted","field":"loc"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('tick-chart')],1)]),_vm._v(" "),_c('div',{staticClass:"row",staticStyle:{"transform":"translateY(-50px) !important"}},[_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('normalized-stacked-bar-chart',{attrs:{"title":"Lines of code added by the top 10 authors as Percentages - By Time Period"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-left":"65px"}},[_c('div',{staticStyle:{"padding-top":"35px"}}),_vm._v(" "),_c('horizontal-bar-chart',{attrs:{"type":"lines","title":"Average Lines of Code Per Commit"}})],1)]),_vm._v(" "),_c('div',{staticClass:"row",staticStyle:{"transform":"translateY(-100px) !important"}},[_c('div',{staticClass:"col col-6"},[_c('one-dimensional-stacked-bar-chart',{attrs:{"type":"lines","title":"Lines of Code Added by the top 10 Authors as Percentages - All Time"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('one-dimensional-stacked-bar-chart',{attrs:{"type":"commit","title":"Commits by the top 10 Authors as Percentages - All Time"}})],1)]),_vm._v(" "),_c('div',{staticClass:"row",staticStyle:{"transform":"translateY(-50px) !important"}},[_c('lines-of-code-chart')],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-f66913b6", __vue__options__)
  } else {
    hotAPI.reload("data-v-f66913b6", __vue__options__)
  }
})()}
});

;require.register("components/GrowthMaturityDeclineCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default,
    DynamicLineChart: _DynamicLineChart2.default
  },
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  methods: {
    getMetricsStatus: function getMetricsStatus() {
      var _this = this;

      var query_string = "group=" + this.selected_group + "&data_source=" + this.selected_source + "&metric_type=" + this.selected_metric_type + "&backend_status=" + this.selected_backend_status + "&frontend_status=" + this.selected_frontend_status + "&is_defined=" + this.selected_is_defined;

      window.AugurAPI.getMetricsStatus(query_string).then(function (data) {
        _this.metricsData = data;
      });
    },
    removeComparison: function removeComparison() {
      $(this.$el).find('.multiselect__content-wrapper').removeClass('selecting');
    }
  },
  mounted: function mounted() {
    this.selected_group = 'all';
    this.selected_source = 'all';
    this.selected_metric_type = 'all';
    this.selected_backend_status = 'all';
    this.selected_frontend_status = 'all';
    this.selected_is_defined = 'all';
    this.getMetricsStatus();
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] }),attrs:{"value":repo},on:{"click":function($event){}}},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"closedIssues","title":"Closed Issues / Week","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md","cite-text":"Issues Closed"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"codeCommits","title":"Code Commits / Week","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/commits.md","cite-text":"Commits"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"codeReviewIteration","title":"Number of Code Review Iterations","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md","cite-text":"Code Review Iterations"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"contributionAcceptance","title":"Contribution Acceptance","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md","cite-text":"Contribution Acceptance"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"forks","title":"Forks / Week","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/forks.md","cite-text":"Forks"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"maintainerResponseToMergeRequestDuration","title":"Time to First Maintainer Response to Merge Request","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md","cite-text":"Time to First Maintainer Response to Merge Request"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"newContributingGithubOrganizations","title":"New Contributing Github Organizations","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/new-contributing-organizations.md","cite-text":"New Contributing Organizations"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"openIssues","title":"Open Issues / Week","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md","cite-text":"Issues Open"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"pullRequestComments","title":"Pull Request Comments / Week ","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/pull-request-comments.md","cite-text":"Pull Request Comments"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('dynamic-line-chart',{attrs:{"source":"pullRequestsOpen","title":"Pull Requests Open / Week","cite-url":"https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/pull-requests-open.md","cite-text":"Open Pull Requests"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-12"},[_c('bubble-chart',{attrs:{"source":"contributingGithubOrganizations","title":"Contributing Github Organizations Overview","size":"total","cite-url":"https://github.com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md","cite-text":"Contributing Organizations"}})],1)]),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('small',[_vm._v("Data provided by "),_c('a',{attrs:{"href":"http://ghtorrent.org/msr14.html"}},[_vm._v("GHTorrent")]),_vm._v(" "),_c('span',{staticClass:"ghtorrent-version"}),_vm._v(" and the "),_c('a',{attrs:{"href":"https://developer.github.com/"}},[_vm._v("GitHub API")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-429b02f1", __vue__options__)
  } else {
    hotAPI.reload("data-v-429b02f1", __vue__options__)
  }
})()}
});

;require.register("components/LoginForm.vue", function(exports, require, module) {
;(function(){
"use strict";

module.exports = {
  data: function data() {
    return {};
  },

  methods: {},
  computed: {}
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _vm._m(0)}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"limiter"},[_c('div',{staticClass:"container-login background"},[_c('div',{staticClass:"wrap-login"},[_c('form',{staticClass:"login-form validate-form"},[_c('div',{staticStyle:{"text-align":"center","padding-right":"10px"}},[_c('img',{attrs:{"src":"static/logo.png","id":"logo","alt":"CHAOSS: Community Health Analytics for Open Source Software"}})]),_vm._v(" "),_c('span',{staticClass:"login-form-title"},[_vm._v("\n          Log in\n        ")]),_vm._v(" "),_c('div',{staticClass:"wrap-input validate-input",attrs:{"data-validate":"Enter username"}},[_c('input',{staticClass:"input",attrs:{"type":"text","name":"username","placeholder":"Username"}}),_vm._v(" "),_c('span',{staticClass:"focus-input",staticStyle:{"padding":"12px 0px 0px 10px"}},[_vm._v("👤")])]),_vm._v(" "),_c('div',{staticClass:"wrap-input validate-input",attrs:{"data-validate":"Enter password"}},[_c('input',{staticClass:"input",attrs:{"type":"password","placeholder":"Password"}}),_vm._v(" "),_c('span',{staticClass:"focus-input",staticStyle:{"padding":"12px 0px 0px 10px"}},[_vm._v("🔒")])]),_vm._v(" "),_c('div',{staticClass:"contact-form-checkbox"},[_c('input',{staticClass:"input-checkbox",attrs:{"id":"ckb1","type":"checkbox"}}),_vm._v(" "),_c('label',{staticClass:"label-checkbox",attrs:{"for":"ckb1"}},[_vm._v("\n            Remember me\n          ")])]),_vm._v(" "),_c('div',{staticClass:"container-login-form-btn"},[_c('button',{staticClass:"login-form-btn"},[_vm._v("\n            Login\n          ")])])])])])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-6fde6fb0", __vue__options__)
  } else {
    hotAPI.reload("data-v-6fde6fb0", __vue__options__)
  }
})()}
});

;require.register("components/MainControls.vue", function(exports, require, module) {
;(function(){
"use strict";

var _vueMultiselect = require("vue-multiselect");

var _vueMultiselect2 = _interopRequireDefault(_vueMultiselect);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    Multiselect: _vueMultiselect2.default
  },
  data: function data() {
    return {
      info: {
        days: 180,
        points: 45
      },
      isCollapsed: false,
      project: "Select project",
      values: [],
      options: [],
      repos: {},
      projects: [],
      disabled: false,
      compCount: 0,
      compared: true
    };
  },

  watch: {
    project: function project() {
      var _this = this;

      this.options = [];
      this.repos[this.project].forEach(function (repo) {
        var url = repo.url;
        var first = url.indexOf(".");
        var last = url.lastIndexOf(".");

        var option = null;

        if (first == last) option = url.slice(url.indexOf('/') + 1);else if (url.slice(last) == '.git') option = url.slice(url.indexOf('/') + 1);else option = url.substring(first + 1, last) + repo.url.slice(url.indexOf('/'));
        _this.options.push(option);
      });
    },
    compCount: function compCount() {
      if (this.$store.state.comparedRepos.length < 2) this.disabled = true;
      if (this.$store.state.comparedRepos.length == 1) this.compared = true;
    }

  },
  directives: {
    'click-outside': {
      bind: function bind(el, binding, vNode) {
        if (typeof binding.value !== 'function') {
          var compName = vNode.context.name;
          var warn = "[Vue-click-outside:] provided expression '" + binding.expression + "' is not a function, but has to be";
          if (compName) {
            warn += "Found in component '" + compName + "'";
          }
        }
        var bubble = binding.modifiers.bubble;
        var handler = function handler(e) {
          if (bubble || !el.contains(e.target) && el !== e.target) {
            binding.value(e);
          }
        };
        el.__vueClickOutside__ = handler;
        document.addEventListener('click', handler);
      },
      unbind: function unbind(el, binding) {
        document.removeEventListener('click', el.__vueClickOutside__);
        el.__vueClickOutside__ = null;
      }
    }
  },
  methods: {
    collapseText: function collapseText() {
      this.isCollapsed = !this.isCollapsed;
      if (!this.isCollapsed) {
        $(this.$el).find('.section').addClass('collapsed');
      } else $(this.$el).find('.section').removeClass('collapsed');
    },
    onStartDateChange: function onStartDateChange(e) {
      var _this2 = this;

      var date = Date.parse(this.$refs.startMonth.value + "/01/" + this.$refs.startYear.value);
      console.log('Start date has been changed!');
      if (this.startDateTimeout) {
        clearTimeout(this.startDateTimeout);
        delete this.startDateTimeout;
        console.log('startDateTimeout');
      }
      this.startDateTimeout = setTimeout(function () {
        _this2.$store.commit('setDates', {
          startDate: date
        });
      }, 100);
    },
    onEndDateChange: function onEndDateChange(e) {
      var _this3 = this;

      var date = null;

      if (e.target.value > 12) {
        date = Date.parse((parseInt(this.endMonth) + 1).toString() + "/01/" + e.target.value);
      } else {
        var month = (parseInt(e.target.value) + 1).toString();
        console.log();
        date = Date.parse(month + "/01/" + this.endYear);
      }
      if (this.endDateTimeout) {
        clearTimeout(this.endDateTimeout);
        delete this.endDateTimeout;
      }
      this.endDateTimeout = setTimeout(function () {
        _this3.$store.commit('setDates', {
          endDate: date
        });
      }, 100);
    },
    onTrailingAverageChange: function onTrailingAverageChange(e) {
      this.info.days = e.target.value;
      this.info.points = e.target.value / 4;
      this.$store.commit('setVizOptions', {
        trailingAverage: e.target.value
      });
    },
    onRawWeeklyChange: function onRawWeeklyChange(e) {
      this.$store.commit('setVizOptions', {
        rawWeekly: e.target.checked
      });
    },
    onAreaChange: function onAreaChange(e) {
      this.$store.commit('setVizOptions', {
        showArea: e.target.checked
      });
    },
    onTooltipChange: function onTooltipChange(e) {
      this.$store.commit('setVizOptions', {
        showTooltip: e.target.checked
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
    },
    onCompare: function onCompare(e) {
      var element = document.getElementById("invalid");
      this.compCount++;
      var repo = window.AugurAPI.Repo({
        githubURL: e.target.value
      });
      if (!repo.batch(['codeCommits'], true)[0]) {
        element.classList.remove("invisible");
      } else {
        this.$store.commit('addComparedRepo', {
          githubURL: e.target.value

        });
        element.classList.add("invisible");
      }
    },
    onArrayCompare: function onArrayCompare() {
      var _this4 = this;

      this.compCount += this.values.length;
      this.values.forEach(function (url) {
        var link = url;
        var end = url.slice(url.length - 4);
        if (end == ".git") link = link.substring(0, url.length - 4);
        _this4.$store.commit('addComparedRepo', {
          githubURL: link
        });
      });
    },
    onValuesClear: function onValuesClear() {
      this.values = [];
    },
    onClear: function onClear() {
      this.values = [];
      this.$store.commit('resetComparedRepos');
    },
    onDetailChange: function onDetailChange(e) {
      this.$store.commit('setVizOptions', {
        showDetail: e.target.checked
      });
    },
    getDownloadedRepos: function getDownloadedRepos() {
      var _this5 = this;

      this.downloadedRepos = [];
      window.AugurAPI.getDownloadedGitRepos().then(function (data) {
        _this5.repos = window._.groupBy(data, 'project_name');
        _this5.projects = Object.keys(_this5.repos);
      });
    },
    keepSelecting: function keepSelecting() {
      $(this.$el).find('.multiselect__content-wrapper').addClass('selecting');
    },
    stopSelecting: function stopSelecting() {
      $(this.$el).find('.multiselect__content-wrapper').removeClass('selecting');
    }
  },
  computed: {
    compare: function compare() {
      return this.$store.state.compare;
    },
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
    },
    startMonth: function startMonth() {
      return this.$store.state.startDate.getMonth();
    },
    startYear: function startYear() {
      return this.$store.state.startDate.getUTCFullYear();
    },
    endMonth: function endMonth() {
      return this.$store.state.endDate.getMonth();
    },
    endYear: function endYear() {
      return this.$store.state.endDate.getUTCFullYear();
    }
  },
  mounted: function mounted() {
    this.getDownloadedRepos();

    window.$(this.$el).find('.multiselect__input').addClass('search');
    window.$(this.$el).find('.multiselect__input').addClass('reposearch');
    console.log("CHECKING", this.$store.state.startDate.getMonth(), this.$store.state.startDate.getUTCFullYear(), this.$store.state.endDate.getMonth(), this.$store.state.endDate.getUTCFullYear());

    if (this.projects.length == 1) this.project = this.projects[0];
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"row",attrs:{"id":"controls"}},[_c('div',{staticClass:"col col-12"},[_c('div',{staticClass:"form"},[_c('div',{staticClass:"topic"},[_c('div',{staticClass:"container"},[_c('div',{staticClass:"row justify-content-md-center"},[_c('div',{staticClass:"col col-9"},[_c('div',{staticClass:"row"},[_vm._m(0),_vm._v(" "),_c('div',{directives:[{name:"click-outside",rawName:"v-click-outside",value:(_vm.stopSelecting),expression:"stopSelecting"}],staticClass:"row col col-4",staticStyle:{"text-align":"center !important"}},[_c('div',{staticClass:"col col-6",staticStyle:{"display":"inline !important"},on:{"click":_vm.keepSelecting}},[_c('multiselect',{attrs:{"options":_vm.projects,"placeholder":_vm.project},model:{value:(_vm.project),callback:function ($$v) {_vm.project=$$v},expression:"project"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"display":"inline !important"},on:{"click":_vm.keepSelecting}},[_c('multiselect',{staticClass:"search reposearch special",attrs:{"options":_vm.options,"multiple":true,"group-label":"url","placeholder":"Select repos"},model:{value:(_vm.values),callback:function ($$v) {_vm.values=$$v},expression:"values"}})],1)]),_vm._v(" "),_c('div',{staticClass:"col col-1"},[_c('input',{staticStyle:{"max-width":"69.9px"},attrs:{"type":"button","value":"Apply"},on:{"click":function($event){_vm.onArrayCompare(); _vm.onValuesClear()}}})]),_vm._v(" "),_c('div',{staticClass:"col col-1"},[_c('input',{staticStyle:{"max-width":"69.9px"},attrs:{"type":"button","value":"Reset"},on:{"click":function($event){_vm.onClear()}}})]),_vm._v(" "),_c('div',{staticClass:"col col-3"},[_c('input',{staticClass:"search reposearch",attrs:{"type":"text","placeholder":"Search other GitHub URL"},on:{"change":_vm.onCompare}}),_vm._v(" "),_c('p')])])]),_vm._v(" "),_c('div',{staticClass:"col col-3",attrs:{"id":"collapse"}},[_c('div',{directives:[{name:"show",rawName:"v-show",value:(_vm.isCollapsed),expression:"isCollapsed"}],staticClass:"col col-12 align-bottom",attrs:{"align":"right"},on:{"click":function($event){_vm.collapseText()}}},[_vm._v("Less configuration options ▼")]),_vm._v(" "),_c('div',{directives:[{name:"show",rawName:"v-show",value:(!_vm.isCollapsed),expression:"!isCollapsed"}],staticClass:"col col-12 align-bottom",attrs:{"align":"right"},on:{"click":function($event){_vm.collapseText()}}},[_vm._v("More configuration options ▶")])])])]),_vm._v(" "),_c('div',{staticClass:"row gutters section collapsible collapsed"},[_c('div',{staticClass:"col col-5"},[_c('label',[_c('h6',[_vm._v("Line Chart Options")]),_vm._v(" "),_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox"},on:{"change":_vm.onRawWeeklyChange}}),_vm._v("Raw weekly values"),_c('sup',{staticClass:"warn"})])]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox","disabled":!_vm.disabled,"checked":""},domProps:{"checked":_vm.disabled},on:{"change":_vm.onAreaChange}}),_vm._v("Standard deviation")])])]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox","disabled":!_vm.disabled,"checked":""},domProps:{"checked":_vm.disabled},on:{"change":_vm.onTooltipChange}}),_vm._v("Show tooltip")])]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox","checked":""},on:{"change":_vm.onDetailChange}}),_vm._v("Enable detail")])])]),_vm._v(" "),_c('label',[_c('h6',[_vm._v("Bubble Chart Options ")]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"each","type":"checkbox"},on:{"change":_vm.onShowBelowAverageChange}}),_vm._v("Show users with below-average total contributions"),_c('sup',{staticClass:"warn"})]),_c('br')])]),_vm._v(" "),_vm._m(1),_vm._v(" "),_c('div',{staticClass:"col col-11"},[_c('small',[_vm._v("1. Line charts show a rolling mean over "+_vm._s(_vm.info.days)+" days with data points at each "+_vm._s(_vm.info.points)+"-day interval")])])])])]),_vm._v(" "),_c('div',{staticClass:"col col-7"},[_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('h6',[_vm._v("Chart Timeline Configuration")]),_vm._v(" "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-11"},[_c('div',{staticClass:"form-item"},[_c('label',[_vm._v("Start Date\n                          "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-7"},[_c('div',{staticClass:"form-item"},[_c('select',{ref:"startMonth",on:{"change":_vm.onStartDateChange}},_vm._l((_vm.months),function(month){return _c('option',{domProps:{"value":month.value,"selected":(_vm.startMonth) == month.value}},[_vm._v(_vm._s(month.name))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Month")])])]),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('div',{staticClass:"form-item"},[_c('select',{ref:"startYear",on:{"change":_vm.onStartDateChange}},_vm._l((_vm.years),function(year){return _c('option',{domProps:{"value":year,"selected":_vm.startYear == year}},[_vm._v(_vm._s(year))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Year")])])])])])])])]),_vm._v(" "),_c('p'),_vm._v(" "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-11"},[_c('div',{staticClass:"form-item"},[_c('label',[_vm._v("End Date\n                          "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-7"},[_c('div',{staticClass:"form-item"},[_c('select',{ref:"endMonth",on:{"change":_vm.onEndDateChange}},_vm._l((_vm.months),function(month){return _c('option',{domProps:{"value":month.value,"selected":(_vm.endMonth) == month.value}},[_vm._v(_vm._s(month.name))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Month")])])]),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('div',{staticClass:"form-item"},[_c('select',{ref:"endYear",on:{"change":_vm.onEndDateChange}},_vm._l((_vm.years),function(year){return _c('option',{domProps:{"value":year,"selected":_vm.endYear == year}},[_vm._v(_vm._s(year))])})),_vm._v(" "),_c('div',{staticClass:"desc"},[_vm._v("Year")])])])])])])])]),_vm._v(" "),_c('br')]),_vm._v(" "),_c('div',{staticClass:"col col-1"}),_vm._v(" "),_c('div',{staticClass:"col col-5"},[_c('h6',[_vm._v("Rendering")]),_vm._v(" "),_c('label',[_vm._v("Line Charts"),_c('sup',[_vm._v("1")]),_c('sup',{staticClass:"warn"}),_vm._v(" "),_c('div',{staticClass:"append col col-10"},[_c('input',{ref:"info",attrs:{"type":"number","min":"20","id":"averagetimespan","value":"180","placeholder":"180"},on:{"change":_vm.onTrailingAverageChange}}),_c('span',[_vm._v("day average")])]),_vm._v(" "),_c('p'),_vm._v(" "),_c('h6',[_vm._v("Comparison Type")]),_vm._v(" "),_c('label',[_c('div',{staticClass:"form-item form-checkboxes"},[_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"zscore","type":"radio"},domProps:{"checked":_vm.compare == 'zscore'},on:{"change":_vm.onCompareChange}}),_vm._v("Z-score")]),_c('br'),_vm._v(" "),_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"baseline","type":"radio"},domProps:{"checked":_vm.compare == 'baseline'},on:{"change":_vm.onCompareChange}}),_vm._v("Baseline is compared")]),_vm._v(" "),_c('label',{staticClass:"checkbox"},[_c('input',{attrs:{"name":"comparebaseline","value":"rolling","type":"radio"},domProps:{"checked":_vm.compare == 'rolling'},on:{"change":_vm.onCompareChange}}),_vm._v("Rolling average")])])])]),_vm._v(" "),_c('br')])])])])])])])])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"col col-3",attrs:{"align":"center","id":"comparetext"}},[_c('h6',[_vm._v("Compare from your repos:")])])},function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"col col-12"},[_c('small',{staticClass:"warn"},[_vm._v(" - These options affect performance")])])}]
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

;require.register("components/MetricsStatusCard.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _AugurHeader = require('./AugurHeader');

var _AugurHeader2 = _interopRequireDefault(_AugurHeader);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {

  name: 'MetricsStatus',
  components: {
    AugurHeader: _AugurHeader2.default
  },
  data: function data() {
    return {
      metricsStatus: [],
      metadata: {
        metricStatusMetadata: [],
        groups: [],
        sources: [],
        metric_types: []
      },
      filters: {
        selected_group: 'all',
        selected_source: 'all',
        selected_metric_type: 'all',
        selected_backend_status: 'all',
        selected_frontend_status: 'all',
        seletec_is_defined: 'all'
      }
    };
  },

  methods: {
    getMetricsStatus: function getMetricsStatus() {
      var _this = this;

      var query_string = "group=" + this.selected_group + "&data_source=" + this.selected_source + "&metric_type=" + this.selected_metric_type + "&backend_status=" + this.selected_backend_status + "&frontend_status=" + this.selected_frontend_status + "&is_defined=" + this.selected_is_defined;

      window.AugurAPI.getMetricsStatus(query_string).then(function (data) {
        _this.metricsStatus = data;
      });
    },
    getMetricsStatusMetadata: function getMetricsStatusMetadata() {
      var _this2 = this;

      window.AugurAPI.getMetricsStatusMetadata().then(function (data) {
        _this2.metadata['metricStatusMetadata'] = data;

        _this2.metadata['groups'] = Object.keys(data[0].groups);

        _this2.metadata['data_sources'] = data[0].data_sources;

        _this2.metadata['metric_types'] = data[0].metric_types;
      });
    },
    getImplementationStatusColor: function getImplementationStatusColor(metric, location) {
      if (metric[location] == "unimplemented") {
        return "#c00";
      } else if (metric[location] == "implemented") {
        return "#0c0";
      }
    },
    getBackendStatusColor: function getBackendStatusColor(metric) {
      if (metric["backend_status"] == "unimplemented") {
        return "#c00";
      } else if (metric["backend_status"] == "implemented") {
        return "#0c0";
      }
    },
    getFrontendStatusColor: function getFrontendStatusColor(metric) {
      if (metric["frontend_status"] == "unimplemented") {
        return "#c00";
      } else if (metric["frontend_status"] == "implemented") {
        return "#0c0";
      }
    }
  },
  mounted: function mounted() {
    this.selected_group = 'all';
    this.selected_source = 'all';
    this.selected_metric_type = 'all';
    this.selected_backend_status = 'all';
    this.selected_frontend_status = 'all';
    this.selected_is_defined = 'all';
    this.getMetricsStatus();
    this.getMetricsStatusMetadata();
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"is-table-container"},[_c('div',{staticClass:"fullwidth"},[_c('augur-header')],1),_vm._v(" "),_c('section',[_c('h3',[_vm._v("CHAOSS Metrics Implementation Status")]),_vm._v(" "),_c('div',{staticClass:"row gutters"},[_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Group:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_group),expression:"selected_group"}],attrs:{"id":"metric_group"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_group=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},_vm._l((_vm.metadata['groups']),function(group){return _c('option',{domProps:{"value":group}},[_vm._v("\n        "+_vm._s(group)+"\n       ")])}))])]),_vm._v(" "),_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Source:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_source),expression:"selected_source"}],attrs:{"id":"metric_source"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_source=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},_vm._l((_vm.metadata['data_sources']),function(data_source){return _c('option',{domProps:{"value":data_source}},[_vm._v("\n        "+_vm._s(data_source)+"\n       ")])}))])]),_vm._v(" "),_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Metric Type:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_metric_type),expression:"selected_metric_type"}],attrs:{"id":"metric_type"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_metric_type=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},_vm._l((_vm.metadata['metric_types']),function(metric_type){return _c('option',{domProps:{"value":metric_type}},[_vm._v("\n        "+_vm._s(metric_type)+"\n       ")])}))])]),_vm._v(" "),_vm._m(0),_vm._v(" "),_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Backend Status:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_backend_status),expression:"selected_backend_status"}],attrs:{"id":"metric_backend_status"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_backend_status=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},[_c('option',{attrs:{"value":"all"}},[_vm._v("all")]),_vm._v(" "),_c('option',{attrs:{"value":"unimplemented"}},[_vm._v("unimplemented")]),_vm._v(" "),_c('option',{attrs:{"value":"implemented"}},[_vm._v("implemented")])])])]),_vm._v(" "),_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Frontend Status:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_frontend_status),expression:"selected_frontend_status"}],attrs:{"id":"metric_frontend_status"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_frontend_status=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},[_c('option',{attrs:{"value":"all"}},[_vm._v("all")]),_vm._v(" "),_c('option',{attrs:{"value":"unimplemented"}},[_vm._v("unimplemented")]),_vm._v(" "),_c('option',{attrs:{"value":"implemented"}},[_vm._v("implemented")])])])]),_vm._v(" "),_c('div',{staticClass:"col col-4"},[_c('label',[_vm._v("Defined:\n      "),_c('select',{directives:[{name:"model",rawName:"v-model",value:(_vm.selected_is_defined),expression:"selected_is_defined"}],attrs:{"id":"metric_is_defined"},on:{"change":[function($event){var $$selectedVal = Array.prototype.filter.call($event.target.options,function(o){return o.selected}).map(function(o){var val = "_value" in o ? o._value : o.value;return val}); _vm.selected_is_defined=$event.target.multiple ? $$selectedVal : $$selectedVal[0]},function($event){_vm.getMetricsStatus()}]}},[_c('option',{attrs:{"value":"all"}},[_vm._v("all")]),_vm._v(" "),_c('option',{attrs:{"value":"true"}},[_vm._v("true")]),_vm._v(" "),_c('option',{attrs:{"value":"false"}},[_vm._v("false")])])])])]),_vm._v(" "),_c('p'),_vm._v(" "),_c('table',{staticClass:"is-responsive"},[_vm._m(1),_vm._v(" "),_c('tbody',{staticStyle:{"display":"block","height":"400px","overflow-y":"scroll","text-align":"center","background":"#eaeaea"}},_vm._l((_vm.metricsStatus),function(metric){return _c('tr',[_c('div',{staticStyle:{"overflow":"hidden"}},[_c('td',{staticStyle:{"width":"119px !important"},style:({ color: _vm.getBackendStatusColor(metric) })},[_vm._v(_vm._s(metric.backend_status))]),_vm._v(" "),_c('td',{staticStyle:{"width":"135px !important"},style:({ color: _vm.getFrontendStatusColor(metric) })},[_vm._v(_vm._s(metric.frontend_status))]),_vm._v(" "),(metric.url != '/')?[_c('td',{staticStyle:{"width":"170px !important"}},[_c('a',{attrs:{"href":metric.documentation_url}},[_vm._v(_vm._s(metric.display_name))])])]:[_c('td',{staticStyle:{"width":"170px !important"}},[_vm._v(_vm._s(metric.display_name))])],_vm._v(" "),_c('td',{staticStyle:{"width":"121px !important"}},[_vm._v(_vm._s(metric.group))]),_vm._v(" "),_c('td',{staticStyle:{"width":"569px !important"}},[_vm._v(_vm._s(metric.endpoint))]),_vm._v(" "),_c('td',{staticStyle:{"width":"120px !important"}},[_vm._v(_vm._s(metric.data_source))]),_vm._v(" "),_c('td',{staticStyle:{"width":"85px !important"}},[_vm._v(_vm._s(metric.metric_type))])],2)])}))])])])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"col col-12"},[_c('br')])},function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('thead',{staticStyle:{"display":"block"}},[_c('tr',{staticStyle:{"font-weight":"600","text-align":"center"}},[_c('td',{staticStyle:{"width":"119px !important"}},[_vm._v("Backend Status")]),_vm._v(" "),_c('td',{staticStyle:{"width":"135px !important"}},[_vm._v("Frontend Status")]),_vm._v(" "),_c('td',{staticStyle:{"width":"170px !important"}},[_vm._v("Name")]),_vm._v(" "),_c('td',{staticStyle:{"width":"121px !important"}},[_vm._v("Group")]),_vm._v(" "),_c('td',{staticStyle:{"width":"569px !important"}},[_vm._v("Endpoint")]),_vm._v(" "),_c('td',{staticStyle:{"width":"120px !important"}},[_vm._v("Source")]),_vm._v(" "),_c('td',{staticStyle:{"width":"85px !important"}},[_vm._v("Metric Type")])])])}]
__vue__options__._scopeId = "data-v-99cabfb0"
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-99cabfb0", __vue__options__)
  } else {
    hotAPI.reload("data-v-99cabfb0", __vue__options__)
  }
})()}
});

;require.register("components/OverviewCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _AugurHeader = require('./AugurHeader');

var _AugurHeader2 = _interopRequireDefault(_AugurHeader);

var _TickChart = require('./charts/TickChart');

var _TickChart2 = _interopRequireDefault(_TickChart);

var _LinesOfCodeChart = require('./charts/LinesOfCodeChart');

var _LinesOfCodeChart2 = _interopRequireDefault(_LinesOfCodeChart);

var _NormalizedStackedBarChart = require('./charts/NormalizedStackedBarChart');

var _NormalizedStackedBarChart2 = _interopRequireDefault(_NormalizedStackedBarChart);

var _OneDimensionalStackedBarChart = require('./charts/OneDimensionalStackedBarChart');

var _OneDimensionalStackedBarChart2 = _interopRequireDefault(_OneDimensionalStackedBarChart);

var _HorizontalBarChart = require('./charts/HorizontalBarChart');

var _HorizontalBarChart2 = _interopRequireDefault(_HorizontalBarChart);

var _GroupedBarChart = require('./charts/GroupedBarChart');

var _GroupedBarChart2 = _interopRequireDefault(_GroupedBarChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    AugurHeader: _AugurHeader2.default,
    TickChart: _TickChart2.default,
    LinesOfCodeChart: _LinesOfCodeChart2.default,
    NormalizedStackedBarChart: _NormalizedStackedBarChart2.default,
    OneDimensionalStackedBarChart: _OneDimensionalStackedBarChart2.default,
    HorizontalBarChart: _HorizontalBarChart2.default,
    GroupedBarChart: _GroupedBarChart2.default,
    StackedBarChart: _StackedBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.gitRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('div',{staticClass:"row",staticStyle:{"transform":"translateY(-50px) !important"}},[_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgTpRankedCommits","title":"Top Repos in 2018 by Commits with Baseline Averages - Sorted","field":"commit"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgTpRankedLoc","title":"Top Repos in 2018 by Net LoC with Baseline Averages - Sorted","field":"loc"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgNewrepRankedCommits","title":"Top New Repos in 2018 by Commits with Baseline Averages - Sorted","field":"commit"}})],1),_vm._v(" "),_c('div',{staticClass:"col col-6",staticStyle:{"padding-right":"35px"}},[_c('grouped-bar-chart',{attrs:{"source":"cdRgNewrepRankedLoc","title":"Top New Repos in 2018 by Net LoC with Baseline Averages - Sorted","field":"loc"}})],1)])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-7117fe96", __vue__options__)
  } else {
    hotAPI.reload("data-v-7117fe96", __vue__options__)
  }
})()}
});

;require.register("components/RiskCard.vue", function(exports, require, module) {
;(function(){
"use strict";

window.onload = function () {
    document.getElementById("ciiBtn").addEventListener("click", function () {
        document.getElementById("overcii").style.display = "block";
        document.getElementById("overcii").class = "row";
        document.getElementById("ciiBtn").style.visibility = "hidden";
        var request = new XMLHttpRequest();
        function loader() {
            var basestr = document.getElementById("base").innerHTML;
            var augURL = 'https://github.com/' + basestr;
            request.open('GET', 'https://bestpractices.coreinfrastructure.org/projects.json?pq=' + augURL, true);
            request.onload = function () {
                var data = JSON.parse(this.response)[0];
                if (data != undefined) {
                    var badgeURL = 'https://bestpractices.coreinfrastructure.org/projects/' + data.id + '/badge';

                    document.getElementById("CIIbadge").src = badgeURL;
                    if (data.badge_percentage_0 < 100) {
                        document.getElementById("CII").innerHTML = data.name + ' is currently not passing CII Best Practices.';
                    } else if (data.badge_percentage_1 < 100) {
                        document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices.';
                    } else if (data.badge_percentage_2 < 100) {
                        document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices. This project has a siver status.';
                    } else if (data.badge_percentage_2 == 100) {
                        document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices. <br>' + data.name + ' maintains a gold status.';
                    }
                } else {
                    document.getElementById("CII").innerHTML = 'No best practice data for this repository.';
                }
            };
        }
        loader();
        request.send();
    });
};
module.exports = {
    data: function data() {
        return {
            colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
        };
    },

    components: {}
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Risk")]),_vm._v(" "),_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"},attrs:{"id":"base"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] }),attrs:{"id":"compared"}},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_c('h2',{staticClass:"col",staticStyle:{"margin-bottom":"20px"}},[_vm._v("CII Best Practices")]),_vm._v(" "),_c('button',{staticStyle:{"border":"2px solid black","width":"100%"},attrs:{"id":"ciiBtn"}},[_vm._v("Retrieve CII information")]),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticStyle:{"text-align":"center","width":"100%","display":"none"},attrs:{"id":"overcii"}},[_c('img',{staticClass:"col",staticStyle:{"width":"419px","height":"146px","margin-left":"auto","margin-right":"auto"},attrs:{"width":"200px","height":"200px","src":"https://i.ibb.co/n8f7NjX/CIITPARENT.png","href":"https://bestpractices.coreinfrastructure.org/en"}}),_vm._v(" "),_c('br'),_vm._v(" "),_c('div',{staticClass:"col-6",staticStyle:{"margin-left":"auto","margin-right":"auto","margin-top":"20px"},attrs:{"id":"CIIbp"}},[_c('div',{attrs:{"size":"total"}},[_c('img',{staticStyle:{"transform":"scale(2)"},attrs:{"id":"CIIbadge"}}),_vm._v(" "),_c('br'),_vm._v(" "),_c('h2',{attrs:{"id":"CII"}})])])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-0abc386c", __vue__options__)
  } else {
    hotAPI.reload("data-v-0abc386c", __vue__options__)
  }
})()}
});

;require.register("components/TableView.vue", function(exports, require, module) {
;(function(){
'use strict';

var _vueMultiselect = require('vue-multiselect');

var _vueMultiselect2 = _interopRequireDefault(_vueMultiselect);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  components: {
    Multiselect: _vueMultiselect2.default
  },
  data: function data() {
    return {
      clipped: true,
      drawer: true,
      fixed: false,
      items: [{ icon: 'bubble_chart', title: 'Inspire' }],
      miniVariant: false,
      right: true,
      rightDrawer: false,
      title: 'Vuetify.js',
      dialog: false,
      headers: [{
        text: 'Dessert (100g serving)',
        align: 'left',
        sortable: false,
        value: 'name'
      }, { text: 'Calories', value: 'calories' }, { text: 'Fat (g)', value: 'fat' }, { text: 'Carbs (g)', value: 'carbs' }, { text: 'Protein (g)', value: 'protein' }, { text: 'Actions', value: 'name', sortable: false }],
      desserts: [],
      editedIndex: -1,
      editedItem: {
        name: '',
        calories: 0,
        fat: 0,
        carbs: 0,
        protein: 0
      },
      defaultItem: {
        name: '',
        calories: 0,
        fat: 0,
        carbs: 0,
        protein: 0
      },
      listPrimitive: null
    };
  },

  computed: {
    formTitle: function formTitle() {
      return this.editedIndex === -1 ? 'New Item' : 'Edit Item';
    }
  },
  watch: {
    dialog: function dialog(val) {
      val || this.close();
    }
  },
  mounted: function mounted() {},
  methods: {
    initialise: function initialise(hamoni) {
      var _this = this;

      hamoni.createList("vue-table", [{
        name: 'Frozen Yogurt',
        calories: 159,
        fat: 6.0,
        carbs: 24,
        protein: 4.0
      }, {
        name: 'Ice cream sandwich',
        calories: 237,
        fat: 9.0,
        carbs: 37,
        protein: 4.3
      }, {
        name: 'Eclair',
        calories: 262,
        fat: 16.0,
        carbs: 23,
        protein: 6.0
      }]).then(function (primitive) {
        _this.listPrimitive = primitive;
        _this.desserts = _this.listPrimitive.getAll();
        _this.subscribeToUpdate();
      }).catch(alert);
    },
    subscribeToUpdate: function subscribeToUpdate() {
      var _this2 = this;

      this.listPrimitive.onItemAdded(function (item) {
        _this2.desserts.push(item.value);
      });
      this.listPrimitive.onItemUpdated(function (item) {
        _this2.desserts.splice(item.index, 1, item.value);
      });
      this.listPrimitive.onItemRemoved(function (item) {
        _this2.desserts.splice(item.index, 1);
      });
    },
    editItem: function editItem(item) {
      this.editedIndex = this.desserts.indexOf(item);
      this.editedItem = Object.assign({}, item);
      this.dialog = true;
    },
    deleteItem: function deleteItem(item) {
      var index = this.desserts.indexOf(item);
      confirm('Are you sure you want to delete this item?') && this.listPrimitive.remove(index);
    },
    close: function close() {
      var _this3 = this;

      this.dialog = false;
      setTimeout(function () {
        _this3.editedItem = Object.assign({}, _this3.defaultItem);
        _this3.editedIndex = -1;
      }, 300);
    },
    save: function save() {
      if (this.editedIndex > -1) {
        this.listPrimitive.update(this.editedIndex, this.editedItem);
      } else {
        this.listPrimitive.add(this.editedItem);
      }
      this.close();
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('v-dialog',{attrs:{"max-width":"500px"},model:{value:(_vm.dialog),callback:function ($$v) {_vm.dialog=$$v},expression:"dialog"}},[_c('v-btn',{staticClass:"mb-2",attrs:{"slot":"activator","color":"primary","dark":""},slot:"activator"},[_vm._v("New Item")]),_vm._v(" "),_c('v-card',[_c('v-card-title',[_c('span',{staticClass:"headline"},[_vm._v(_vm._s(_vm.formTitle))])]),_vm._v(" "),_c('v-card-text',[_c('v-container',{attrs:{"grid-list-md":""}},[_c('v-layout',{attrs:{"wrap":""}},[_c('v-flex',{attrs:{"xs12":"","sm6":"","md4":""}},[_c('v-text-field',{attrs:{"label":"Dessert name"},model:{value:(_vm.editedItem.name),callback:function ($$v) {_vm.$set(_vm.editedItem, "name", $$v)},expression:"editedItem.name"}})],1),_vm._v(" "),_c('v-flex',{attrs:{"xs12":"","sm6":"","md4":""}},[_c('v-text-field',{attrs:{"label":"Calories"},model:{value:(_vm.editedItem.calories),callback:function ($$v) {_vm.$set(_vm.editedItem, "calories", $$v)},expression:"editedItem.calories"}})],1),_vm._v(" "),_c('v-flex',{attrs:{"xs12":"","sm6":"","md4":""}},[_c('v-text-field',{attrs:{"label":"Fat (g)"},model:{value:(_vm.editedItem.fat),callback:function ($$v) {_vm.$set(_vm.editedItem, "fat", $$v)},expression:"editedItem.fat"}})],1),_vm._v(" "),_c('v-flex',{attrs:{"xs12":"","sm6":"","md4":""}},[_c('v-text-field',{attrs:{"label":"Carbs (g)"},model:{value:(_vm.editedItem.carbs),callback:function ($$v) {_vm.$set(_vm.editedItem, "carbs", $$v)},expression:"editedItem.carbs"}})],1),_vm._v(" "),_c('v-flex',{attrs:{"xs12":"","sm6":"","md4":""}},[_c('v-text-field',{attrs:{"label":"Protein (g)"},model:{value:(_vm.editedItem.protein),callback:function ($$v) {_vm.$set(_vm.editedItem, "protein", $$v)},expression:"editedItem.protein"}})],1)],1)],1)],1),_vm._v(" "),_c('v-card-actions',[_c('v-spacer'),_vm._v(" "),_c('v-btn',{attrs:{"color":"blue darken-1","flat":""},nativeOn:{"click":function($event){return _vm.close($event)}}},[_vm._v("Cancel")]),_vm._v(" "),_c('v-btn',{attrs:{"color":"blue darken-1","flat":""},nativeOn:{"click":function($event){return _vm.save($event)}}},[_vm._v("Save")])],1)],1)],1),_vm._v(" "),_c('v-data-table',{staticClass:"elevation-1",attrs:{"headers":_vm.headers,"items":_vm.desserts,"hide-actions":""},scopedSlots:_vm._u([{key:"items",fn:function(props){return [_c('td',[_vm._v(_vm._s(props.item.name))]),_vm._v(" "),_c('td',{staticClass:"text-xs-right"},[_vm._v(_vm._s(props.item.calories))]),_vm._v(" "),_c('td',{staticClass:"text-xs-right"},[_vm._v(_vm._s(props.item.fat))]),_vm._v(" "),_c('td',{staticClass:"text-xs-right"},[_vm._v(_vm._s(props.item.carbs))]),_vm._v(" "),_c('td',{staticClass:"text-xs-right"},[_vm._v(_vm._s(props.item.protein))]),_vm._v(" "),_c('td',{staticClass:"justify-center layout px-0"},[_c('v-btn',{staticClass:"mx-0",attrs:{"icon":""},on:{"click":function($event){_vm.editItem(props.item)}}},[_c('v-icon',{attrs:{"color":"teal"}},[_vm._v("edit")])],1),_vm._v(" "),_c('v-btn',{staticClass:"mx-0",attrs:{"icon":""},on:{"click":function($event){_vm.deleteItem(props.item)}}},[_c('v-icon',{attrs:{"color":"pink"}},[_vm._v("delete")])],1)],1)]}}])})],1)}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-6147dc76", __vue__options__)
  } else {
    hotAPI.reload("data-v-6147dc76", __vue__options__)
  }
})()}
});

;require.register("components/Tabs.vue", function(exports, require, module) {
;(function(){
'use strict';

module.exports = {
  props: ['owner', 'repo', 'comparedowner', 'comparedrepo', 'groupid'],
  computed: {
    gitRepo: function gitRepo() {
      return this.$store.state.gitRepo;
    },
    currentTab: function currentTab() {
      return this.$store.state.tab;
    },
    baseRepo: function baseRepo() {
      return this.$store.state.baseRepo;
    },
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    }
  },
  methods: {
    changeTab: function changeTab(e) {
      console.log("changing tab to: ", e.target.dataset.value);
      this.$store.commit('setTab', {
        tab: e.target.dataset.value
      });
      if (this.$store.state.comparedRepos.length == 1) {
        var owner = this.gitRepo ? null : this.baseRepo.split('/')[0];
        var repo = this.gitRepo ? this.gitRepo : this.baseRepo.split('/')[1];
        var comparedowner = this.comparedRepos[0].split('/').length > 2 ? null : this.comparedRepos[0].split('/')[0];
        var comparedrepo = this.comparedRepos[0].split('/').length > 2 ? this.comparedRepos[0] : this.comparedRepos[0].split('/')[1];
        var name = e.target.dataset['value'] + "compare";
        this.$router.push({
          name: name,
          params: { owner: owner, repo: repo, comparedowner: comparedowner, comparedrepo: comparedrepo }
        });
      } else if (this.$store.state.comparedRepos.length > 1) {
        var groupid = this.gitRepo ? String(this.gitRepo) + '+' : String(state.baseRepo) + "+";
        this.comparedRepos.forEach(function (repo) {
          groupid += String(repo) + '+';
        });
        var _name = e.target.dataset['value'] + "group";
        this.$router.push({
          name: _name,
          params: { groupid: groupid }
        });
      } else {
        var _owner = this.gitRepo ? null : this.baseRepo.split('/')[0];
        var _repo = this.gitRepo ? this.gitRepo : this.baseRepo.split('/')[1];
        this.$router.push({
          name: e.target.dataset['value'],
          params: { owner: _owner, repo: _repo }
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('nav',{staticClass:"tabs"},[_c('ul',[_c('li',{class:{ active: (_vm.currentTab == 'gmd') }},[_c('a',{attrs:{"href":"#","data-value":"gmd"},on:{"click":_vm.changeTab}},[_vm._v("Growth, Maturity, and Decline")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'diversityinclusion') }},[_c('a',{attrs:{"href":"#","data-value":"diversityinclusion"},on:{"click":_vm.changeTab}},[_vm._v("Diversity and Inclusion")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'risk') }},[_c('a',{attrs:{"href":"#","data-value":"risk"},on:{"click":_vm.changeTab}},[_vm._v("Risk")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'value') }},[_c('a',{attrs:{"href":"#","data-value":"value"},on:{"click":_vm.changeTab}},[_vm._v("Value")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'activity') }},[_c('a',{attrs:{"href":"#","data-value":"activity"},on:{"click":_vm.changeTab}},[_vm._v("Activity")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'experimental') }},[_c('a',{attrs:{"href":"#","data-value":"experimental"},on:{"click":_vm.changeTab}},[_vm._v("Experimental")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'git'), hidden: !_vm.gitRepo }},[_c('a',{attrs:{"href":"#","data-value":"git"},on:{"click":_vm.changeTab}},[_vm._v("Git")])]),_vm._v(" "),_c('li',{class:{ active: (_vm.currentTab == 'overview'), hidden: !_vm.gitRepo }},[_c('a',{attrs:{"href":"#","data-value":"overview"},on:{"click":_vm.changeTab}},[_vm._v("Overview")])])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-004f2c6b", __vue__options__)
  } else {
    hotAPI.reload("data-v-004f2c6b", __vue__options__)
  }
})()}
});

;require.register("components/ValueCard.vue", function(exports, require, module) {
;(function(){
'use strict';

var _DynamicLineChart = require('./charts/DynamicLineChart');

var _DynamicLineChart2 = _interopRequireDefault(_DynamicLineChart);

var _BubbleChart = require('./charts/BubbleChart');

var _BubbleChart2 = _interopRequireDefault(_BubbleChart);

var _StackedBarChart = require('./charts/StackedBarChart');

var _StackedBarChart2 = _interopRequireDefault(_StackedBarChart);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

module.exports = {
  data: function data() {
    return {
      colors: ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    };
  },

  components: {
    DynamicLineChart: _DynamicLineChart2.default,
    BubbleChart: _BubbleChart2.default,
    StackedBarChart: _StackedBarChart2.default
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('section',[_c('h1',[_vm._v("Value")]),_vm._v(" "),_c('div',{staticStyle:{"display":"inline-block"}},[_c('h2',{staticStyle:{"display":"inline-block","color":"black !important"}},[_vm._v(_vm._s(_vm.$store.state.baseRepo))]),_vm._v(" "),(_vm.$store.state.comparedRepos.length > 0)?_c('h2',{staticClass:"repolisting",staticStyle:{"display":"inline-block"}},[_vm._v(" compared to: ")]):_vm._e(),_vm._v(" "),_vm._l((_vm.$store.state.comparedRepos),function(repo,index){return _c('h2',{staticStyle:{"display":"inline-block"}},[_c('span',{staticClass:"repolisting",style:({ 'color': _vm.colors[index] })},[_vm._v(" "+_vm._s(repo)+" ")])])})],2),_vm._v(" "),_vm._m(0)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticClass:"row"},[_c('p',[_vm._v("We currently do not have any metrics developed for this group.")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-5e0cf204", __vue__options__)
  } else {
    hotAPI.reload("data-v-5e0cf204", __vue__options__)
  }
})()}
});

;require.register("components/charts/BubbleChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var spec = {
  "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
  "spec": {
    "hconcat": [{
      "title": "Code Engagement",
      "width": 475,
      "height": 300,
      "mark": {
        "type": "circle",
        "cursor": "pointer"
      },
      "transform": [{
        "calculate": "'https://www.google.com/search?q=' + datum.name", "as": "url"
      }],
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover"
        },
        "grid": {
          "type": "interval", "bind": "scales"
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
        "tooltip": {
          "field": "name",
          "type": "nominal"
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
      "width": 475,
      "height": 300,
      "mark": {
        "type": "circle",
        "cursor": "pointer"
      },
      "transform": [{
        "calculate": "'https://www.google.com/search?q=' + datum.name", "as": "url"
      }],
      "selection": {
        "paintbrush": {
          "type": "single",
          "on": "mouseover"
        },
        "grid": {
          "type": "interval", "bind": "scales"
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
          "tooltip": {
            "field": "name",
            "type": "nominal"
          },

          "value": "grey"
        }
      }
    }]
  }
};

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'comparedTo'],
  data: function data() {
    return {
      values: []
    };
  },

  components: {
    'vega-interactive': window.VueVega.mapVegaLiteSpec(spec)
  },
  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    showBelowAverage: function showBelowAverage() {
      return this.$store.state.showBelowAverage;
    },
    chart: function chart() {
      var _this = this;

      var removeBelowAverageContributors = !this.showBelowAverage;
      $(this.$el).find('.showme').addClass('invis');
      $(this.$el).find('.bubblechart').addClass('loader');
      var shared = {};
      var processData = function processData(data) {
        window.AugurRepos[_this.repo][_this.source]().then(function (data) {
          shared.baseData = data.map(function (e) {
            e.repo = _this.repo.toString();return e;
          });
          if (removeBelowAverageContributors) {
            shared.baseData = _AugurStats2.default.aboveAverage(shared.baseData, 'total');
          }
          if (_this.comparedTo) {
            return window.AugurRepos[_this.comparedTo].contributors();
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
            if (removeBelowAverageContributors) {
              compareData = _AugurStats2.default.aboveAverage(compareData, 'total');
            }
            _this.values = _.concat(shared.baseData, compareData);
          } else {
            _this.values = shared.baseData;
          }
          $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
          $(_this.$el).find('.bubblechart').removeClass('loader');
        });
      };
      if (this.repo) {

        if (this.data) {
          processData(this.data);
        } else {
          window.AugurRepos[this.repo][this.source]().then(function (data) {
            shared.baseData = data.map(function (e) {
              e.repo = _this.repo.toString();return e;
            });
            if (removeBelowAverageContributors) {
              shared.baseData = _AugurStats2.default.aboveAverage(shared.baseData, 'total');
            }
            if (_this.comparedTo) {
              return window.AugurRepos[_this.comparedTo].contributors();
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
              if (removeBelowAverageContributors) {
                compareData = _AugurStats2.default.aboveAverage(compareData, 'total');
              }
              _this.values = _.concat(shared.baseData, compareData);
            } else {
              _this.values = shared.baseData;
            }
            $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
            $(_this.$el).find('.bubblechart').removeClass('loader');
          });
        }
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

;require.register("components/charts/BusFactor.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title'],
  data: function data() {
    return {
      values: []
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    chart: function chart() {
      var _this = this;

      $(this.$el).find('.showme').addClass('invis');
      $(this.$el).find('.textchart').addClass('loader');
      if (this.repo) {
        window.AugurRepos[this.repo][this.source]().then(function (data) {
          $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
          $(_this.$el).find('.textchart').removeClass('loader');
          _this.values = data;
          console.log('Data:');
          console.log(data);
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"textchart hidefirst invis"},[_c('h3',[_vm._v(_vm._s(_vm.title))]),_vm._v(" "),_c('table',[_c('tr',[_c('th',[_vm._v("Best:")]),_vm._v(" "),_c('td',[_vm._v(_vm._s((_vm.values[0]) ? _vm.values[0].best : undefined))])]),_vm._v(" "),_c('tr',[_c('th',[_vm._v("Worst")]),_vm._v(" "),_c('td',[_vm._v(_vm._s((_vm.values[0]) ? _vm.values[0].worst : undefined))])])]),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-410e1f3c", __vue__options__)
  } else {
    hotAPI.reload("data-v-410e1f3c", __vue__options__)
  }
})()}
});

;require.register("components/charts/DependencyOverview.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _AugurStats = require('../../AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

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

        this.$refs['dependents'].innerHTML = 'Loading...';
        window.AugurRepos[this.repo].dependents().then(function (dependents) {
          if (!dependents || !dependents.length) {
            _this.$refs['dependents'].innerHTML = 'No dependents found.';
          }
          _this.$refs['dependents'].innerHTML = '';
          for (var i = 0; i < dependents.length && i < 10; i++) {
            _this.$refs['dependents'].innerHTML += dependents[i].name + '<br>';
          }
        }, function () {
          _this.$refs['dependents'].innerHTML = 'No data.';
        });

        this.$refs['dependencies'].innerHTML = '';
        window.AugurRepos[this.repo].dependencies().then(function (dependencies) {
          if (!dependencies || !dependencies.length) {
            _this.$refs['dependencies'].innerHTML = 'No dependencies found.';
          }
          _this.$refs['dependencies'].innerHTML = '';
          for (var i = 0; i < dependencies.dependencies.length && i < 10; i++) {
            _this.$refs['dependencies'].innerHTML += dependencies.dependencies[i].name + '<br>';
          }
        }, function () {
          _this.$refs['dependencies'].innerHTML = 'No data.';
        });
      }
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',[_c('div',{staticClass:"row"},[_c('div',{staticClass:"col col-6"},[_c('h3',[_vm._v("Top Dependents")]),_vm._v(" "),_c('div',{ref:"dependents",staticClass:"deps"},[_vm._v("\n        Loading...\n      ")])]),_vm._v(" "),_c('div',{staticClass:"col col-6"},[_c('h3',[_vm._v("Top Dependencies")]),_vm._v(" "),_c('div',{ref:"dependencies",staticClass:"deps"},[_vm._v("\n        Loading...\n      ")])])])])}
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

;require.register("components/charts/DirectionalTimeChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'field'],
  data: function data() {
    return {
      values: []
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    gitRepo: function gitRepo() {
      return this.$store.state.gitRepo;
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
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    },
    rawWeekly: function rawWeekly() {
      return this.$store.state.rawWeekly;
    },
    showArea: function showArea() {
      return this.$store.state.showArea;
    },
    showTooltip: function showTooltip() {
      return this.$store.state.showTooltip;
    },
    showDetail: function showDetail() {
      return this.$store.state.showDetail;
    },
    months: function months() {
      return { 1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
      };
    },
    spec: function spec() {
      var _this = this;

      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
        "padding": { 'left': 45, 'top': 10, 'right': 70, 'bottom': 50 },
        "config": {
          "bar": {
            "discreteBandSize": 10
          }
        },
        "title": {
          "text": this.title,

          "offset": 10
        },
        "width": 420,
        "height": 250,
        "layer": [{
          "mark": "text",
          "encoding": {
            "text": {
              "field": "month", "type": "nominal",
              "axis": { "title": "" }
            },
            "y": {
              "field": "net_lines_minus_whitespace", "type": "quantitative",
              "axis": { "title": "net loc" }
            },
            "x": {
              "field": "commits", "type": 'quantitative',

              "axis": { "title": "commits" }
            },
            "color": {
              "field": "month", "type": "ordinal",
              "scale": { "range": ["black", "#CC0314", "#1403CC", "#098118", "#CCAE00", "#C24F00", "#5E0081", "#0FA1C1", "#BD00B3"] }
            }
          }
        }, {

          "mark": "point",
          "encoding": {
            "y": {
              "field": "next_y1", "type": "quantitative",
              "axis": { "title": "", "labels": false }
            },
            "x": {
              "field": "next_x1", "type": 'quantitative',
              "axis": { "title": "", "labels": false }
            },
            "color": {
              "field": "month", "type": "ordinal",
              "scale": { "range": ["black", "#CC0314", "#1403CC", "#098118", "#CCAE00", "#C24F00", "#5E0081", "#0FA1C1", "#BD00B3"] }
            }
          }
        }],
        "resolve": { "scale": { "y": "independent", "x": "independent" } }
      };

      var repos = [];
      if (this.gitRepo) {
        repos.push(window.AugurAPI.Repo({ gitURL: this.gitRepo }));
      }
      var endpoints = [];
      var fields = {};
      this.source.split(',').forEach(function (endpointAndFields) {
        var split = endpointAndFields.split(':');
        endpoints.push(split[0]);
        if (split[1]) {
          fields[split[0]] = split[1].split('+');
        }
      });
      if (this.data) {
        processGitData(this.data);
      } else {
        var repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
        repo[this.source]().then(function (data) {
          console.log("batch data", data);
          processData(data);
        }, function () {});
      }
      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');
      var processGitData = function processGitData(data) {
        var repo = window.AugurAPI.Repo({ gitURL: _this.repo });
        var dat = [];
        repo.changesByAuthor().then(function (changes) {
          dat.push(changes);
        });
      };
      var defaultProcess = function defaultProcess(obj, key) {
        var d = null;
        if (typeof field == "string") field = [field];
        d = _AugurStats2.default.convertKey(obj[key], key);
        return d;
      };
      var processData = function processData(data) {
        console.log(repos, data, "CHECK");
        var sort = _this.field == 'commit' ? "patches" : "net";
        data.sort(function (a, b) {
          return b[sort] - a[sort];
        });
        console;
        for (var i = 0; i < data.length - 1; i++) {
          var diffLoc = data[i + 1]['net_lines_minus_whitespace'] - data[i]['net_lines_minus_whitespace'];
          var diffCom = data[i + 1]['commits'] - data[i]['commits'];
          data[i]['next_y1'] = data[i]['net_lines_minus_whitespace'] + diffLoc / 10;
          data[i]['next_x1'] = data[i]['commits'] + diffCom / 10;
          data[i]['next_y2'] = data[i]['net_lines_minus_whitespace'] + diffLoc / 10;
          data[i]['next_x2'] = data[i]['commits'] + diffCom / 10 - data[i]['commits'] / 20;
          data[i]['next_y3'] = data[i]['net_lines_minus_whitespace'] + (data[i + 1]['net_lines_minus_whitespace'] - data[i]['net_lines_minus_whitespace']) / 10;
          data[i]['next_x3'] = data[i]['commits'] + (data[i + 1]['commits'] - data[i]['commits']) / 10;
        }
        data.forEach(function (el) {

          el.month = _this.months[el.month];
        });
        repos.forEach(function (repo) {
          console.log("repo data", data);
          _this.values = data;
        });
      };
      return config;
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"groupedbarchart"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-6196c9b8", __vue__options__)
  } else {
    hotAPI.reload("data-v-6196c9b8", __vue__options__)
  }
})()}
});

;require.register("components/charts/DualAxisContributions.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
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
    };
  },
  created: function created() {
    this.tick = 0;
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    spec: function spec() {
      var _this = this;

      var type = null,
          bin = null,
          size = null,
          opacity = null;

      if (this.tick == 0) {
        type = "circle";
        bin = false;
        size = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": "15",
          "scale": { "minSize": 30, "maxSize": 31 }
        };
        opacity = {};
      }
      if (this.tick == 1) {
        type = "tick";
        bin = false;
        size = {};
        opacity = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": ".5"
        };
      }
      if (this.tick == 2) {
        type = "rect";
        bin = { "maxbins": 40 };
        size = {};
        opacity = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": ".5"
        };
      }

      var config = _defineProperty({
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
            "title": null
          },
          "legend": {
            "titleFontSize": 10,
            "titlePadding": 10
          }, "scale": { "minSize": 100, "maxSize": 500 }
        },
        "layer": [{
          "transform": [],
          "mark": "bar",
          "encoding": {
            "y": {
              "field": "commits", "type": "quantitative",
              "axis": { "grid": false }
            },
            "x": {
              "field": "month", "type": "temporal",
              "axis": { "title": "" }
            },
            "color": {
              "value": "red"
            }
          }
        }, {
          "transform": [{
            "window": [{
              "op": "sum",
              "field": "commits",
              "as": "avg_commits"
            }]
          }],
          "mark": "text",
          "encoding": {
            "text": { "field": "avg_commits", "type": "quantitative" },
            "y": { "value": 10 },
            "x": {
              "field": "month", "type": "temporal",
              "axis": { "title": "" }
            },
            "color": {
              "value": "black"
            }
          }
        }, {
          "transform": [],
          "mark": "bar",
          "encoding": {
            "y": {
              "field": "rate", "type": "quantitative",
              "axis": { "grid": false }
            },
            "x": {
              "field": "month", "type": "temporal",
              "axis": { "title": "" }
            },
            "color": {
              "value": "blue"
            }
          }
        }],
        "resolve": { "scale": { "y": "independent" } }
      }, 'config', {
        "view": { "stroke": "transparent" },
        "axis": { "domainWidth": 1 }
      });

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      repo.cdRepTpIntervalLocCommits().then(function (changes) {
        console.log("CHANGE", changes);

        _this.values = changes;
      });

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      return config;
    }
  }

};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"tickchart "},[_c('h3',[_vm._v("Contributions By Time Interval for 2018")]),_vm._v(" "),_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-2da7ab99", __vue__options__)
  } else {
    hotAPI.reload("data-v-2da7ab99", __vue__options__)
  }
})()}
});

;require.register("components/charts/DynamicLineChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'domain', 'data'],
  data: function data() {
    return {
      legendLabels: [],
      values: [],
      status: {},
      detail: this.$store.state.showDetail,
      compRepos: this.$store.state.comparedRepos,
      metricSource: null,
      timeperiod: 'all',
      forceRecomputeCounter: 0
    };
  },

  watch: {
    compRepos: function compRepos() {
      var allFalse = true;
      for (var key in this.status) {
        if (this.status[key]) allFalse = false;
      }if (allFalse) {
        $(this.$el).find('.spinner').addClass('loader');
        $(this.$el).find('.error').addClass('hidden');
      }
      $(this.$el).find('.hidefirst').addClass('invis');
      $(this.$el).find('.hidefirst').addClass('invisDet');
      $(this.$el).find('.spinner').addClass('loader');
      $(this.$el).find('.spacing').removeClass('hidden');
    }
  },
  beforeUpdate: function beforeUpdate() {
    this.$store.watch(function (state) {
      console.log("WORKED");
      this.thisShouldTriggerRecompute();
      return;
    });
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    gitRepos: function gitRepos() {
      return this.$store.state.gitRepo;
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
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    },
    rawWeekly: function rawWeekly() {
      return this.$store.state.rawWeekly;
    },
    showArea: function showArea() {
      return this.$store.state.showArea;
    },
    showTooltip: function showTooltip() {
      return this.$store.state.showTooltip;
    },
    showDetail: function showDetail() {
      return this.$store.state.showDetail;
    },
    spec: function spec() {
      var _this = this;

      this.forceRecomputeCounter;

      var repos = [];
      if (this.repo) {
        if (window.AugurRepos[this.repo]) repos.push(window.AugurRepos[this.repo]);else if (this.domain) {
          var temp = window.AugurAPI.Repo({ "gitURL": this.gitRepo });
          if (window.AugurRepos[temp]) temp = window.AugurRepos[temp];else window.AugurRepos[temp] = temp;
          repos.push(temp);
        }
      }
      this.comparedRepos.forEach(function (repo) {
        repos.push(window.AugurRepos[repo]);
      });

      repos.forEach(function (repo) {
        _this.status[repo] = true;
      });

      var colors = ["black", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"];
      var brush = { "filter": { "selection": "brush" } };
      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "config": {
          "axis": {
            "grid": false
          },
          "legend": {
            "offset": -505,
            "titleFontSize": 0,
            "titlePadding": 10
          }
        },
        "vconcat": [{
          "title": {
            "text": this.title,
            "offset": 15
          },
          "width": 520,
          "height": 250,
          "layer": [{
            "transform": [brush],
            "mark": "rule",
            "encoding": {
              "x": {
                "field": "date",
                "type": "temporal",
                "axis": {
                  "labels": !this.showDetail
                }
              },
              "color": {
                "field": "name",
                "type": "nominal",
                "scale": { "range": colors },
                "sort": false
              },
              "opacity": {
                "value": 0
              }
            }

          }]
        }]
      };

      if (!this.showDetail) brush = { "filter": "datum.date > 0" };

      var selectionAdded = false;

      var getStandardLine = function getStandardLine(key, color) {
        var raw = key.substring(key.length - 7) == "Rolling" ? false : true;
        return {
          "transform": [brush],
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": {
                "labels": !_this.showDetail,
                "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": color
            }
          },
          "mark": {
            "type": "line",

            "clip": true
          }
        };
      };

      var getRawLine = function getRawLine(key, color) {
        var raw = key.substring(key.length - 7) == "Rolling" ? false : true;
        return {
          "transform": [brush],
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": {
                "labels": !_this.showDetail,
                "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": color
            },
            "opacity": { "value": .3 }
          },
          "mark": {
            "type": "line",

            "clip": true
          }
        };
      };

      var getToolPoint = function getToolPoint(key) {
        var selection = !selectionAdded ? {
          "tooltip": {
            "type": "single",
            "on": "mouseover",
            "encodings": ["x"],
            "empty": "none"
          }
        } : null;
        var size = 17;
        var timeDiff = Math.abs(_this.latest.getTime() - _this.earliest.getTime());
        var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
        size = diffDays / 150;
        if (_this.rawWeekly) size = 3;
        selectionAdded = true;
        return {
          "transform": [brush],
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": { "format": "%b %Y", "title": " " }
            },
            "opacity": {
              "value": 0
            },
            "color": {
              "value": "black"
            },
            "size": {
              "value": size
            }
          },
          "mark": {
            "type": "rule",
            "clip": true
          },
          "selection": selection
        };
      };

      var getStandardPoint = function getStandardPoint(key, color) {
        var selection = !selectionAdded ? {
          "tooltip": {
            "type": "single",
            "on": "mouseover",
            "encodings": ["x"],
            "empty": "none"
          }
        } : null;
        selectionAdded = true;
        var raw = key.substring(key.length - 7) == "Rolling" ? false : true;
        return {
          "transform": [brush],
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": {
                "title": " ",
                "format": "%b %Y"
              }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": "black"
            },
            "opacity": {
              "condition": {
                "selection": "tooltip",
                "value": 1
              },
              "value": 0
            }
          },
          "mark": {
            "type": "point"
          },
          "selection": selection
        };
      };

      var getArea = function getArea(extension) {
        return {
          "transform": [brush],
          "mark": {
            "type": "area",
            "interpolate": "basis",
            "clip": true
          },
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": { "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": "lower" + extension,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "y2": {
              "field": "upper" + extension,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": "gray"
            },
            "opacity": { "value": 0.14 }
          }
        };
      };

      var rule = {
        "transform": [{
          "filter": {
            "selection": "tooltip"
          }
        }, brush],
        "mark": "rule",
        "encoding": {
          "x": {
            "type": "temporal",
            "field": "date",
            "axis": { "format": "%b %Y", "title": " " }
          },
          "color": {
            "value": "black"
          }
        }
      };

      var getValueText = function getValueText(key) {
        return {

          "transform": [{
            "filter": {
              "selection": "tooltip"
            }
          }, brush],
          "mark": {
            "type": "text",
            "align": "left",
            "dx": 5,
            "dy": -5
          },
          "encoding": {
            "text": {
              "type": "quantitative",
              "field": key
            },
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": { "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": "green"
            }
          }
        };
      };

      var getDateText = function getDateText(key) {
        return {

          "transform": [{
            "filter": {
              "selection": "tooltip"
            }
          }, brush],
          "mark": {
            "type": "text",
            "align": "left",
            "dx": 5,
            "dy": -15
          },
          "encoding": {
            "text": {
              "type": "temporal",
              "field": "date"
            },
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": { "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "color": {
              "value": "black"
            }
          }
        };
      };

      var getDetail = function getDetail(key) {
        var color = _this.comparedTo && _this.status.compared ? '#FF3647' : 'black';
        return {
          "width": 520,
          "height": 60,
          "mark": "line",
          "title": {
            "text": " "
          },
          "selection": {
            "brush": { "type": "interval", "encodings": ["x"] }
          },
          "encoding": {
            "x": {
              "field": "date",
              "type": "temporal",
              "axis": { "format": "%b %Y", "title": " " }
            },
            "y": {
              "field": key,
              "type": "quantitative",
              "axis": {
                "title": null
              }
            },
            "opacity": {
              "value": 0.5
            },
            "color": {
              "value": color
            }
          }

        };
      };

      if (this.showArea && repos.length < 3) {
        repos.forEach(function (repo) {
          config.vconcat[0].layer.push(getArea(repo));
        });
      } else {
        repos.forEach(function (repo) {
          for (var x = 0; x < config.vconcat[0].layer.length; x++) {
            if (config.vconcat[0].layer[x] == getArea(repo)) {
              config.vconcat[0].layer[x] = {};
              buildMetric();
            }
          }
        });
      }

      var buildMetric = function buildMetric() {
        var color = 0;
        repos.forEach(function (repo) {
          buildLines("valueRolling" + repo, colors[color]);

          if (_this.rawWeekly) config.vconcat[0].layer.push(getRawLine("value" + repo, colors[color]));

          if (_this.showDetail) config.vconcat[1] = getDetail("valueRolling" + _this.repo);else if (config.vconcat[1]) config.vconcat.pop();
          color++;
        });
      };

      var buildLines = function buildLines(key, color) {
        config.vconcat[0].layer.push(getStandardLine(key, color));
      };

      var buildTooltip = function buildTooltip(key) {
        config.vconcat[0].layer.push(getToolPoint(key));
        if (repos.length < 3) {
          var col = -1;
          repos.forEach(function (repo) {
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

      if (this.showTooltip) {
        repos.forEach(function (repo) {
          var key = _this.rawWeekly ? "value" + repo : "valueRolling" + repo;
          buildTooltip(key);
        });
      } else {}

      buildMetric();

      if (this.showDetail) {
        var today = new Date();
        var startyear = this.timeperiod && this.timeperiod != 'all' ? function () {
          var d = new Date();
          switch (_this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate() - 30));
              return d.getFullYear();
            case "year":
              d = new Date(d.setDate(d.getDate() - 365));
              return d.getFullYear();
          }
        }() : this.earliest.getFullYear();
        var startmonth = this.timeperiod && this.timeperiod != 'all' ? function () {
          var d = new Date();
          switch (_this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate() - 30));
              return d.getMonth();
            case "year":
              d = new Date(d.setDate(d.getDate() - 365));
              return d.getMonth();
          }
        }() : this.earliest.getMonth();
        var startdate = this.timeperiod && this.timeperiod != 'all' ? function () {
          var d = new Date();
          switch (_this.timeperiod) {
            case "month":
              d = new Date(d.setDate(d.getDate() - 30));
              return d.getDate();
            case "year":
              d = new Date(d.setDate(d.getDate() - 365));
              return d.getDate();
          }
        }() : this.earliest.getDate();

        config.vconcat[1].encoding.x["scale"] = {
          "domain": [{ "year": startyear, "month": startmonth, "date": startdate }, { "year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate() }]
        };
      } else {
        for (var i = 0; i < config.vconcat[0].layer.length; i++) {
          config.vconcat[0].layer[i].encoding.x["scale"] = {
            "domain": [{ "year": this.earliest.getFullYear(), "month": this.earliest.getMonth(), "date": this.earliest.getDate() }, { "year": this.latest.getFullYear(), "month": this.latest.getMonth(), "date": this.latest.getDate() }]
          };
        }
      }

      if (!this.status.base && !this.comparedTo || !this.status.compared && !this.status.base) {
        if (!this.showDetail) {
          window.$(this.$refs.holder).find('.hidefirst').removeClass('invisDet');
          window.$(this.$refs.holder).find('.hidefirst').addClass('invis');
        } else {
          window.$(this.$refs.holder).find('.hidefirst').removeClass('invis');
          window.$(this.$refs.holder).find('.hidefirst').addClass('invisDet');
        }
      }

      var endpoints = [];
      var fields = {};
      this.source.split(',').forEach(function (endpointAndFields) {
        var split = endpointAndFields.split(':');
        endpoints.push(split[0]);
        if (split[1]) {
          fields[split[0]] = split[1].split('+');
        }
      });

      var compare = this.compare;
      var processData = function processData(data) {
        _this.__download_data = data;
        _this.__download_file = _this.title.replace(/ /g, '-').replace('/', 'by').toLowerCase();
        _this.$refs.downloadJSON.href = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(_this.__download_data));
        _this.$refs.downloadJSON.setAttribute('download', _this.__download_file + '.json');

        var defaultProcess = function defaultProcess(obj, key, field, count) {
          var d = null;
          if (typeof field == "string") field = [field];

          d = _AugurStats2.default.convertKey(obj[key], field);

          d = _AugurStats2.default.convertDates(d, _this.earliest, _this.latest, 'date');

          return d;
        };

        var normalized = [];
        var aggregates = [];
        var buildLines = function buildLines(obj, onCreateData, repo) {
          if (!obj) {
            return;
          }
          if (!onCreateData) {
            onCreateData = function onCreateData(obj, key, field, count) {
              normalized.push(d);
            };
          }
          var count = 0;
          for (var key in obj) {

            if (obj.hasOwnProperty(key)) {
              if (fields[key]) {
                fields[key].forEach(function (field) {
                  onCreateData(obj, key, field, count);
                  count++;
                });
              } else {
                if (Array.isArray(obj[key]) && obj[key].length > 0) {
                  var field = Object.keys(obj[key][0]).splice(1);
                  onCreateData(obj, key, field, count);
                  count++;
                } else {
                  _this.status[repo] = false;
                  _this.renderError();
                }
              }
            }
          }
        };
        var legend = [];
        var values = [];
        var colors = [];
        var baselineVals = null;
        var baseDate = null;
        repos.forEach(function (repo) {
          buildLines(data[repo], function (obj, key, field, count) {
            var d = defaultProcess(obj, key, field, count);

            var rolling = null;
            if (repo == _this.repo) baseDate = d[0].date;else d = _AugurStats2.default.alignDates(d, baseDate, _this.period);
            if (_this.compare == 'zscore') {
              rolling = _AugurStats2.default.rollingAverage(_AugurStats2.default.zscores(d, 'value'), 'value', _this.period, repo);
            } else if (_this.compare == 'baseline') {
                if (repo.githubURL == _this.repo) {
                  baselineVals = _AugurStats2.default.rollingAverage(d, 'value', _this.period, repo);
                }
                rolling = _AugurStats2.default.rollingAverage(d, 'value', _this.period, repo);
                if (baselineVals) {

                  for (var i = 0; i < baselineVals.length; i++) {
                    if (rolling[i] && baselineVals[i]) rolling[i].valueRolling -= baselineVals[i].valueRolling;
                  }
                }
              } else {
                rolling = _AugurStats2.default.rollingAverage(d, 'value', _this.period, repo);
              }

            normalized.push(_AugurStats2.default.standardDeviationLines(rolling, 'valueRolling', repo));
            aggregates.push(_AugurStats2.default.convertKey(d, 'value', 'value' + repo));
            legend.push(repo + " " + field);
            colors.push(window.AUGUR_CHART_STYLE.brightColors[count]);
          }, repo);
        });

        if (normalized.length == 0) {} else {
          values = [];
          for (var i = 0; i < legend.length; i++) {
            normalized[i].forEach(function (d) {
              d.name = legend[i];
              d.color = colors[i];
              values.push(d);
            });
            if (_this.rawWeekly) {
              aggregates[i].forEach(function (d) {
                d.name = legend[i];
                d.color = colors[i];
                values.push(d);
              });
            }
          }
          repos.forEach(function (repo) {
            if (!_this.status[repo]) {
              var _temp = JSON.parse(JSON.stringify(values));
              _temp = _temp.map(function (datum) {
                datum.name = repo + ": data n/a";


                return datum;
              });
              values.push.apply(values, _temp);
            }
          });

          _this.legendLabels = legend;
          _this.values = values;

          var allFalse = true;
          for (var key in _this.status) {
            if (_this.status[key]) allFalse = false;
          }if (!allFalse) $(_this.$el).find('.error').addClass('hidden');

          $(_this.$el).find('.hidefirst').removeClass('invis');
          $(_this.$el).find('.hidefirst').removeClass('invisDet');
          $(_this.$el).find('.spinner').removeClass('loader');
          $(_this.$el).find('.spacing').addClass('hidden');
          $(_this.$el).find('.hidefirst').removeClass('invisDet');

          _this.renderChart();
        }
      };

      if (this.data) {
        processData(this.data);
      } else {

        window.AugurAPI.batchMapped(repos, endpoints).then(function (data) {
          processData(data);
        }, function () {});
      }

      return config;
    }
  },
  methods: {
    thisShouldTriggerRecompute: function thisShouldTriggerRecompute() {
      this.forceRecomputeCounter++;
    },
    downloadSVG: function downloadSVG(e) {
      var svgsaver = new window.SvgSaver();
      var svg = window.$(this.$refs.holder).find('svg')[0];
      svgsaver.asSvg(svg, this.__download_file + '.svg');
    },
    downloadPNG: function downloadPNG(e) {
      var svgsaver = new window.SvgSaver();
      var svg = window.$(this.$refs.holder).find('svg')[0];
      svgsaver.asPng(svg, this.__download_file + '.png');
    },
    renderChart: function renderChart() {
      this.$refs.chart.className = 'linechart intro';
      window.$(this.$refs.holder).find('.hideme').removeClass('invis');
      window.$(this.$refs.holder).find('.showme').removeClass('invis');
      window.$(this.$refs.holder).find('.hideme').removeClass('invisDet');
      window.$(this.$refs.holder).find('.showme').removeClass('invisDet');
      window.$(this.$refs.holder).find('.deleteme').remove();
      this.$refs.chartholder.innerHTML = '';
      this.$refs.chartholder.appendChild(this.mgConfig.target);
    },
    renderError: function renderError() {
      $(this.$el).find('.spinner').removeClass('loader');
      $(this.$el).find('.error').removeClass('hidden');
    }
  }, created: function created() {
    var _this2 = this;

    var query_string = "chart_mapping=" + this.source;
    window.AugurAPI.getMetricsStatus(query_string).then(function (data) {
      _this2.metricSource = data[0].data_source;
    });
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"spacing"}),_vm._v(" "),_c('div',{staticClass:"error hidden"},[_c('br'),_vm._v("Data is missing or unavailable for metric: "),_c('p',{staticStyle:{"color":"black !important"}},[_vm._v(_vm._s(_vm.title))])]),_vm._v(" "),_c('div',{staticClass:"spinner loader"}),_vm._v(" "),_c('div',{staticClass:"hidefirst linechart",class:{ invis: !_vm.detail, invisDet: _vm.detail }},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1),_vm._v(" "),_c('div',{staticClass:"row below-chart"},[_c('div',{staticClass:"col col-1"}),_vm._v(" "),_c('div',{staticClass:"col col-3",staticStyle:{"padding-left":"10px","position":"relative","top":"-8px !important"}},[_c('span',{staticStyle:{"font-size":"12px"}},[_vm._v("Data source: "+_vm._s(_vm.metricSource))])]),_vm._v(" "),_c('div',{staticClass:"col col-2",staticStyle:{"width":"154px !important","height":"38px !important","position":"relative","top":"-12px !important"}},[_c('cite',{staticClass:"metric"},[_c('a',{staticStyle:{"width":"100px !important","height":"38px !important","position":"absolute"},attrs:{"href":_vm.citeUrl,"target":"_blank"}},[_c('img',{staticStyle:{"width":"100px","position":"relative"},attrs:{"src":"https://i.ibb.co/VmxHk3q/Chaoss-Definition-Logo.png","alt":"Chaoss-Definition-Logo","border":"0"}})])])]),_vm._v(" "),_c('div',{staticClass:"col col-4",staticStyle:{"position":"relative","top":"-8px !important"}},[_c('button',{staticClass:"button download graph-download",on:{"click":_vm.downloadSVG}},[_vm._v("⬇ SVG")]),_c('button',{staticClass:"button graph-download download",on:{"click":_vm.downloadPNG}},[_vm._v("⬇ PNG")]),_c('a',{ref:"downloadJSON",staticClass:"button graph-download download",attrs:{"role":"button"}},[_vm._v("⬇ JSON")])])])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-869af3b0", __vue__options__)
  } else {
    hotAPI.reload("data-v-869af3b0", __vue__options__)
  }
})()}
});

;require.register("components/charts/EmptyChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _AugurStats = require('../../AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

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

;require.register("components/charts/GroupedBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'field'],
  data: function data() {
    return {
      values: []
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    gitRepo: function gitRepo() {
      return this.$store.state.gitRepo;
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
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    },
    rawWeekly: function rawWeekly() {
      return this.$store.state.rawWeekly;
    },
    showArea: function showArea() {
      return this.$store.state.showArea;
    },
    showTooltip: function showTooltip() {
      return this.$store.state.showTooltip;
    },
    showDetail: function showDetail() {
      return this.$store.state.showDetail;
    },
    spec: function spec() {
      var _this = this;

      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
        "padding": { 'left': 25, 'top': 15, 'right': 80, 'bottom': 50 },
        "config": {
          "bar": {
            "discreteBandSize": 10
          },
          "zero": false,
          "scale": {
            "nice": false

          },
          "axis": {
            "tickRound": false
          },
          "title": {
            "fontSize": 1
          }

        },
        "title": {
          "text": this.title,

          "offset": 10

        },
        "width": 420,
        "height": 250,
        "layer": [{
          "transform": [{
            "calculate": "datum.index + 0.125", "as": "loc_location"
          }],
          "mark": {
            "type": "bar",
            "clip": true
          },
          "encoding": {
            "y": {
              "field": "net", "type": "quantitative",
              "axis": { "title": "net loc", "grid": false },
              "scale": {
                "nice": false
              }
            },
            "y2": {
              "field": "avg_loc", "type": "quantitative", "axis": { "title": "", "grid": false },
              "scale": {
                "nice": false
              }
            },
            "x": {
              "field": "loc_location", "type": 'quantitative',

              "axis": { "title": "", "labels": false }
            },
            "color": {
              "value": "#FF3647"
            }
          }
        }, {
          "transform": [{
            "calculate": "datum.index - 0.125", "as": "commit_location"
          }],
          "mark": {
            "type": "bar",
            "clip": true
          },
          "encoding": {
            "y": {
              "field": "avg_commits",
              "axis": { "title": "commits", "grid": false },
              "scale": {
                "nice": false
              }
            },
            "y2": {
              "field": "patches", "type": "quantitative",
              "axis": { "title": "commits", "grid": false },
              "scale": {
                "nice": false
              }
            },
            "x": {
              "field": "commit_location", "type": 'quantitative',
              "axis": { "title": "", "labels": false }
            },
            "color": {
              "value": "#4736FF",

              "legend": null
            }
          }
        }, {
          "transform": [{
            "calculate": "datum.index", "as": "text_location"
          }, {
            "calculate": "-10", "as": "y"
          }],
          "mark": {
            "type": "text",
            "angle": 330
          },
          "encoding": {
            "text": {
              "field": "name", "type": "nominal"
            },
            "y": {
              "value": 280,

              "axis": {
                "title": "",
                "grid": false
              },
              "scale": {
                "nice": false
              }

            },
            "x": {
              "field": "text_location", "type": 'quantitative',
              "axis": { "title": "", "labels": false }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "rule"
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "patches",
              "axis": {
                "title": "", "grid": false
              },
              "scale": {
                "nice": false
              }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "rule"
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "net",
              "axis": null,
              "scale": {
                "nice": false
              }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "bar",
            "clip": false
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "net_lines_minus_whitespace",
              "axis": null,
              "scale": {
                "nice": false
              }

            },
            "opacity": { "value": 0 },
            "color": {
              "field": "key",
              "type": "ordinal",
              "scale": { "range": ["#4736FF", "#FF3647"] },
              "legend": { "offset": -16 }
            }

          }
        }],
        "resolve": { "scale": { "y": "independent", "color": "independent" } }
      };

      var repos = [];
      if (this.gitRepo) {
        repos.push(window.AugurAPI.Repo({ gitURL: this.gitRepo }));
      }
      var endpoints = [];
      var fields = {};
      this.source.split(',').forEach(function (endpointAndFields) {
        var split = endpointAndFields.split(':');
        endpoints.push(split[0]);
        if (split[1]) {
          fields[split[0]] = split[1].split('+');
        }
      });
      if (this.data) {
        processGitData(this.data);
      } else {
        var repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
        repo[this.source]().then(function (data) {
          console.log("batch data", data);
          processData(data);
        }, function () {});
      }
      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');
      var processGitData = function processGitData(data) {
        var repo = window.AugurAPI.Repo({ gitURL: _this.repo });
        var dat = [];
        repo.changesByAuthor().then(function (changes) {
          dat.push(changes);
        });
      };
      var defaultProcess = function defaultProcess(obj, key) {
        var d = null;
        if (typeof field == "string") field = [field];
        d = _AugurStats2.default.convertKey(obj[key], key);
        return d;
      };
      var processData = function processData(data) {
        console.log(repos, data, "CHECK");
        var sort = _this.field == 'commit' ? "patches" : "net";
        data.sort(function (a, b) {
          return b[sort] - a[sort];
        });
        var sum_commit = 0;
        var sum_loc = 0;
        var max_loc = 0;
        var max_commit = 0;
        var min_loc = 0;
        var min_commit = 0;
        for (var i = 0; i < data.length; i++) {
          sum_commit += data[i]['patches'];
          sum_loc += data[i]['net'];
          data[i]['index'] = i;
          if (data[i]['net'] > max_loc) max_loc = data[i]['net'];
          if (data[i]['patches'] > max_commit) max_commit = data[i]['patches'];
          if (data[i]['net'] < min_loc) min_loc = data[i]['net'];
          if (data[i]['patches'] < min_commit) min_commit = data[i]['patches'];
          if (i == 0) data[i].key = "commits";else data[i].key = "net lines changed";
        }

        data.forEach(function (el) {
          el.avg_commits = sum_commit / data.length;
          el.avg_loc = sum_loc / data.length;
        });

        var dif_loc = Math.abs(max_loc - sum_loc / data.length) > Math.abs(min_loc - sum_loc / data.length) ? Math.abs(max_loc - sum_loc / data.length) : Math.abs(min_loc - sum_loc / data.length);
        var dif_commit = Math.abs(max_commit - sum_commit / data.length) > Math.abs(min_commit - sum_commit / data.length) ? Math.abs(max_commit - sum_commit / data.length) : Math.abs(min_commit - sum_commit / data.length);
        config.layer[0].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[0].encoding.y2.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[1].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[1].encoding.y2.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[2].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[3].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[4].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];

        repos.forEach(function (repo) {
          _this.values = data;
        });
      };
      return config;
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"groupedbarchart"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")]),_vm._v(" "),_vm._m(0)],1)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticStyle:{"padding":"0 50px 0 50px","font-size":"12px"}},[_c('p',[_vm._v("*The black \"baseline\" represents the averages of both LoC and commits across all repositories within the selected repository's overlying Facade organization during the calendar year shown. Wherever this bar stretches to shows how far above or below the raw value of the statistic is from the regular average.")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-45bc243c", __vue__options__)
  } else {
    hotAPI.reload("data-v-45bc243c", __vue__options__)
  }
})()}
});

;require.register("components/charts/HorizontalBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'type'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
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
    };
  },
  created: function created() {
    this.type = 1;
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    spec: function spec() {
      var _this = this;

      var field = null;

      if (this.type == 0) {
        field = "netratio";
      } else if (this.type == 1) {
        field = "totalratio";
      } else if (this.type == 2) {
        field = "addedratio";
      }

      var colors = ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"];
      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 700,
        "height": 310,
        "config": {
          "tick": {
            "thickness": 8,
            "bandSize": 23
          },
          "axis": {
            "grid": false
          }
        },
        "title": {
          "text": this.title,
          "offset": 15

        },
        "layer": [{
          "transform": [{
            "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
            "as": "Majority type of changes"
          }, {
            "calculate": "(datum.additions - datum.deletions)",
            "as": "Net lines added"
          }, {
            "calculate": "((datum.additions - datum.deletions) / datum.commits)",
            "as": "netratio"
          }, {
            "calculate": "(datum.additions / datum.commits)",
            "as": "addedratio"
          }, {
            "calculate": "(datum.lines / datum.commits)",
            "as": "totalratio"
          }],
          "mark": {
            "type": "bar",
            "tooltip": { "content": "data" }
          },
          "encoding": {
            "x": { "field": field, "type": "quantitative" },
            "y": {
              "field": "author_email",
              "sort": {
                "field": field,
                "op": "mean",
                "order": "descending"
              },
              "type": "nominal",
              "axis": { "title": null }
            },
            "color": {
              "field": "author_email",
              "type": "nominal",
              "scale": { "scheme": "category10" },
              "legend": null
            }
          }

        }]

      };

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      var authors = [];
      var track = {};
      repo.changesByAuthor().then(function (changes) {
        changes.forEach(function (change) {
          track[change.author_email] = track[change.author_email] ? track[change.author_email] : { 'commits': 0, 'lines': 0, 'additions': 0, 'deletions': 0 };
          track[change.author_email]['commits'] = track[change.author_email]['commits'] ? track[change.author_email]['commits'] + 1 : 1;

          track[change.author_email]['lines'] = track[change.author_email]['lines'] ? track[change.author_email]['lines'] + change.additions + change.deletions : change.additions + change.deletions;
          track[change.author_email]['additions'] = track[change.author_email]['additions'] ? track[change.author_email]['additions'] + change.additions : change.additions;
          track[change.author_email]['deletions'] = track[change.author_email]['deletions'] ? track[change.author_email]['deletions'] + change.deletions : change.deletions;
        });

        changes.forEach(function (change) {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates);
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates);
            }
          }
          if (!authors.includes(change["author_email"])) {
            authors.push(change["author_email"]);
            change["flag"] = (track[change.author_email] / track["total"] * 100).toFixed(4);
          }
        });

        _this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
        var careabout = [];
        _this.contributors.slice(0, 10).forEach(function (obj) {
          careabout.push(obj["author_email"]);
        });

        var findObjectByKey = function findObjectByKey(array, key, value) {
          var ary = [];
          for (var i = 0; i < array.length; i++) {
            if (array[i][key] == value) {
              ary.push(array[i]);
            }
          }
          return ary;
        };

        var ary = [];

        for (var key in track) {
          if (careabout.includes(key)) ary.push({ "author_email": key, "commits": track[key]['commits'], "lines": track[key]['lines'], "additions": track[key]['additions'], "deletions": track[key]['deletions'] });
        }

        _this.values = ary;
        console.log("TRACK", ary, careabout);
      });

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      var processData = function processData(data) {};

      return config;
    }
  }

};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"normalbar"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes tickradios",staticStyle:{"position":"relative","top":"-60px !important"}},[_c('div',{staticClass:"inputGroup "},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.type),expression:"type"}],attrs:{"id":"totalradio","name":"lines","value":"1","type":"radio","checked":""},domProps:{"checked":_vm._q(_vm.type,"1")},on:{"change":function($event){_vm.type="1"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"totalradio"}},[_vm._v("Total")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup "},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.type),expression:"type"}],attrs:{"id":"netradio","name":"lines","value":"0","type":"radio"},domProps:{"checked":_vm._q(_vm.type,"0")},on:{"change":function($event){_vm.type="0"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"netradio"}},[_vm._v("Net")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup "},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.type),expression:"type"}],attrs:{"id":"addedradio","name":"lines","value":"2","type":"radio"},domProps:{"checked":_vm._q(_vm.type,"2")},on:{"change":function($event){_vm.type="2"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"addedradio"}},[_vm._v("Added")])])])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-8d346828", __vue__options__)
  } else {
    hotAPI.reload("data-v-8d346828", __vue__options__)
  }
})()}
});

;require.register("components/charts/LinesOfCodeChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    return {
      contributors: [],
      organizations: [],
      view: 'year',
      monthNames: monthNames,
      monthDecimals: monthDecimals,
      years: years,
      setYear: 0
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    chart: function chart() {
      var _this = this;

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      repo.changesByAuthor().then(function (changes) {
        changes.forEach(function (change) {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates);
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates);
            }
          }
        });

        _this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
        _this.organizations = flattenAndSort(organizations, 'name', 'additions');
      });
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('h3',[_vm._v("Lines of code added by the top 10 authors")]),_vm._v(" "),_c('table',{staticClass:"lines-of-code-table"},[_c('thead',[_c('tr',[_c('th',[_vm._v("Author")]),_vm._v(" "),_vm._l((_vm.years),function(year){return (!_vm.setYear)?_c('th',{staticClass:"clickable-header",on:{"click":function($event){_vm.setYear = year}}},[_vm._v(_vm._s(year))]):_vm._e()}),_vm._v(" "),_vm._l((_vm.monthNames),function(month){return (_vm.setYear)?_c('th',[_vm._v(_vm._s(month))]):_vm._e()}),_vm._v(" "),(!_vm.setYear)?_c('th',[_vm._v("Total all time")]):_vm._e(),_vm._v(" "),(_vm.setYear)?_c('th',{on:{"click":function($event){_vm.setYear = 0}}},[_vm._v(_vm._s(_vm.setYear))]):_vm._e()],2)]),_vm._v(" "),_c('tbody',_vm._l((_vm.contributors.slice(0, 10)),function(contributor){return _c('tr',[_c('td',[_vm._v(_vm._s(contributor.author_email))]),_vm._v(" "),_vm._l((_vm.years),function(year){return (!_vm.setYear)?_c('td',[_vm._v(_vm._s((contributor[year]) ? contributor[year].additions || 0 : 0))]):_vm._e()}),_vm._v(" "),_vm._l((_vm.monthDecimals),function(month){return (_vm.setYear)?_c('td',[_vm._v(_vm._s((contributor[_vm.setYear + '-' + month]) ? contributor[_vm.setYear + '-' + month].additions || 0 : 0))]):_vm._e()}),_vm._v(" "),(!_vm.setYear)?_c('td',[_vm._v(_vm._s(contributor.additions))]):_vm._e(),_vm._v(" "),(_vm.setYear)?_c('td',[_vm._v(_vm._s((contributor[_vm.setYear]) ? contributor[_vm.setYear].additions || 0 : 0))]):_vm._e()],2)}))]),_vm._v(" "),_c('br'),_vm._v(" "),_c('h3',[_vm._v("Lines of code added by the top 5 organizations")]),_vm._v(" "),_c('table',{staticClass:"lines-of-code-table"},[_c('thead',[_c('tr',[_c('th',[_vm._v("Author")]),_vm._v(" "),_vm._l((_vm.years),function(year){return (!_vm.setYear)?_c('th',{staticClass:"clickable-header",on:{"click":function($event){_vm.setYear = year}}},[_vm._v(_vm._s(year))]):_vm._e()}),_vm._v(" "),_vm._l((_vm.monthNames),function(month){return (_vm.setYear)?_c('th',[_vm._v(_vm._s(month))]):_vm._e()}),_vm._v(" "),(!_vm.setYear)?_c('th',[_vm._v("Total all time")]):_vm._e(),_vm._v(" "),(_vm.setYear)?_c('th',{staticClass:"clickable-header",on:{"click":function($event){_vm.setYear = _vm.year}}},[_vm._v(_vm._s(_vm.setYear))]):_vm._e()],2)]),_vm._v(" "),_c('tbody',_vm._l((_vm.organizations.slice(0, 10)),function(organization){return _c('tr',[_c('td',[_vm._v(_vm._s(organization.name))]),_vm._v(" "),_vm._l((_vm.years),function(year){return (!_vm.setYear)?_c('td',[_vm._v(_vm._s((organization[year]) ? organization[year].additions || 0 : 0))]):_vm._e()}),_vm._v(" "),_vm._l((_vm.monthDecimals),function(month){return (_vm.setYear)?_c('td',[_vm._v(_vm._s((organization[_vm.setYear + '-' + month]) ? organization[_vm.setYear + '-' + month].additions || 0 : 0))]):_vm._e()}),_vm._v(" "),(!_vm.setYear)?_c('td',[_vm._v(_vm._s(organization.additions))]):_vm._e(),_vm._v(" "),(_vm.setYear)?_c('td',[_vm._v(_vm._s((organization[_vm.setYear]) ? organization[_vm.setYear].additions || 0 : 0))]):_vm._e()],2)}))]),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-2b1e04b8", __vue__options__)
  } else {
    hotAPI.reload("data-v-2b1e04b8", __vue__options__)
  }
})()}
});

;require.register("components/charts/NormalizedStackedBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    return {
      values: [],
      contributors: [],
      organizations: [],
      view: 'year',
      monthNames: monthNames,
      monthDecimals: monthDecimals,
      years: years,
      setYear: 0,
      group: 1
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    spec: function spec() {
      var _this = this;

      var type = null,
          bin = null,
          size = null,
          timeUnit = null,
          format = null;

      if (this.group == 0) {
        timeUnit = 'year';
        format = '%Y';
        type = "bar";
        bin = false;
        size = 30;
      }
      if (this.group == 1) {
        timeUnit = 'yearmonth';
        format = '%y %b';
        type = "bar";
        bin = false;
        size = 13;
      }
      if (this.group == 2) {
        timeUnit = 'yearmonth';
        format = '%y %b';
        type = "bar";
        bin = false;
        size = 13;
        type = "area";
      }

      var colors = ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"];
      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 800,
        "height": 380,
        "title": {
          "text": this.title,
          "offset": 15
        },
        "config": {
          "axis": {
            "grid": false
          },
          "legend": {
            "offset": -20,
            "orient": "right",
            "titlePadding": 10,
            "padding": 40,
            "labelFontSize": 14,
            "titleFontSize": 14,
            "labelLimit": 260
          },
          "scale": { "minSize": 100, "maxSize": 500 },
          "bar": {
            "continuousBandSize": size,
            "binSpacing": 0
          }
        },
        "layer": [{
          "transform": [{
            "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
            "as": "Majority type of changes"
          }, {
            "calculate": "(datum.additions - datum.deletions)",
            "as": "Net lines added"
          }, {
            "calculate": "(datum.additions + datum.deletions)",
            "as": "Total lines changed"
          }, {
            "calculate": "(datum.count * 100)",
            "as": "percent"
          }],
          "mark": {
            "type": type,
            "tooltip": { "content": "data" },

            "cornerRadius": 45
          },
          "encoding": {
            "x": {
              "field": "author_date",
              "type": "temporal",

              "timeUnit": timeUnit,

              "axis": { "domain": false, "format": format }
            },
            "y": {
              "field": "count",
              "type": "quantitative",

              "aggregate": "sum",
              "stack": "center",
              "axis": null
            },
            "color": {
              "field": "author_email",
              "type": "nominal",
              "scale": { "scheme": "category10" }
            }
          }

        }]

      };

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      var authors = [];
      var track = { "total": 0 };
      repo.changesByAuthor().then(function (changes) {
        changes.forEach(function (change) {
          change.author_date = new Date(change.author_date);
          change["count"] = change["count"] ? change["count"] + 1 : 1;
          track[change.author_email] = track[change.author_email] ? track[change.author_email] + 1 : 1;
          track["total"] += 1;
        });

        changes.forEach(function (change) {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates);
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates);
            }
          }
          if (!authors.includes(change["author_email"])) {
            authors.push(change["author_email"]);
            change["flag"] = (track[change.author_email] / track["total"]).toFixed(4);
          }
        });

        _this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
        var careabout = [];
        _this.contributors.slice(0, 10).forEach(function (obj) {
          careabout.push(obj["author_email"]);
        });

        var findObjectByKey = function findObjectByKey(array, key, value) {
          var ary = [];
          for (var i = 0; i < array.length; i++) {
            if (array[i][key] == value) {
              ary.push(array[i]);
            }
          }
          return ary;
        };

        var ary = [];

        careabout.forEach(function (name) {
          findObjectByKey(changes, "author_email", name).forEach(function (obj) {
            ary.push(obj);
          });
        });

        _this.values = ary;
      });

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      var processData = function processData(data) {};

      return config;
    }
  }

};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"tickchart ",staticStyle:{"margin-bottom":"0 !important"}},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes tickradios",staticStyle:{"position":"relative","top":"-80px !important"}},[_c('div',{staticClass:"inputGroup ",staticStyle:{"padding-top":"5px"}},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.group),expression:"group"}],attrs:{"id":"yearradio","name":"timeframe","value":"0","type":"radio"},domProps:{"checked":_vm._q(_vm.group,"0")},on:{"change":function($event){_vm.group="0"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"yearradio"}},[_vm._v("Year")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup ",staticStyle:{"padding-top":"5px"}},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.group),expression:"group"}],attrs:{"id":"monthradio","name":"timeframe","value":"1","type":"radio"},domProps:{"checked":_vm._q(_vm.group,"1")},on:{"change":function($event){_vm.group="1"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"monthradio"}},[_vm._v("Month")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup ",staticStyle:{"padding-top":"5px"}},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.group),expression:"group"}],attrs:{"id":"contradio","name":"timeframe","value":"2","type":"radio"},domProps:{"checked":_vm._q(_vm.group,"2")},on:{"change":function($event){_vm.group="2"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"contradio"}},[_vm._v("Continuous")])])])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-0760224e", __vue__options__)
  } else {
    hotAPI.reload("data-v-0760224e", __vue__options__)
  }
})()}
});

;require.register("components/charts/OneDimensionalStackedBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'type'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
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
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    spec: function spec() {
      var _this = this;

      var type = null,
          bin = null,
          size = null;

      if (this.tick == 0) {
        type = "circle";
        bin = false;
        size = {
          "field": "Net lines added",
          "type": "quantitative",
          "min": "15",
          "scale": { "minSize": 30, "maxSize": 31 }
        };
      }
      if (this.tick == 1) {
        type = "tick";
        bin = false;
        size = {};
      }
      if (this.tick == 2) {
        type = "rect";
        bin = { "maxbins": 40 };
        size = {};
      }

      var colors = ["#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"];
      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 780,

        "config": {
          "tick": {
            "thickness": 8,
            "bandSize": 23
          },
          "axis": {
            "grid": false
          }

        },
        "title": {
          "text": this.title,
          "offset": 40
        },
        "layer": [{
          "transform": [{
            "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
            "as": "Majority type of changes"
          }, {
            "calculate": "(datum.additions - datum.deletions)",
            "as": "Net lines added"
          }, {
            "calculate": "(datum.additions + datum.deletions)",
            "as": "Total lines changed"
          }, {
            "calculate": "(datum.flag * 100)",
            "as": "percent"
          }],
          "mark": {
            "type": "bar",
            "tooltip": { "content": "data" }
          },
          "encoding": {
            "x": { "field": "count", "type": "quantitative", "sort": { "op": "sum", "order": "descending" }, "stack": "normalize", "axis": { "labels": false, "title": null } },
            "color": {
              "field": "author_email",
              "type": "nominal",
              "scale": { "scheme": "category10" },
              "legend": null
            }
          }

        }]

      };

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      var authors = [];
      var track = { "total": 0 };
      repo.changesByAuthor().then(function (changes) {
        changes.forEach(function (change) {
          change.author_date = new Date(change.author_date);
          if (_this.type == "commit") {
            change["count"] = change["count"] ? change["count"] + 1 : 1;
            track[change.author_email] = track[change.author_email] ? track[change.author_email] + 1 : 1;
            track["total"] += 1;
          } else if (_this.type == "lines") {
            change["count"] = change["count"] ? change["count"] + change.additions : change.additions;
            track[change.author_email] = track[change.author_email] ? track[change.author_email] + change.additions : change.additions;
            track["total"] += change.additions;
          }
        });

        changes.forEach(function (change) {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates);
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates);
            }
          }
          if (!authors.includes(change["author_email"])) {
            authors.push(change["author_email"]);
            change["flag"] = (track[change.author_email] / track["total"] * 100).toFixed(4);
          }
        });

        _this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
        var careabout = [];
        _this.contributors.slice(0, 10).forEach(function (obj) {
          careabout.push(obj["author_email"]);
        });

        var findObjectByKey = function findObjectByKey(array, key, value) {
          var ary = [];
          for (var i = 0; i < array.length; i++) {
            if (array[i][key] == value) {
              ary.push(array[i]);
            }
          }
          return ary;
        };

        var ary = [];

        careabout.forEach(function (name) {
          findObjectByKey(changes, "author_email", name).forEach(function (obj) {
            ary.push(obj);
          });
        });

        _this.values = ary;
      });

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      var processData = function processData(data) {};

      return config;
    }
  }

};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"normalbar"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-5685f17a", __vue__options__)
  } else {
    hotAPI.reload("data-v-5685f17a", __vue__options__)
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

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
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
      var _this = this;

      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "data": { "values": [] },
        "title": this.title,
        "width": this.$el ? this.$el.offestWidth : 800,
        "height": 400,
        "autosize": "fit",
        "mark": "bar",
        "encoding": {
          "y": { "aggregate": "sum",
            "field": "value",
            "type": "quantitative" },
          "x": { "field": "date",
            "type": "temporal" },
          "color": { "field": "field",
            "type": "nominal" }
        }
      };

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var endpoints = [];
      var fields = {};
      this.source.split(',').forEach(function (endpointAndFields) {
        var split = endpointAndFields.split(':');
        endpoints.push(split[0]);
        if (split[1]) {
          fields[split[0]] = split[1].split('+');
        }
      });

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      var processData = function processData(data) {
        var defaultProcess = function defaultProcess(obj, key, field, count) {
          var d = _AugurStats2.default.convertKey(obj[key], field);
          return _AugurStats2.default.convertDates(d, _this.earliest, _this.latest);
        };

        var normalized = [];
        var buildLines = function buildLines(obj, onCreateData) {
          if (!obj) {
            return;
          }
          if (!onCreateData) {
            onCreateData = function onCreateData(obj, key, field, count) {
              var d = defaultProcess(obj, key, field, count);
              normalized.push(d);
            };
          }
          var count = 0;
          for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
              if (fields[key]) {
                fields[key].forEach(function (field) {
                  onCreateData(obj, key, field, count);
                  count++;
                });
              } else {
                if (Array.isArray(obj[key]) && obj[key].length > 0) {
                  var field = Object.keys(obj[key][0]).splice(1);
                  onCreateData(obj, key, field, count);
                  count++;
                } else {
                  _this.renderError();
                  return;
                }
              }
            }
          }
        };

        var values = [];

        buildLines(data[_this.repo], function (obj, key, field, count) {
          normalized.push(defaultProcess(obj, key, field, count));
        });

        if (normalized.length == 0) {
          _this.renderError();
        } else {
          for (var i = 0; i < normalized.length; i++) {
            normalized[i].forEach(function (d) {
              values.push(d);
            });
          }
        }

        $(_this.$el).find('.showme, .hidefirst').removeClass('invis');
        $(_this.$el).find('.stackedbarchart').removeClass('loader');
        _this.values = values;
      };

      if (this.data) {
        processData(this.data);
      } else {
        window.AugurAPI.batchMapped(repos, endpoints).then(function (data) {
          processData(data);
        });
      }

      return config;
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

;require.register("components/charts/TickChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data'],
  data: function data() {
    var years = [];
    for (var i = 9; i >= 0; i--) {
      years.push(new Date().getFullYear() - i);
    }
    var monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
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
    };
  },
  created: function created() {
    this.tick = 0;
  },

  computed: {
    repo: function repo() {
      return this.$store.state.gitRepo;
    },
    earliest: function earliest() {
      return this.$store.state.startDate;
    },
    latest: function latest() {
      return this.$store.state.endDate;
    },
    spec: function spec() {
      var _this = this;

      var type = null,
          bin = null,
          size = null,
          opacity = null;

      if (this.tick == 0) {
        type = "circle";
        bin = false;
        size = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": "15",
          "scale": { "minSize": 30, "maxSize": 31 }
        };
        opacity = {};
      }
      if (this.tick == 1) {
        type = "tick";
        bin = false;
        size = {};
        opacity = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": ".5"
        };
      }
      if (this.tick == 2) {
        type = "rect";
        bin = { "maxbins": 40 };
        size = {};
        opacity = {
          "field": "Total lines changed",
          "type": "quantitative",
          "min": ".5"
        };
      }

      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
        "width": 950,
        "height": 300,
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
            "titleFontSize": 10,
            "titlePadding": 10
          }, "scale": { "minSize": 100, "maxSize": 500 }
        },
        "layer": [{
          "transform": [{
            "calculate": "(datum.additions > datum.deletions) ? 'more deletions' : 'more additions'",
            "as": "Majority type of changes"
          }, {
            "calculate": "(datum.additions - datum.deletions)",
            "as": "Net lines added"
          }, {
            "calculate": "(datum.additions + datum.deletions) < 50000 ? 50000 : ((datum.additions + datum.deletions) > 1000000 ? 1000000 : (datum.additions + datum.deletions))",
            "as": "Total lines changed"
          }],
          "mark": type,
          "encoding": {
            "x": { "field": "author_date", "type": "temporal", "bin": bin, "axis": { "format": "%b %Y", "title": " " } },
            "y": { "field": "author_email", "type": "nominal" },
            "color": {
              "field": "Net lines added",
              "type": "quantitative",
              "scale": { "range": ["#FF0000", "#00FF00"] }
            },
            "size": size,
            "opacity": opacity

          }

        }]

      };

      var repo = window.AugurAPI.Repo({ gitURL: this.repo });
      var contributors = {};
      var organizations = {};

      var addChanges = function addChanges(dest, src) {
        if (dest && src) {
          if ((typeof dest === 'undefined' ? 'undefined' : _typeof(dest)) !== 'object') {
            dest['additions'] = 0;
            dest['deletions'] = 0;
          }
          dest['additions'] += src['additions'] || 0;
          dest['deletions'] += src['deletions'] || 0;
        }
      };

      var group = function group(obj, name, change, filter) {
        if (filter(change)) {
          var year = new Date(change.author_date).getFullYear();
          var month = new Date(change.author_date).getMonth();
          obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + '-' + month] = obj[change[name]][year + '-' + month] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + '-' + month], change);
        }
      };

      var flattenAndSort = function flattenAndSort(obj, keyName, sortField) {
        return Object.keys(obj).map(function (key) {
          var d = obj[key];
          d[keyName] = key;
          return d;
        }).sort(function (a, b) {
          return b[sortField] - a[sortField];
        });
      };

      var filterDates = function filterDates(change) {
        return new Date(change.author_date).getFullYear() > _this.years[0];
      };

      repo.changesByAuthor().then(function (changes) {
        changes.forEach(function (change) {
          change.author_date = new Date(change.author_date);
        });

        changes.forEach(function (change) {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change, filterDates);
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'affiliation', change, filterDates);
            }
          }
        });

        _this.contributors = flattenAndSort(contributors, 'author_email', 'additions');
        var careabout = [];
        _this.contributors.slice(0, 10).forEach(function (obj) {
          careabout.push(obj["author_email"]);
        });

        var findObjectByKey = function findObjectByKey(array, key, value) {
          var ary = [];
          for (var i = 0; i < array.length; i++) {
            if (array[i][key] == value) {
              ary.push(array[i]);
            }
          }
          return ary;
        };

        var ary = [];

        careabout.forEach(function (name) {
          findObjectByKey(changes, "author_email", name).forEach(function (obj) {
            ary.push(obj);
          });
        });

        _this.values = ary;
      });

      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');

      var repos = [];
      if (this.repo) {
        repos.push(window.AugurRepos[this.repo]);
      }

      var processData = function processData(data) {};

      return config;
    }
  }

};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder",staticStyle:{"position":"relative","z-index":"5"}},[_c('div',{staticClass:"tickchart"},[_c('h3',{staticStyle:{"text-align":"center"}},[_vm._v("Lines of code added by the top 10 authors visualized")]),_vm._v(" "),_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")]),_vm._v(" "),_c('div',{staticClass:"form-item form-checkboxes tickradios",staticStyle:{"transform":"translateY(-35px) !important"}},[_c('div',{staticClass:"inputGroup"},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.tick),expression:"tick"}],attrs:{"id":"circradio","name":"comparebaseline","value":"0","type":"radio"},domProps:{"checked":_vm._q(_vm.tick,"0")},on:{"change":function($event){_vm.tick="0"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"circradio"}},[_vm._v("Circle")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup "},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.tick),expression:"tick"}],attrs:{"id":"tickradio","name":"comparebaseline","value":"1","type":"radio"},domProps:{"checked":_vm._q(_vm.tick,"1")},on:{"change":function($event){_vm.tick="1"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"tickradio"}},[_vm._v("Tick")])]),_vm._v(" "),_c('div',{staticClass:"inputGroup "},[_c('input',{directives:[{name:"model",rawName:"v-model",value:(_vm.tick),expression:"tick"}],attrs:{"id":"rectradio","name":"comparebaseline","value":"2","type":"radio"},domProps:{"checked":_vm._q(_vm.tick,"2")},on:{"change":function($event){_vm.tick="2"}}}),_vm._v(" "),_c('label',{attrs:{"id":"front","for":"rectradio"}},[_vm._v("Rectangle")])])])],1)])}
__vue__options__.staticRenderFns = []
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-083303b4", __vue__options__)
  } else {
    hotAPI.reload("data-v-083303b4", __vue__options__)
  }
})()}
});

;require.register("components/charts/TimeIntervalBarChart.vue", function(exports, require, module) {
;(function(){
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vuex = require('vuex');

var _AugurStats = require('AugurStats');

var _AugurStats2 = _interopRequireDefault(_AugurStats);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

exports.default = {
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'data', 'field'],
  data: function data() {
    return {
      values: []
    };
  },

  computed: {
    repo: function repo() {
      return this.$store.state.baseRepo;
    },
    gitRepo: function gitRepo() {
      return this.$store.state.gitRepo;
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
    comparedRepos: function comparedRepos() {
      return this.$store.state.comparedRepos;
    },
    rawWeekly: function rawWeekly() {
      return this.$store.state.rawWeekly;
    },
    showArea: function showArea() {
      return this.$store.state.showArea;
    },
    showTooltip: function showTooltip() {
      return this.$store.state.showTooltip;
    },
    showDetail: function showDetail() {
      return this.$store.state.showDetail;
    },
    months: function months() {
      return { 1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
      };
    },
    spec: function spec() {
      var _this = this;

      var config = {
        "$schema": "https://vega.github.io/schema/vega-lite/v3.json",
        "padding": { 'left': 60, 'top': 10, 'right': 70, 'bottom': 20 },
        "config": {
          "bar": {
            "discreteBandSize": 24
          },
          "zero": false,
          "scale": {
            "nice": false

          },
          "axis": {
            "tickRound": false
          }

        },
        "title": {
          "text": this.title,

          "offset": 10,
          "fontSize": 3
        },
        "width": 1000,
        "height": 250,
        "layer": [{
          "transform": [{
            "calculate": "datum.month + 0.155", "as": "loc_location"
          }],
          "mark": {
            "type": "bar",
            "clip": "true"
          },
          "encoding": {
            "y": {
              "field": "net_lines_minus_whitespace", "type": "quantitative",
              "axis": { "title": "net loc", "grid": false },
              "scale": {
                "domain": [-1000000, 1000000],
                "nice": false
              }
            },
            "y2": {
              "field": "avg_loc", "type": "quantitative", "axis": { "title": "", "grid": false },
              "scale": {
                "domain": [-1000000, 1000000],
                "nice": false
              }
            },
            "x": {
              "field": "loc_location", "type": 'quantitative',

              "axis": { "title": "", "labels": false }
            },
            "color": {
              "value": "#FF3647"
            }
          }
        }, {
          "transform": [{
            "calculate": "datum.month - 0.155", "as": "commit_location"
          }],
          "mark": {
            "type": "bar",
            "clip": "true"
          },
          "encoding": {
            "y": {
              "field": "avg_commits",
              "axis": { "title": "commits", "grid": false },
              "scale": {
                "domain": [-100, 100],
                "nice": false
              }
            },
            "y2": {
              "field": "commits", "type": "quantitative",
              "axis": { "title": "commits", "grid": false },
              "scale": {
                "domain": [-100, 100],
                "nice": false
              }
            },
            "x": {
              "field": "commit_location", "type": 'quantitative',
              "axis": { "title": "", "labels": false }
            },
            "color": {
              "value": "#4736FF",

              "legend": null
            }
          }
        }, {
          "transform": [{
            "calculate": "datum.month", "as": "text_location"
          }, {
            "calculate": "-10", "as": "y"
          }],
          "mark": {
            "type": "text"
          },
          "encoding": {
            "text": {
              "field": "month_name", "type": "nominal"
            },
            "y": {
              "value": 270,

              "axis": {
                "title": "",
                "grid": false
              },
              "scale": {
                "domain": [-1000000, 1000000],
                "nice": false
              }

            },
            "x": {
              "field": "text_location", "type": 'quantitative',
              "axis": { "title": "", "labels": false }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "rule"
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "commits",
              "axis": {
                "title": "", "grid": false
              },
              "scale": {
                "domain": [-100, 100],
                "nice": false
              }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "rule"
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "net_lines_minus_whitespace",
              "axis": null,
              "scale": {
                "domain": [-1000000, 1000000],
                "nice": false
              }
            }

          }
        }, {
          "transform": [],
          "mark": {
            "type": "bar",
            "clip": "true"
          },
          "encoding": {

            "y": {
              "aggregate": "mean",
              "field": "net_lines_minus_whitespace",
              "axis": null,
              "scale": {
                "nice": false
              }

            },
            "opacity": { "value": 0 },
            "color": {
              "field": "key",
              "type": "ordinal",
              "scale": { "range": ["#4736FF", "#FF3647"] },
              "legend": { "offset": -16 }
            }

          }
        }],
        "resolve": { "scale": { "y": "independent", "color": "independent" } }
      };

      var repos = [];
      if (this.gitRepo) {
        repos.push(window.AugurAPI.Repo({ gitURL: this.gitRepo }));
      }
      var endpoints = [];
      var fields = {};
      this.source.split(',').forEach(function (endpointAndFields) {
        var split = endpointAndFields.split(':');
        endpoints.push(split[0]);
        if (split[1]) {
          fields[split[0]] = split[1].split('+');
        }
      });
      if (this.data) {
        processGitData(this.data);
      } else {
        var repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
        repo[this.source]().then(function (data) {
          console.log("batch data", data);
          processData(data);
        }, function () {});
      }
      $(this.$el).find('.showme, .hidefirst').removeClass('invis');
      $(this.$el).find('.stackedbarchart').removeClass('loader');
      var processGitData = function processGitData(data) {
        var repo = window.AugurAPI.Repo({ gitURL: _this.repo });
        var dat = [];
        repo.changesByAuthor().then(function (changes) {
          dat.push(changes);
        });
      };
      var defaultProcess = function defaultProcess(obj, key) {
        var d = null;
        if (typeof field == "string") field = [field];
        d = _AugurStats2.default.convertKey(obj[key], key);
        return d;
      };
      var processData = function processData(data) {
        console.log(repos, data, "CHECK");
        var sum_commit = 0;
        var sum_loc = 0;
        var max_loc = 0;
        var max_commit = 0;
        var min_loc = 0;
        var min_commit = 0;
        for (var i = 0; i < data.length; i++) {
          sum_commit += data[i]['commits'];
          sum_loc += data[i]['net_lines_minus_whitespace'];
          console.log(i, data[i]['commits'], data[i]['net_lines_minus_whitespace']);
          data[i]['index'] = i;
          if (data[i]['net_lines_minus_whitespace'] > max_loc) max_loc = data[i]['net_lines_minus_whitespace'];
          if (data[i]['commits'] > max_commit) max_commit = data[i]['commits'];
          if (data[i]['net_lines_minus_whitespace'] < min_loc) {
            min_loc = data[i]['net_lines_minus_whitespace'];
            console.log("min = ", data[i]['net_lines_minus_whitespace']);
          }
          if (data[i]['commits'] < min_commit) min_commit = data[i]['commits'];
          if (i == 0) data[i].key = "commits";else data[i].key = "net lines changed";
        }

        data.forEach(function (el) {
          el.avg_commits = sum_commit / data.length;
          el.avg_loc = sum_loc / data.length;
          el.month_name = _this.months[el.month];
        });

        var dif_loc = Math.abs(max_loc - sum_loc / data.length) > Math.abs(min_loc - sum_loc / data.length) ? Math.abs(max_loc - sum_loc / data.length) : Math.abs(min_loc - sum_loc / data.length);
        var dif_commit = Math.abs(max_commit - sum_commit / data.length) > Math.abs(min_commit - sum_commit / data.length) ? Math.abs(max_commit - sum_commit / data.length) : Math.abs(min_commit - sum_commit / data.length);
        console.log("HERE", sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc);
        config.layer[0].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[0].encoding.y2.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[1].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[1].encoding.y2.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[2].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];
        config.layer[3].encoding.y.scale.domain = [sum_commit / data.length - dif_commit, sum_commit / data.length + dif_commit];
        config.layer[4].encoding.y.scale.domain = [sum_loc / data.length - dif_loc, sum_loc / data.length + dif_loc];

        repos.forEach(function (repo) {
          _this.values = data;
        });
      };
      return config;
    }
  }
};
})()
if (module.exports.__esModule) module.exports = module.exports.default
var __vue__options__ = (typeof module.exports === "function"? module.exports.options: module.exports)
if (__vue__options__.functional) {console.error("[vueify] functional components are not supported and should be defined in plain js files using render functions.")}
__vue__options__.render = function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{ref:"holder"},[_c('div',{staticClass:"groupedbarchart"},[_c('vega-lite',{attrs:{"spec":_vm.spec,"data":_vm.values}}),_vm._v(" "),_c('p',[_vm._v(" "+_vm._s(_vm.chart)+" ")]),_vm._v(" "),_vm._m(0)],1)])}
__vue__options__.staticRenderFns = [function render () {var _vm=this;var _h=_vm.$createElement;var _c=_vm._self._c||_h;return _c('div',{staticStyle:{"padding":"0 50px 0 50px","font-size":"12px"}},[_c('p',[_vm._v("*The black \"baseline\" represents the averages of both LoC and commits for this repo across all months. Wherever this bar stretches to shows how far above or below the raw value of the statistic is from the regular average.")])])}]
if (module.hot) {(function () {  var hotAPI = require("vue-hot-reload-api")
  hotAPI.install(require("vue"), true)
  if (!hotAPI.compatible) return
  module.hot.accept()
  if (!module.hot.data) {
    hotAPI.createRecord("data-v-a041a78c", __vue__options__)
  } else {
    hotAPI.reload("data-v-a041a78c", __vue__options__)
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

require.register("router.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _AugurCards = require('./components/AugurCards');

var _AugurCards2 = _interopRequireDefault(_AugurCards);

var _GrowthMaturityDeclineCard = require('./components/GrowthMaturityDeclineCard');

var _GrowthMaturityDeclineCard2 = _interopRequireDefault(_GrowthMaturityDeclineCard);

var _ExperimentalCard = require('./components/ExperimentalCard');

var _ExperimentalCard2 = _interopRequireDefault(_ExperimentalCard);

var _vueRouter = require('vue-router');

var _vueRouter2 = _interopRequireDefault(_vueRouter);

var _vue = require('vue');

var _vue2 = _interopRequireDefault(_vue);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

_vue2.default.use(_vueRouter2.default);

exports.default = new _vueRouter2.default({
    routes: [{ path: '/', component: _vue2.default.component('augur-cards', require('./components/AugurCards')) }]
});
});

;require.register("router/router.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _vue = require('vue');

var _vue2 = _interopRequireDefault(_vue);

var _vueRouter = require('vue-router');

var _vueRouter2 = _interopRequireDefault(_vueRouter);

var _MetricsStatusCard = require('../components/MetricsStatusCard.vue');

var _MetricsStatusCard2 = _interopRequireDefault(_MetricsStatusCard);

var _BaseRepoActivityCard = require('../components/BaseRepoActivityCard.vue');

var _BaseRepoActivityCard2 = _interopRequireDefault(_BaseRepoActivityCard);

var _BaseRepoEcosystemCard = require('../components/BaseRepoEcosystemCard.vue');

var _BaseRepoEcosystemCard2 = _interopRequireDefault(_BaseRepoEcosystemCard);

var _GrowthMaturityDeclineCard = require('../components/GrowthMaturityDeclineCard');

var _GrowthMaturityDeclineCard2 = _interopRequireDefault(_GrowthMaturityDeclineCard);

var _RiskCard = require('../components/RiskCard');

var _RiskCard2 = _interopRequireDefault(_RiskCard);

var _ValueCard = require('../components/ValueCard');

var _ValueCard2 = _interopRequireDefault(_ValueCard);

var _DiversityInclusionCard = require('../components/DiversityInclusionCard');

var _DiversityInclusionCard2 = _interopRequireDefault(_DiversityInclusionCard);

var _GitCard = require('../components/GitCard');

var _GitCard2 = _interopRequireDefault(_GitCard);

var _OverviewCard = require('../components/OverviewCard.vue');

var _OverviewCard2 = _interopRequireDefault(_OverviewCard);

var _ExperimentalCard = require('../components/ExperimentalCard');

var _ExperimentalCard2 = _interopRequireDefault(_ExperimentalCard);

var _DownloadedReposCard = require('../components/DownloadedReposCard.vue');

var _DownloadedReposCard2 = _interopRequireDefault(_DownloadedReposCard);

var _LoginForm = require('../components/LoginForm');

var _LoginForm2 = _interopRequireDefault(_LoginForm);

var _AugurCards = require('../components/AugurCards.vue');

var _AugurCards2 = _interopRequireDefault(_AugurCards);

var _MainControls = require('../components/MainControls.vue');

var _MainControls2 = _interopRequireDefault(_MainControls);

var _AugurHeader = require('../components/AugurHeader.vue');

var _AugurHeader2 = _interopRequireDefault(_AugurHeader);

var _Tabs = require('../components/Tabs.vue');

var _Tabs2 = _interopRequireDefault(_Tabs);

var _TableView = require('../components/TableView.vue');

var _TableView2 = _interopRequireDefault(_TableView);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

var routes = [{ path: '/', component: _AugurCards2.default,
  children: [{
    path: "",
    name: "reposcard",
    components: {
      header: _AugurHeader2.default,
      content: _DownloadedReposCard2.default
    }
  }]
}, { path: '/login', component: _LoginForm2.default }, { path: '/metrics_status',
  component: _MetricsStatusCard2.default
}, { path: '/single/:owner?/:repo', name: 'single', props: true, canReuse: false, component: _AugurCards2.default,
  children: [{
    path: "gmd",
    name: "gmd",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GrowthMaturityDeclineCard2.default
    }
  }, {
    path: "diversityinclusion",
    name: "diversityinclusion",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _DiversityInclusionCard2.default
    }
  }, {
    path: "risk",
    name: "risk",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _RiskCard2.default
    }
  }, {
    path: "activity",
    name: "activity",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _BaseRepoActivityCard2.default
    }
  }, {
    path: "value",
    name: "value",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ValueCard2.default
    }
  }, {
    path: "experimental",
    name: "experimental",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ExperimentalCard2.default
    }
  }, {
    path: "git",
    name: "git",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GitCard2.default
    }
  }, {
    path: "overview",
    name: "overview",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _OverviewCard2.default
    }
  }]
},
// {path: '/:tab/:domain/:owner/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'gitsinglecompare'},
{ path: '/compare/:owner?/:repo/comparedto/:comparedowner/:comparedrepo', component: _AugurCards2.default, name: 'singlecompare', props: true, canReuse: false,
  children: [{
    path: "gmd",
    name: "gmdcompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GrowthMaturityDeclineCard2.default
    }
  }, {
    path: "diversityinclusion",
    name: "diversityinclusioncompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _DiversityInclusionCard2.default
    }
  }, {
    path: "risk",
    name: "riskcompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _RiskCard2.default
    }
  }, {
    path: "value",
    name: "valuecompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ValueCard2.default
    }
  }, {
    path: "activity",
    name: "activitycompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _BaseRepoActivityCard2.default
    }
  }, {
    path: "experimental",
    name: "experimentalcompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ExperimentalCard2.default
    }
  }, {
    path: "git",
    name: "gitcompare",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GitCard2.default
    }
  }]
}, { path: '/groupcompare/:groupid', component: _AugurCards2.default, name: 'group', props: true, canReuse: false,
  children: [{
    path: "gmd",
    name: "gmdgroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GrowthMaturityDeclineCard2.default
    }
  }, {
    path: "diversityinclusion",
    name: "diversityinclusiongroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _DiversityInclusionCard2.default
    }
  }, {
    path: "risk",
    name: "riskgroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _RiskCard2.default
    }
  }, {
    path: "value",
    name: "valuegroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ValueCard2.default
    }
  }, {
    path: "activity",
    name: "activitygroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _BaseRepoActivityCard2.default
    }
  }, {
    path: "experimental",
    name: "experimentalgroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _ExperimentalCard2.default
    }
  }, {
    path: "git",
    name: "gitgroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _GitCard2.default
    }
  }, {
    path: "overview",
    name: "overviewgroup",
    components: {
      header: _AugurHeader2.default,
      tabs: _Tabs2.default,
      controls: _MainControls2.default,
      content: _OverviewCard2.default
    }
  }]
}];
var downloadedRepos = [],
    repos = [],
    projects = [];
window.AugurAPI.getDownloadedGitRepos().then(function (data) {

  repos = window._.groupBy(data, 'project_name');
  projects = Object.keys(repos);
});
// const routes = routerOptions.map(route => {
//   // let route1 = Object.assign({}, route);
//   return {
//     route,
//     component: () => require(`@/components/${route.component}.vue`)
//   }
// })


exports.default = new _vueRouter2.default({
  // routes,
  routes: routes,
  mode: 'history',
  hashbang: false
});
});

;require.alias("buffer/index.js", "buffer");
require.alias("process/browser.js", "process");
require.alias("vue/dist/vue.common.js", "vue");process = require('process');require.register("___globals___", function(exports, require, module) {
  
});})();require('___globals___');


//# sourceMappingURL=app.js.map