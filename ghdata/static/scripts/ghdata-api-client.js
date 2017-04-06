/* SPDX-License-Identifier: MIT */

/**
 * Handles interaction with a GHData server.
 * @constructor
 */
function GHDataAPIClient (apiUrl, owner, repo, apiVersion) {
  this.owner = owner || '';
  this.repo = repo || '';
  this.url = apiUrl;
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
  opts.url = opts.url || (this.url + this.apiversion + '/' + this.owner + '/' + this.repo + '/' + opts.endpoint);
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
    if (params && typeof params === 'object') {
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
