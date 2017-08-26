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
require.register("GHDataAPI.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var $ = require('jquery');

var GHDataAPI = function () {
  function GHDataAPI(hostURL, version) {
    _classCallCheck(this, GHDataAPI);

    this._version = version || 'unstable';
    this._host = hostURL || 'http://' + window.location.hostname + ':5000/';
    this.__cache = {};
  }

  _createClass(GHDataAPI, [{
    key: 'Repo',
    value: function Repo(owner, repoName) {
      var _this = this;

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
        var self = _this;
        var url = _this._host + _this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint;
        return function (params, callback) {
          if (self.__cache[btoa(url)]) {
            if (self.__cache[btoa(url)].created_at > Date.now() - 1000 * 60) {
              return new Promise(function (resolve, reject) {
                resolve(JSON.parse(self.__cache[btoa(url)].data));
              });
            }
          }
          return $.get(url, params, callback).then(function (data) {
            self.__cache[btoa(url)] = {
              created_at: Date.now(),
              data: JSON.stringify(data)
            };
            if (typeof callback === 'function') {
              callback(data);
            }
            return new Promise(function (resolve, reject) {
              resolve(data);
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
      repo.uniqueCommitters = Timeseries('unique_committers');

      repo.pullsAcceptanceRate = Endpoint('pulls/acceptance_rate');
      repo.issuesResponseTime = Endpoint('issues/response_time');
      repo.contributors = Endpoint('contributors');
      repo.contributions = Endpoint('contributions');
      repo.committerLocations = Endpoint('committer_locations');
      repo.communityAge = Endpoint('community_age');
      repo.linkingWebsites = Endpoint('linking_websites');
      repo.busFactor = Endpoint('bus_factor');
      repo.dependents = Endpoint('dependents');
      repo.dependencies = Endpoint('dependencies');

      return repo;
    }
  }]);

  return GHDataAPI;
}();

exports.default = GHDataAPI;

});

require.register("GHDataCharts.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _metricsGraphics = require('metrics-graphics');

var _metricsGraphics2 = _interopRequireDefault(_metricsGraphics);

var _d = require('d3');

var d3 = _interopRequireWildcard(_d);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

window.$ = require('jquery');
window.jQuery = window.$;

var GHDataCharts = function () {
  function GHDataCharts() {
    _classCallCheck(this, GHDataCharts);
  }

  _createClass(GHDataCharts, null, [{
    key: 'convertDates',
    value: function convertDates(data) {
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return GHDataCharts.convertDates(datum);
        });
      } else {
        var EARLIEST = new Date('01-01-2005');
        data = data.map(function (d) {
          d.date = new Date(d.date);
          return d;
        }).filter(function (d) {
          return d.date > EARLIEST;
        });
      }
      return data;
    }
  }, {
    key: 'convertKey',
    value: function convertKey(data, key) {
      if (Array.isArray(data[0])) {
        data = data.map(function (datum) {
          return GHDataCharts.convertKey(datum, key);
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
    key: 'rollingAverage',
    value: function rollingAverage(data, windowSizeInDays) {
      var windowMiliseconds = windowSizeInDays * 24 /*hours*/ * 60 /*minutes*/ * 60 /*seconds*/ * 1000 /*miliseconds*/;
      var keys = Object.keys(data[0]);
      var rolling = [];
      data.forEach(function (elem) {
        var after = new Date(elem.date).getTime() - windowMiliseconds;
        var before = new Date(elem.date).getTime();
        var average = {};
        var count = 0;
        data.forEach(function (toAverage) {
          var testDate = new Date(toAverage.date).getTime();
          if (testDate <= before && testDate >= after) {
            count++;
            keys.forEach(function (prop) {
              if (!isNaN(toAverage[prop] / 2.0) && average[prop] && prop !== 'date') {
                if (!average[prop]) {
                  average[prop] = 0;
                }
                average[prop] += toAverage[prop];
              } else if (!isNaN(toAverage[prop] / 2.0) || prop === 'date') {
                average[prop] = toAverage[prop];
              }
            });
          }
        });
        for (var prop in average) {
          if (average.hasOwnProperty(prop) && prop !== 'date') {
            average[prop] = average[prop] / count;
          }
        }
        rolling.push(average);
      });
      return rolling;
    }
  }, {
    key: 'convertToPercentages',
    value: function convertToPercentages(data) {
      if (data && data[0]) {
        var keys = Object.keys(data[0]);
      } else {
        return [];
      }
      if (keys[1] !== 'date' && !isNaN(data[0][keys[1]] / 2.0)) {
        var baseline = (data[0][keys[1]] + data[1][keys[1]]) / 2;
        if (isNaN(baseline)) {
          baseline = 1;
        }
        data = data.map(function (datum) {
          datum['value'] = datum[keys[1]] / baseline;
          return datum;
        });
      }
      return data;
    }
  }, {
    key: 'combine',
    value: function combine() {
      return Array.from(arguments);
    }
  }, {
    key: 'ComparisonLineChart',
    value: function ComparisonLineChart(selector, data, title, baseline) {
      GHDataCharts.convertDates(data);
      var keys = Object.keys(data[0]).filter(function (d) {
        return (/ratio/.test(d)
        );
      });
      console.log(keys);
      return _metricsGraphics2.default.data_graphic({
        title: title || 'Comparison',
        data: data,
        full_width: true,
        height: 200,
        baselines: [{ value: 1, label: baseline || 'Other Repo' }],
        format: 'percentage',
        x_accessor: 'date',
        y_accessor: keys,
        target: selector
      });
    }
  }, {
    key: 'LineChart',
    value: function LineChart(selector, data, title, rollingAverage) {
      var data_graphic_config = {
        title: title || 'Activity',
        data: data,
        full_width: true,
        height: 200,
        x_accessor: 'date',
        target: selector
      };

      GHDataCharts.convertDates(data);

      if (rollingAverage) {
        data_graphic_config.legend = [title.toLowerCase(), '6 month average'];
        console.log(data);
        var rolling = GHDataCharts.rollingAverage(data, 180);
        data_graphic_config.data = GHDataCharts.convertKey(GHDataCharts.combine(data, rolling), Object.keys(data[0])[1]);
        console.log(data_graphic_config.data);
        data_graphic_config.colors = ['#CCC', '#FF3647'];
        data_graphic_config.y_accessor = 'value';
      }

      if (Array.isArray(data_graphic_config.data[0])) {
        data_graphic_config.legend = data_graphic_config.legend || ['compared', 'base'];
        data_graphic_config.colors = data_graphic_config.colors || ['#FF3647', '#999'];
        data_graphic_config.y_accessor = data_graphic_config.y_accessor || Object.keys(data_graphic_config.data[0][0]).slice(1);
      } else {
        data_graphic_config.y_accessor = Object.keys(data[0]).slice(1);
        data_graphic_config.legend = data_graphic_config.y_accessor;
      }

      if (Object.keys(data_graphic_config.data[0]).slice(1).length > 1) {
        var legend = document.createElement('div');
        legend.style.position = 'relative';
        legend.style.margin = '0';
        legend.style.padding = '0';
        legend.style.height = '0';
        legend.style.top = '31px';
        legend.style.left = '55px';
        legend.style.fontSize = '14px';
        legend.style.fontWeight = 'bold';
        legend.style.opacity = '0.8';
        $(selector).append(legend);
        data_graphic_config.legend_target = legend;
        $(selector).hover(function () {
          legend.style.display = 'none';
        }, function () {
          legend.style.display = 'block';
        });
      }

      var chart = _metricsGraphics2.default.data_graphic(data_graphic_config);
    }
  }, {
    key: 'Timeline',
    value: function Timeline(selector, data, title) {
      var dataCleaned = [];
      var legend = [];
      for (var event in data) {
        if (data.hasOwnProperty(event)) {
          dataCleaned.push([{
            date: new Date(data[event]),
            value: 10
          }]);
          legend.push(event);
        }
      }
      console.log(dataCleaned);
      return _metricsGraphics2.default.data_graphic({
        title: title || 'Timeline',
        data: dataCleaned,
        full_width: true,
        height: 200,
        x_accessor: 'date',
        legend: legend,
        target: selector
      });
    }
  }, {
    key: 'NoChart',
    value: function NoChart(selector, title) {
      return _metricsGraphics2.default.data_graphic({
        title: "Missing Data",
        error: 'Data unavaliable for ' + title,
        chart_type: 'missing-data',
        missing_text: title + ' could not be loaded',
        target: '#missing-data',
        full_width: true,
        height: 200
      });
    }
  }]);

  return GHDataCharts;
}();

exports.default = GHDataCharts;

});

require.register("lib/kube/kube.js", function(exports, require, module) {
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

require.register("lib/mg_line_brushing.js", function(exports, require, module) {
'use strict';

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.default = AddBrushingCapability;

var _d = require('d3');

var d3 = _interopRequireWildcard(_d);

var _jquery = require('jquery');

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function AddBrushingCapability(MG) {

    /*
    The MIT License (MIT)
     Copyright (c) 2015 Dan de Havilland
     Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
     The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
    */

    MG.line_brushing = {
        set_brush_as_base: function set_brush_as_base(target) {
            var svg = d3.select(target).select('svg'),
                current,
                history = brushHistory[target];

            svg.classed('mg-brushed', false);

            if (history) {
                history.brushed = false;

                current = history.current;
                history.original = current;

                args.min_x = current.min_x;
                args.max_x = current.max_x;
                args.min_y = current.min_y;
                args.max_y = current.max_y;

                history.steps = [];
            }
        },

        zoom_in: function zoom_in(target, options) {},

        zoom_out: function zoom_out(target, options) {}
    };

    /* helpers */
    function get_brush_interval(args) {
        var resolution = args.brushing_interval,
            interval;

        if (!resolution) {
            if (args.time_series) {
                resolution = d3.timeDay;
            } else {
                resolution = 1;
            }
        }

        // work with N as integer
        if (typeof resolution === 'number') {
            interval = {
                round: function round(val) {
                    return resolution * Math.round(val / resolution);
                },
                offset: function offset(val, count) {
                    return val + resolution * count;
                }
            };
        }
        // work with d3.time.[interval]
        else if (typeof resolution.round === 'function' && typeof resolution.offset === 'function') {
                interval = resolution;
            } else {
                console.warn('The `brushing_interval` provided is invalid. It must be either a number or expose both `round` and `offset` methods');
            }

        return interval;
    }

    function is_within_bounds(datum, args) {
        var x = +datum[args.x_accessor],
            y = +datum[args.y_accessor];

        return x >= (+args.processed.min_x || x) && x <= (+args.processed.max_x || x) && y >= (+args.processed.min_y || y) && y <= (+args.processed.max_y || y);
    }

    /**
      Brushing for line charts
       1. hooks
    */

    var brushHistory = {},
        args;

    MG.add_hook('global.defaults', function (args) {
        // enable brushing unless it's explicitly disabled
        args.brushing = args.brushing !== false;
        if (args.brushing) {
            args.brushing_history = args.brushing_history !== false;
            args.aggregate_rollover = true;
        }
    });

    function brushing() {
        var chartContext = this;

        args = this.args;

        if (args.brushing === false) {
            return this;
        }

        if (!brushHistory[args.target] || !brushHistory[args.target].brushed) {
            brushHistory[args.target] = {
                brushed: false,
                steps: [],
                original: {
                    min_x: +args.processed.min_x,
                    max_x: +args.processed.max_x,
                    min_y: +args.processed.min_y,
                    max_y: +args.processed.max_y
                }
            };
        }

        var isDragging = false,
            mouseDown = false,
            originX,
            svg = d3.select(args.target).select('svg'),
            body = d3.select('body'),
            rollover = svg.select('.mg-rollover-rect, .mg-voronoi'),
            brushingGroup,
            extentRect;

        rollover.classed('mg-brush-container', true);

        brushingGroup = rollover.insert('g', '*').classed('mg-brush', true);

        extentRect = brushingGroup.append('rect').attr('opacity', 0).attr('y', args.top).attr('height', args.height - args.bottom - args.top - args.buffer).classed('mg-extent', true);

        // mousedown, start area selection
        svg.on('mousedown', function () {
            mouseDown = true;
            isDragging = false;
            originX = d3.mouse(this)[0];
            svg.classed('mg-brushed', false);
            svg.classed('mg-brushing-in-progress', true);
            extentRect.attr({
                x: d3.mouse(this)[0],
                opacity: 0,
                width: 0
            });
        });

        // mousemove / drag, expand area selection
        svg.on('mousemove', function () {
            if (mouseDown) {
                isDragging = true;
                rollover.classed('mg-brushing', true);

                var mouseX = d3.mouse(this)[0],
                    newX = Math.min(originX, mouseX),
                    width = Math.max(originX, mouseX) - newX;

                extentRect.attr('x', newX).attr('width', width).attr('opacity', 1);
            }
        });

        // mouseup, finish area selection
        svg.on('mouseup', function () {
            mouseDown = false;
            svg.classed('mg-brushing-in-progress', false);

            var xScale = args.scales.X,
                yScale = args.scales.Y,
                flatData = [].concat.apply([], args.data),
                boundedData,
                yBounds,
                xBounds,
                extentX0 = +extentRect.attr('x'),
                extentX1 = extentX0 + +extentRect.attr('width'),
                interval = get_brush_interval(args),
                offset = 0,
                mapDtoX = function mapDtoX(d) {
                return +d[args.x_accessor];
            },
                mapDtoY = function mapDtoY(d) {
                return +d[args.y_accessor];
            };

            // if we're zooming in: calculate the domain for x and y axes based on the selected rect
            if (isDragging) {
                isDragging = false;

                if (brushHistory[args.target].brushed) {
                    brushHistory[args.target].steps.push({
                        max_x: args.brushed_max_x || args.processed.max_x,
                        min_x: args.brushed_min_x || args.processed.min_x,
                        max_y: args.brushed_max_y || args.processed.max_y,
                        min_y: args.brushed_min_y || args.processed.min_y
                    });
                }

                brushHistory[args.target].brushed = true;

                boundedData = [];
                // is there at least one data point in the chosen selection? if not, increase the range until there is.
                var iterations = 0;
                while (boundedData.length === 0 && iterations <= flatData.length) {

                    var xValX0 = xScale.invert(extentX0);
                    var xValX1 = xScale.invert(extentX1);
                    xValX0 = xValX0 instanceof Date ? xValX0 : interval.round(xValX0);
                    xValX1 = xValX1 instanceof Date ? xValX1 : interval.round(xValX1);

                    args.brushed_min_x = xValX0;
                    args.brushed_max_x = Math.max(interval.offset(args.min_x, 1), xValX1);

                    boundedData = flatData.filter(function (d) {
                        var val = d[args.x_accessor];
                        return val >= args.brushed_min_x && val <= args.brushed_max_x;
                    });

                    iterations++;
                }

                xBounds = d3.extent(boundedData, mapDtoX);
                args.brushed_min_x = +xBounds[0];
                args.brushed_max_x = +xBounds[1];
                xScale.domain(xBounds);

                yBounds = d3.extent(boundedData, mapDtoY);
                // add 10% padding on the y axis for better display
                // @TODO: make this an option
                args.brushed_min_y = yBounds[0] * 0.9;
                args.brushed_max_y = yBounds[1] * 1.1;
                yScale.domain(yBounds);
            }
            // zooming out on click, maintaining the step history
            else if (args.brushing_history) {
                    if (brushHistory[args.target].brushed) {
                        var previousBrush = brushHistory[args.target].steps.pop();
                        if (previousBrush) {
                            args.brushed_max_x = previousBrush.max_x;
                            args.brushed_min_x = previousBrush.min_x;
                            args.brushed_max_y = previousBrush.max_y;
                            args.brushed_min_y = previousBrush.min_y;

                            xBounds = [args.brushed_min_x, args.brushed_max_x];
                            yBounds = [args.brushed_min_y, args.brushed_max_y];
                            xScale.domain(xBounds);
                            yScale.domain(yBounds);
                        } else {
                            brushHistory[args.target].brushed = false;

                            delete args.brushed_max_x;
                            delete args.brushed_min_x;
                            delete args.brushed_max_y;
                            delete args.brushed_min_y;

                            xBounds = [brushHistory[args.target].original.min_x, brushHistory[args.target].original.max_x];

                            yBounds = [brushHistory[args.target].original.min_y, brushHistory[args.target].original.max_y];
                        }
                    }
                }

            // has anything changed?
            if (xBounds && yBounds) {
                if (xBounds[0] < xBounds[1]) {
                    // trigger the brushing callback

                    var step = {
                        min_x: xBounds[0],
                        max_x: xBounds[1],
                        min_y: yBounds[0],
                        max_y: yBounds[1]
                    };

                    brushHistory[args.target].current = step;

                    if (args.after_brushing) {
                        args.after_brushing.apply(this, [step]);
                    }
                }

                // redraw the chart
                if (!args.brushing_manual_redraw) {
                    MG.data_graphic(args);
                }
            }
        });

        return this;
    }

    MG.add_hook('line.after_init', function (lineChart) {
        brushing.apply(lineChart);
    });

    function processXAxis(args, min_x, max_x) {
        if (args.brushing) {
            args.processed.min_x = args.brushed_min_x ? Math.max(args.brushed_min_x, min_x) : min_x;
            args.processed.max_x = args.brushed_max_x ? Math.min(args.brushed_max_x, max_x) : max_x;
        }
    }

    MG.add_hook('x_axis.process_min_max', processXAxis);

    function processYAxis(args) {
        if (args.brushing && (args.brushed_min_y || args.brushed_max_y)) {
            args.processed.min_y = args.brushed_min_y;
            args.processed.max_y = args.brushed_max_y;
        }
    }

    MG.add_hook('y_axis.process_min_max', processYAxis);

    function afterRollover(args) {
        if (args.brushing_history && brushHistory[args.target] && brushHistory[args.target].brushed) {
            var svg = d3.select(args.target).select('svg');
            svg.classed('mg-brushed', true);
        }
    }

    MG.add_hook('line.after_rollover', afterRollover);

    return;
}

});

;require.register("ui.js", function(exports, require, module) {
'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _GHDataCharts = require('./GHDataCharts');

var _GHDataCharts2 = _interopRequireDefault(_GHDataCharts);

var _GHDataAPI = require('./GHDataAPI');

var _GHDataAPI2 = _interopRequireDefault(_GHDataAPI);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

var queryString = require('query-string');

var GHDataDashboard = function () {
  function GHDataDashboard(state) {
    var _this = this;

    _classCallCheck(this, GHDataDashboard);

    this.EMPTY_STATE = {
      comparedTo: []
    };
    this.STARTING_HTML = $('#cards')[0].innerHTML;
    this.state = state || this.EMPTY_STATE;
    this.ghdata = new _GHDataAPI2.default();
    if (/repo/.test(location.search) && !state) {
      console.log('State from URL');
      this.setStateFromURL();
    }
    window.addEventListener('popstate', function (e) {
      _this.setStateFromURL();
    });
  }

  _createClass(GHDataDashboard, [{
    key: 'setStateFromURL',
    value: function setStateFromURL() {
      var _this2 = this;

      var parsed = queryString.parse(location.search, { arrayFormat: 'bracket' });
      var state = {
        comparedTo: []
      };
      state.repo = this.ghdata.Repo(parsed.repo.replace(' ', '/'));
      if (parsed.comparedTo) {
        parsed.comparedTo.forEach(function (repo) {
          state.comparedTo.push(_this2.ghdata.Repo(repo.replace(' ', '/')));
        });
      }
      this.state = state;
      this.render();
    }
  }, {
    key: 'pushState',
    value: function pushState(state, title) {
      this.state = state || this.state;
      title = title || this.state.repo.owner + '/' + this.state.repo.name;
      var queryString = '?repo=' + this.state.repo.owner + '+' + this.state.repo.name;
      this.state.comparedTo.forEach(function (repo) {
        queryString += '&comparedTo[]=' + repo.owner + '+' + repo.name;
      });
      history.pushState(null, title, queryString);
      document.title = title;
    }
  }, {
    key: 'addCard',
    value: function addCard(title, repo, className) {
      var cardElement = document.createElement('section');
      if (className) {
        cardElement.className = className;
      }
      var titleElement = document.createElement('h1');
      var repoElement = document.createElement('h2');
      titleElement.innerHTML = title;
      repoElement.innerHTML = repo;
      $('#cards').append(cardElement);
      $(cardElement).append(titleElement);
      $(cardElement).append(repoElement);
      return cardElement;
    }
  }, {
    key: 'renderGraphs',
    value: function renderGraphs(element, repo) {
      $(element).find('.linechart').each(function (index, element) {
        var title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1);
        console.log(element.dataset.source);
        repo[element.dataset.source]().then(function (data) {
          if (data && data.length) {
            $(element).find('cite').each(function (i, e) {
              $(e).show();
            });
            _GHDataCharts2.default.LineChart(element, data, title, typeof element.dataset.rolling !== 'undefined');
          } else {
            _GHDataCharts2.default.NoChart(element, title);
          }
        }, function (error) {
          _GHDataCharts2.default.NoChart(element, title);
        });
      });
    }
  }, {
    key: 'renderComparisonForm',
    value: function renderComparisonForm() {
      var self = this;
      if (this.comparisonCard && this.comparisonCard.parentElement) {
        this.comparisonCard.outerHTML = '';
      }
      this.comparisonCard = this.addCard(null, null, 'unmaterialized');
      $(this.comparisonCard).append($('#comparison-form-template')[0].innerHTML);
      $(this.comparisonCard).find('.search').on('keyup', function (e) {
        if (e.keyCode === 13) {
          var comparedRepo = self.ghdata.Repo(this.value);
          self.state.comparedTo.push(comparedRepo);
          self.pushState();
          self.renderComparisonRepo(null, comparedRepo);
        }
      });
    }
  }, {
    key: 'renderBaseRepo',
    value: function renderBaseRepo(repo) {
      repo = repo || this.state.repo;
      $('#main-repo-search').val(repo.owner + '/' + repo.name);

      var activityCard = this.addCard('Activity', '<strong>' + repo.owner + '/' + repo.name + '</strong>');
      activityCard.innerHTML += $('#base-template')[0].innerHTML;
      this.renderGraphs(activityCard, repo);

      var ecosystemCard = this.addCard('Ecosystem', '<strong>' + repo.owner + '/' + repo.name + '</strong>');
      ecosystemCard.innerHTML += $('#ecosystem-template')[0].innerHTML;
      this.renderGraphs(ecosystemCard, repo);
      repo.dependents().then(function (dependents) {
        for (var i = 0; i < dependents.length && i < 10; i++) {
          $(ecosystemCard).find('#dependents').append(dependents[i].name + '<br>');
        }
      });
      repo.dependencies().then(function (dependencies) {
        for (var i = 0; i < dependencies.dependencies.length && i < 10; i++) {
          $(ecosystemCard).find('#dependencies').append(dependencies.dependencies[i].name + '<br>');
        }
      });

      this.renderComparisonForm();
    }
  }, {
    key: 'renderComparisonRepo',
    value: function renderComparisonRepo(compareRepo, baseRepo) {
      compareRepo = compareRepo || this.state.repo;
      var activityComparisonCard = this.addCard('Activity', '<strong>' + compareRepo.owner + '/' + compareRepo.name + '</strong> versus <strong>' + baseRepo.owner + '/' + baseRepo.name + '</strong>');
      activityComparisonCard.innerHTML += $('#base-template')[0].innerHTML;
      $(activityComparisonCard).find('.linechart').each(function (index, element) {
        var title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1);
        compareRepo[element.dataset.source]().then(function (compare) {
          var compareData = _GHDataCharts2.default.rollingAverage(_GHDataCharts2.default.convertToPercentages(compare), 180);
          baseRepo[element.dataset.source]().then(function (base) {
            var baseData = _GHDataCharts2.default.rollingAverage(_GHDataCharts2.default.convertToPercentages(base), 180);
            var combinedData = _GHDataCharts2.default.combine(baseData, compareData);
            _GHDataCharts2.default.LineChart(element, combinedData, title, false);
          }, function (error) {
            _GHDataCharts2.default.NoChart(element, title);
          });
        }, function (error) {
          _GHDataCharts2.default.NoChart(element, title);
        });
      });
      this.renderComparisonForm();
    }
  }, {
    key: 'render',
    value: function render(state) {
      var _this3 = this;

      state = state || this.state;
      var $cards = $('#cards');
      $cards.html('');
      this.renderBaseRepo();
      state.comparedTo.forEach(function (repo) {
        _this3.renderComparisonRepo(null, repo);
      });
    }
  }, {
    key: 'startSearch',
    value: function startSearch(url) {
      this.state = this.EMPTY_STATE;
      this.state.repo = this.ghdata.Repo(url);
      this.pushState();
      this.render();
    }
  }, {
    key: 'reset',
    value: function reset() {
      var self = this;
      $('#cards').html(this.STARTING_HTML).find('.reposearch').on('keyup', function (e) {
        if (e.keyCode === 13) {
          self.startSearch(this.value);
        }
      });
    }
  }]);

  return GHDataDashboard;
}();

$(document).ready(function () {

  window.dashboard = new GHDataDashboard();

  $('.reposearch').on('keyup', function (e) {
    if (e.keyCode === 13) {
      dashboard.startSearch(this.value);
    }
  });
});

});

require.alias("process/browser.js", "process");process = require('process');require.register("___globals___", function(exports, require, module) {
  
});})();require('___globals___');


//# sourceMappingURL=app.js.map