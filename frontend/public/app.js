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
require.register("components/contributions.tag", function(exports, require, module) {
riot.tag('contributions', '<div class="echarts-container" style="width: 100%; height: 400px;"></div>', function(opts) {

  this.on('mount', () => {
    var echarts = require('echarts')
    var chart = echarts.init(this.root.querySelector('.echarts-container'))
    chart.showLoading()

    this.opts.api.get('contributions', {orient: 'split'}).then((contributions) => {

      var data = [];

      contributions.data.forEach((row) => {
        for (var i = 1; i < row.length; i++) {
          if (!row[i]) {
            row[i] = 0
          }
          data.push([row[0], row[i], (i-1)])
        }
      })

      console.log(data)

      chart.hideLoading()
      chart.setOption({
          series: [{
              type: 'themeRiver',
              data: data
          }]
      })

    })
  })


});
});

require.register("components/githubform.tag", function(exports, require, module) {
riot.tag('githubform', '<img src="images/logo.svg" alt="OSSHealth" class="logo"> <input type="text" placeholder="GitHub URL" ref="githubURL"> <button onclick="{ submit }">Analyze</button><br><br>', function(opts) {

this.submit = function (e) {
  var splitURL = this.root.querySelectorAll('input')[0].value.split('/')
  var repo, owner
  if (splitURL.length > 2) {
    console.log('big')
    repo = splitURL[3]
    owner = splitURL[4]
  } else if (splitURL.length === 2) {
    console.log('lil')
    repo = splitURL[0]
    owner = splitURL[1]
  } else {
    let errorMessage = document.createElement('p')
    errorMessage.style.color = '#f00'
    errorMessage.innerHTML = 'Enter a valid URL'
    this.root.appendChild(errorMessage)
    return
  }
  this.opts.onsubmit(owner, repo)
}.bind(this);


});
});

require.register("components/healthreport.tag", function(exports, require, module) {
riot.tag('healthreport', '<div class="container"> <section> <div class="row"> <div class="nine columns"><h1 id="repo-label">{owner} / {repo}</h1></div> </div> </section> <section> <h2>Contributions</h2> <div class="row"> <div class="twelve columns"><contributions></contributions></div> </div> </section> </div>', function(opts) {

  this.owner = this.opts.owner
  this.repo = this.opts.repo

  var ghdata = require('../lib/ghdata-api-client')
  var api = new ghdata.GHDataAPIClient(undefined, this.owner, this.repo)
  console.log(api)
  console.log(api.get)

  this.on('mount', function () {
    require('./contributions.tag');
    riot.mount('contributions', {api: api})
  })


});
});

require.register("components/report.tag", function(exports, require, module) {
riot.tag('HealthReport', '<section> <div class="row"> <div class="nine columns"><h1 id="repo-label"> facebook / folly </h1></div> <div class="three columns"><div id="status" class="badge healthy">healthy</div></div> </div> </section> <section> <h2>Growth Indicators</h2> <div class="row trends"> <TimeseriesGraph path="commits"></div> <div class="four columns" id="commits-over-time"></div> <div class="four columns" id="stargazers-over-time"></div> <div class="four columns" id="forks-over-time"></div> </div>  <div class="row trends"> <div class="four columns" id="issues-over-time"></div> <div class="four columns" id="pulls-over-time"></div> </div> </section>', function(opts) {


});
});

require.register("ghdata-api-client.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.default = GHDataAPIClient;
/* SPDX-License-Identifier: MIT */

/**
 * Handles interaction with a GHData server.
 * @constructor
 */
function GHDataAPIClient(apiUrl, owner, repo, apiVersion) {
  this.owner = owner || '';
  this.repo = repo || '';
  this.url = apiUrl || 'http://' + document.location.hostname + ':5000/';
  this.apiversion = apiVersion || 'unstable';
}

/* Request Handling
 * Create a friendly wrapper around XMLHttpRequest
--------------------------------------------------------------*/

/**
 * Wraps XMLHttpRequest with many goodies. Credit to SomeKittens on StackOverflow.
 * @param {Object} opts - Stores the url (opts.url), method (opts.method), headers (opts.headers) and query parameters (opt.params). All optional.
 * @returns {Promise} Resolves with XMLHttpResponse.response
 */
GHDataAPIClient.prototype.request = function (opts) {
  // Use GHData by default
  opts.endpoint = opts.endpoint || '';
  opts.url = opts.url || this.url + this.apiversion + '/' + this.owner + '/' + this.repo + '/' + opts.endpoint;
  opts.method = opts.method || 'GET';
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open(opts.method, opts.url);
    xhr.onload = function () {
      if (this.status >= 200 && this.status < 300) {
        resolve(xhr.response);
      } else {
        reject({
          status: this.status,
          statusText: xhr.statusText
        });
      }
    };
    xhr.onerror = function () {
      reject({
        status: this.status,
        statusText: xhr.statusText
      });
    };
    if (opts.headers) {
      Object.keys(opts.headers).forEach(function (key) {
        xhr.setRequestHeader(key, opts.headers[key]);
      });
    }
    var params = opts.params;
    // We'll need to stringify if we've been given an object
    // If we have a string, this is skipped.
    if (params && (typeof params === 'undefined' ? 'undefined' : _typeof(params)) === 'object') {
      params = Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
      }).join('&');
    }
    xhr.send(params);
  });
};

/**
 * Wraps the GET requests with the correct options for most GHData calls
 * @param {String} endpoint - Endpoint to send the request to
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with Object created from the JSON returned by GHData
 */
GHDataAPIClient.prototype.get = function (endpoint, params) {
  var self = this;
  return new Promise(function (resolve, request) {
    self.request({
      method: 'GET',
      endpoint: endpoint,
      params: params
    }).then(function (response) {
      // Lets make this thing JSON
      var result = JSON.parse(response);
      resolve(result);
    });
  });
};

/* Endpoints
 * Wrap all the API endpoints to make it as simple as possible
--------------------------------------------------------------*/

/**
 * Commits timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.commitsByWeek = function (params) {
  return this.get('timeseries/commits', params);
};

/**
 * Forks timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with forks timeeseries object
 */
GHDataAPIClient.prototype.forksByWeek = function (params) {
  return this.get('timeseries/forks', params);
};

/**
 * Stargazers timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.stargazersByWeek = function (params) {
  return this.get('timeseries/stargazers', params);
};

/**
 * Issues timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.issuesByWeek = function (params) {
  return this.get('timeseries/issues', params);
};

/**
 * Pull Requests timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.pullRequestsByWeek = function (params) {
  return this.get('timeseries/pulls', params);
};

/**
 * Pull Requests timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.contributionsByWeek = function (params) {
  return this.get('timeseries/contributions', params);
};

/**
 * How quickly after issues are made they are commented on
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.issuesResponseTime = function (params) {
  return this.get('timeseries/issues/response_time', params);
};

/**
 * Contributions timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.contributors = function (params) {
  return this.get('timeseries/contributors', params);
};

/**
 * Locations of the committers
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.committerLocations = function (params) {
  return this.get('commits/locations', params);
};

});

require.register("index.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.buildForm = buildForm;
exports.start = start;
require('riot');

function buildForm(owner, repo) {
  require('./components/healthreport');
  riot.mount('healthreport', { owner: owner, repo: repo });
}

function start() {
  require('./components/githubform');
  riot.mount('githubform', { onsubmit: buildForm });
  //riot.mount('report', {owner: owner, repo: repo});
}

});

;require.register("lib/ghdata-api-client.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.GHDataAPIClient = GHDataAPIClient;
/* SPDX-License-Identifier: MIT */

/**
 * Handles interaction with a GHData server.
 * @constructor
 */
function GHDataAPIClient(apiUrl, owner, repo, apiVersion) {
  this.owner = owner || '';
  this.repo = repo || '';
  this.url = apiUrl || 'http://' + document.location.hostname + ':5000/';
  this.apiversion = apiVersion || 'unstable';
  return this;
}

/* Request Handling
 * Create a friendly wrapper around XMLHttpRequest
--------------------------------------------------------------*/

/**
 * Wraps XMLHttpRequest with many goodies. Credit to SomeKittens on StackOverflow.
 * @param {Object} opts - Stores the url (opts.url), method (opts.method), headers (opts.headers) and query parameters (opt.params). All optional.
 * @returns {Promise} Resolves with XMLHttpResponse.response
 */
GHDataAPIClient.prototype.request = function (opts) {
  // Use GHData by default
  opts.endpoint = opts.endpoint || '';
  opts.url = opts.url || this.url + this.apiversion + '/' + this.owner + '/' + this.repo + '/' + opts.endpoint;
  opts.method = opts.method || 'GET';
  return new Promise(function (resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open(opts.method, opts.url);
    xhr.onload = function () {
      if (this.status >= 200 && this.status < 300) {
        resolve(xhr.response);
      } else {
        reject({
          status: this.status,
          statusText: xhr.statusText
        });
      }
    };
    xhr.onerror = function () {
      reject({
        status: this.status,
        statusText: xhr.statusText
      });
    };
    if (opts.headers) {
      Object.keys(opts.headers).forEach(function (key) {
        xhr.setRequestHeader(key, opts.headers[key]);
      });
    }
    var params = opts.params;
    // We'll need to stringify if we've been given an object
    // If we have a string, this is skipped.
    if (params && (typeof params === 'undefined' ? 'undefined' : _typeof(params)) === 'object') {
      params = Object.keys(params).map(function (key) {
        return encodeURIComponent(key) + '=' + encodeURIComponent(params[key]);
      }).join('&');
    }
    xhr.send(params);
  });
};

/**
 * Wraps the GET requests with the correct options for most GHData calls
 * @param {String} endpoint - Endpoint to send the request to
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with Object created from the JSON returned by GHData
 */
GHDataAPIClient.prototype.get = function (endpoint, params) {
  var self = this;
  return new Promise(function (resolve, request) {
    self.request({
      method: 'GET',
      endpoint: endpoint,
      params: params
    }).then(function (response) {
      // Lets make this thing JSON
      var result = JSON.parse(response);
      resolve(result);
    });
  });
};

/* Endpoints
 * Wrap all the API endpoints to make it as simple as possible
--------------------------------------------------------------*/

/**
 * Commits timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.commitsByWeek = function (params) {
  return this.get('timeseries/commits', params);
};

/**
 * Forks timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with forks timeeseries object
 */
GHDataAPIClient.prototype.forksByWeek = function (params) {
  return this.get('timeseries/forks', params);
};

/**
 * Stargazers timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.stargazersByWeek = function (params) {
  return this.get('timeseries/stargazers', params);
};

/**
 * Issues timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.issuesByWeek = function (params) {
  return this.get('timeseries/issues', params);
};

/**
 * Pull Requests timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.pullRequestsByWeek = function (params) {
  return this.get('timeseries/pulls', params);
};

/**
 * Pull Requests timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.contributionsByWeek = function (params) {
  return this.get('timeseries/contributions', params);
};

/**
 * How quickly after issues are made they are commented on
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.issuesResponseTime = function (params) {
  return this.get('timeseries/issues/response_time', params);
};

/**
 * Contributions timeseries
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.contributors = function (params) {
  return this.get('timeseries/contributors', params);
};

/**
 * Locations of the committers
 * @param {Object} params - Query string params to pass to the API
 * @returns {Promise} Resolves with commits timeseries object
 */
GHDataAPIClient.prototype.committerLocations = function (params) {
  return this.get('commits/locations', params);
};

});

require.register("posts.tag", function(exports, require, module) {
riot.tag('posts', '<h1>work</h1>', function(opts) {
  
});

});

require.alias("brunch/node_modules/process/browser.js", "process");process = require('process');require.register("___globals___", function(exports, require, module) {
  
});})();require('___globals___');


//# sourceMappingURL=app.js.map