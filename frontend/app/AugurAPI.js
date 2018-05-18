var $ = require('jquery')
var _ = require('lodash')

export default class AugurAPI {
  constructor (hostURL, version, autobatch) {
    this._version = version || '/api/unstable'
    this._host = hostURL || 'http://' + window.location.host
    this.__cache = {}
    this.__timeout = null
    this.__pending = {}

    this.autobatch = (typeof autobatch !== 'undefined') ? autobatch : true
    this.openRequests = 0
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

  batch (endpoints) {
    let str = '[{"method": "GET", "path": "' + endpoints.join('"},{"method": "GET", "path": "') + '"}]'
    this.openRequests++
    let url = '' + this._host + this._version + '/batch'

    // Check cached
    if (this.__cache[window.btoa(url + endpoints.join(','))]) {
      if (this.__cache[window.btoa(url + endpoints.join(','))].created_at > Date.now() - 1000 * 60) {
        return new Promise((resolve, reject) => {
          resolve(this.__cache[window.btoa(url + endpoints.join(','))].data)
        })
      }
    }

    return $.ajax(url, {
      type: 'post',
      data: str,
      dataType: 'json',
      contentType: 'application/json'
    }).then((data) => {
      this.openRequests--
      // Save to cache
      this.__cache[window.btoa(url + endpoints.join(','))] = {
        created_at: Date.now(),
        data: data
      }
      return new Promise((resolve, reject) => {
        if (typeof (data) === 'undefined') {
          reject(new Error('data-undefined'))
        } else {
          resolve(data)
        }
      })
    })
  }

  batchMapped (repos, fields) {
    let endpoints = []
    let reverseMap = {}
    let processedData = {}
    repos.forEach((repo) => {
      Array.prototype.push.apply(endpoints, repo.batch(fields, true))
      _.assign(reverseMap, repo.__reverseEndpointMap)
      processedData[repo.toString()] = {}
    })
    return this.batch(endpoints).then((data) => {
      return new Promise((resolve, reject) => {
        if (Array.isArray(data)) {
          data.forEach(response => {
            if (response.status === 200) {
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = JSON.parse(response.response)
            } else {
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = null
            }
          })
          resolve(processedData)
        } else {
          reject(new Error('data-not-array'))
        }
      })
    })
  }

  Repo (owner, repoName) {
    var repo
    if (repoName) {
      repo = {owner: owner, name: repoName}
    } else if (owner) {
      let splitURL = owner.split('/')
      if (splitURL.length < 3) {
        repo = {owner: splitURL[0], name: splitURL[1]}
      } else {
        repo = {owner: splitURL[3], name: splitURL[4]}
      }
    }

    repo.toString = () => { return repo.owner + '/' + repo.name }

    repo.__endpointMap = {}
    repo.__reverseEndpointMap = {}

    var Endpoint = (r, name, endpoint) => {
      this.openRequests++
      var self = this
      var fullEndpoint = this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint
      var url = this._host + fullEndpoint
      r.__endpointMap[name] = fullEndpoint
      r.__reverseEndpointMap[fullEndpoint] = { name: name, owner: repo.toString() }
      r[name] = function (params, callback) {
        if (self.__cache[window.btoa(url)]) {
          if (self.__cache[window.btoa(url)].created_at > Date.now() - 1000 * 60) {
            return new Promise((resolve, reject) => {
              resolve(self.__cache[window.btoa(url)].data)
            })
          }
        }
        if (this.autobatch) {
          return this.__autobatcher(url, params)
        }
        return $.get(url, params).then((data) => {
          this.openRequests--
          self.__cache[window.btoa(url)] = {
            created_at: Date.now(),
            data: data
          }
          if (typeof callback === 'function') {
            callback(data)
          }
          return new Promise((resolve, reject) => {
            if (typeof (data) === 'undefined') {
              reject(new Error('data-undefined'))
            } else {
              resolve(data)
            }
          })
        })
      }
      return r[name]
    }

    var Timeseries = (r, jsName, endpoint) => {
      let func = Endpoint(r, jsName, 'timeseries/' + endpoint)
      func.relativeTo = (baselineRepo, params, callback) => {
        var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name
        return Endpoint(url)()
      }
      return func
    }

    repo.batch = (jsNameArray, noExecute) => {
      var routes = jsNameArray.map((e) => { return repo.__endpointMap[e] })
      if (noExecute) {
        return routes
      }
      return this.batch(routes).then((data) => {
        return new Promise((resolve, reject) => {
          if (Array.isArray(data)) {
            let mapped = {}
            data.forEach(response => {
              if (response.status === 200) {
                mapped[repo.__reverseEndpointMap[response.path].name] = JSON.parse(response.response)
              } else {
                mapped[repo.__reverseEndpointMap[response.path].name] = null
              }
            })
            resolve(mapped)
          } else {
            reject(new Error('data-not-array'))
          }
        })
      })
    }

    Timeseries(repo, 'commits', 'commits')
    Timeseries(repo, 'forks', 'forks')
    Timeseries(repo, 'issues', 'issues')
    Timeseries(repo, 'pulls', 'pulls')
    Timeseries(repo, 'stars', 'stargazers')
    Timeseries(repo, 'tags', 'tags')
    Timeseries(repo, 'downloads', 'downloads')
    Timeseries(repo, 'totalCommitters', 'total_committers')
    Timeseries(repo, 'issueComments', 'issue/comments')
    Timeseries(repo, 'commitComments', 'commits/comments')
    Timeseries(repo, 'pullReqComments', 'pulls/comments')
    Timeseries(repo, 'pullsAcceptanceRate', 'pulls/acceptance_rate')
    Timeseries(repo, 'issuesClosed', 'issues/closed')
    Timeseries(repo, 'issuesResponseTime', 'issues/response_time')
    Timeseries(repo, 'issueActivity', 'issues/activity')
    Timeseries(repo, 'communityEngagement', 'community_engagement')
    Timeseries(repo, 'linesChanged', 'lines_changed')
    Timeseries(repo, 'commits100', 'commits100')
    Timeseries(repo, 'fakes', 'fakes')

    Endpoint(repo, 'maintainerResponseTime', 'pull/maintainer_response_time')
    Endpoint(repo, 'contributors', 'contributors')
    Endpoint(repo, 'contributions', 'contributions')
    Endpoint(repo, 'committerLocations', 'committer_locations')
    Endpoint(repo, 'communityAge', 'community_age')
    Endpoint(repo, 'linkingWebsites', 'linking_websites')
    Endpoint(repo, 'busFactor', 'bus_factor')
    Endpoint(repo, 'dependents', 'dependents')
    Endpoint(repo, 'dependencies', 'dependencies')
    Endpoint(repo, 'dependencyStats', 'dependency_stats')
    Endpoint(repo, 'watchers', 'watchers')

    return repo
  }
}
